import requests
import mysql.connector
API_KEY='92536bc787b6dca1777c13fbb645e766'


# app.config['MYSQL_USER'] = 'jschlehr'
# app.config['MYSQL_PASSWORD'] = 'notr3dam3'
# app.config['MYSQL_DB'] = 'jschlehr'
# app.config['MYSQL_HOST'] = 'localhost'
# app.secret_key = "supersecretkey321"

# mysql.init_app(app)



def get_odds(league):
    print('Making Request to ', end="")
    try:
        URL = 'https://api.the-odds-api.com/v4/sports/{league}/odds'.format(league=league)
        print( URL )
        response = requests.get( URL, params = 
            { 'api_key':API_KEY, 
            'markets':'totals',
            'regions':'us' } )
        if response.status_code != 200:
            print("Error making API call")
            return {'error': 'API FAILED'}
        return response.json()
    except Exception as e:
        print(e)
        return None

def insert_games( mydb, league, games, bet_type ):
    print("Traversing games")
    for game in games:
        id = game['id']
        home_team = game['home_team']
        away_team = game['away_team']
        date = game['commence_time']
        hours = date[:10]
        minutes = date[12:-1]
        date = hours 
        OU = None
        for bookmakers in game['bookmakers']:
            if bookmakers['key'] == 'draftkings':
                if bet_type == 'OU':
                    OU = bookmakers['markets'][0]['outcomes'][0]['point']
        
        if not ( home_team and away_team and date and hours and minutes and date and OU ):
            print("Error can't find metrics ")
            return 
        else:
            print("Connected to database")
        curr = mydb.cursor()
        query = "INSERT INTO {league} (id, home_team, away_team, date, OU) VALUES (\"{id}\",\"{home_team}\",\"{away_team}\", \"{date}\", {OU} ) ON DUPLICATE KEY UPDATE OU={OU}, date=\"{date}\"".format( id=id, league=league, home_team=home_team, away_team=away_team, date=date, OU=OU )
        curr.execute(query) 
        mydb.commit()

        print("inserted")

def main():
    leagues = ["americanfootball_ncaaf", "americanfootball_nfl", "basketball_nba" ]
    mydb = mysql.connector.connect(
        host="localhost",
        user="jschlehr",
        password="notr3dam3",
        database="jschlehr"
    )

    for league in leagues:
        games = get_odds(league)
        insert_games(mydb, league, games, 'OU' )


if __name__ == "__main__":
    main()

