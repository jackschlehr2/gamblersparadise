from serpapi import GoogleSearch
import mysql.connector
import time
import pprint
API_KEYS=['9183c69b2a4151fe87b0ae7044eaaa5a854781f3aa37ca82658e1030d918cd04','16f9bb419af6e71c7f51853c6ac573bb947a733fe8184abd2eadab1a101e5224','94136cb72617f3b44dc927412eca47df0de942214e1c96816aa8c19910b9c7da']
def main():
    leagues=['americanfootball_nfl','basketball_nba']
    mydb = mysql.connector.connect(
        host="localhost",
        user="jschlehr",
        password="notr3dam3",
        database="jschlehr"
    )
    mydb.cursor()
    curr_key = 0
    curr = mydb.cursor()
    for league in leagues:
        print( f'starting leage {league}...' )
        query = f'select id, home_team, away_team, DATE(date), ou from {league} where date < CURDATE()'
        curr.execute( query ) 
        games = curr.fetchall()
        for game in games: 
            time.sleep(1)
            teams_and_date = f"{game[1]} {game[2]} {str(game[3])}"
            print( f'making request for game: {teams_and_date}...')
            try: 
                final_score = make_request( teams_and_date,curr_key )
            except ValueError:
                print( f"ERROR value error for {teams_and_date}")
                curr_key += 1
                if curr_key >= len(API_KEYS):
                    curr_key = 0
                continue
            except Exception as e:
                print( f"ERROR {e} with {teams_and_date} ")
                curr_key += 1
                if curr_key >= len(API_KEYS):
                    curr_key = 0
                continue

            print("updating if game hit")
            if final_score < int(game[4]): #under hit
                query=f"update bets set win=1 where game_id=\"{game[0]}\" and ou=0" #ou=0 means bet under
                curr.execute( query ) 
                mydb.commit()
                query=f"update bets set win=0 where game_id=\"{game[0]}\" and ou=1" #ou=1 means bet over
                curr.execute( query ) 
                mydb.commit()
                print( f"updated {game[0]} ")
            else:
                query=f"update bets set win=1 where game_id=\"{game[0]}\" and ou=1" #ou=0 means bet under
                curr.execute( query ) 
                mydb.commit()
                query=f"update bets set win=0 where game_id=\"{game[0]}\" and ou=0" #ou=1 means bet over
                curr.execute( query ) 
                mydb.commit()
                print( f"updated {game[0]} " )

        

def make_request( teams_and_date, curr_key ):
    params= {'api_key': API_KEYS[curr_key],
            'location':  'United States',
            'q': teams_and_date }
    response = GoogleSearch(params)
    results = response.get_dict()
    teams = results['sports_results']['game_spotlight']['teams']
    total = 0
    for team in teams:
        total += int( team['score']['total'] )
    return total


if __name__ == '__main__':
    main()