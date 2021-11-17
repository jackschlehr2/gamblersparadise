from flask import Flask, render_template, request, json, session, redirect, url_for, abort
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import requests
from datetime import date
mysql = MySQL()

app = Flask(__name__)
 
# MySQL configurations
API_KEY='92536bc787b6dca1777c13fbb645e766'
app.config['MYSQL_USER'] = 'jschlehr'
app.config['MYSQL_PASSWORD'] = 'notr3dam3'
app.config['MYSQL_DB'] = 'jschlehr'
app.config['MYSQL_HOST'] = 'localhost'
app.secret_key = "supersecretkey321"
mysql.init_app(app)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for( 'login') )

    return wrap


@app.route("/")
def main():
    users = get_users()
    return render_template('index.html', users=users)


@app.route("/feed")
@login_required
def feed():
    bets = get_bets()
    return render_template( 'feed.html', bets=bets)

@app.route("/features")
def features():
    return render_template('features.html')


@app.route('/sign-up', methods=['POST','GET'])
def signUp():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        if _name and _email and _password:
            if username_exists(_name):
                return render_template('signup.html', message={"status":"message"
                ,"message":"username exists" })
            conn = mysql.connection
            curr = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            curr.execute("INSERT INTO users (user_username, user_password, user_email) VALUES (%s, %s, %s)", 
                                                    ( _name, _hashed_password, _email ) )
            conn.commit()
            session['logged_in'] = True
            session['user_name'] = _name
            curr.execute( "SELECT * FROM users WHERE user_id = @@Identity" )
            data = curr.fetchall()
            session['user_id'] = data[0][0]
            return render_template('account.html',account_name=session['user_name'],  message={"status":"success", "message":"Account Successfully made!"} )
        else:
            return render_template('signup.html', message={"status":"error", "message":"an error was encountered, try again"} )

def username_exists(username):
    conn = mysql.connection
    curr = conn.cursor()
    query= "SELECT * FROM users WHERE user_username = \"{user}\"".format(user=username)
    curr.execute(query)
    data = curr.fetchall()
    if len(data) > 0:
        return True
    return False


@app.route( "/profile/<username>", methods=['POST','GET'])
@login_required
def view_profile(username):
    conn = mysql.connection
    curr = conn.cursor()
    query= "SELECT * FROM users WHERE user_username = \"{user}\"".format(user=username)
    curr.execute(query)
    data = curr.fetchall()
    num_followers=0
    num_following=0

    return render_template('profile.html', account_name=username, \
            num_followers=num_followers, num_following=num_following)


@app.route( "/add-friend/<username>", methods=['POST','GET'])
@login_required
def add_friend(username):
    conn = mysql.connection
    curr = conn.cursor()
    query = "select user_id from users where user_username=\"{username}\"".format(username=username)
    curr.execute( query )
    data = curr.fetchall()
    try:
        friend_id = int(data[0][0])
    except Exception as e:
        print(e)
        return 
    query = "INSERT INTO friends values ( {user_id}, {friend_id} )".format( user_id=int(session['user_id']), friend_id=int(friend_id) )
    curr.execute( query )
    conn.commit()
    print(query)

    url = "/profile/{}".format(username)
    return view_profile(username)








@app.route('/login', methods=['POST', 'GET'] )
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        _username = request.form['inputName']
        _password = request.form['inputPassword']
        if not (_username and _password):
            return render_template( 'index.html', message={"status":"error", "message":"error occured"})
        if _username and _password:
            conn = mysql.connection
            curr = conn.cursor()
            curr.execute("SELECT * FROM users WHERE user_username = (%s) or user_email = (%s)", 
                                                    ( _username, _username ) )
            
            data = curr.fetchall()
            if not data:
                return json.dumps( {'fail':'fail'})
            # TODO: case where query returns more than one result
            # refactor to make more robust
            query_password = data[0][2]
            # TODO fix so that the returns are better
            if check_password_hash(query_password, _password):
                session['logged_in'] = True
                session['user_id'] = data[0][0]
                session['user_name'] = _username
                return render_template('account.html', message={"status":"success", "message":"Logged In!"})
            return render_template('login.html', message={"status":"error", "message":"Incorrect password"})




@app.route( '/account', methods=['GET'])
@login_required
def account():
    return render_template('account.html', account_name=session['user_name'])

@app.route( '/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method=='GET':
        return render_template('change_password.html')
    elif request.method=='POST':
        old_password_from_form = request.form['oldPassword']
        new_password1 = request.form['newPassword1']
        new_password2 = request.form['newPassword2']
        if new_password1 != new_password2: 
            return render_template('change_password.html', message="Passwords Not Same")

        conn = mysql.connection
        curr = conn.cursor()
        _user_id = session['user_id']
        query = "SELECT user_password FROM users WHERE user_id = {user_id}".format(user_id=_user_id )
        curr.execute( query )
        data = curr.fetchall()
        current_password = data[0][0]
        if check_password_hash(current_password, old_password_from_form ):
            new_password_hash = generate_password_hash(new_password2)
            query = "UPDATE users SET user_password = \"{new_password_hash}\" where user_id = {user_id}".format(new_password_hash=new_password_hash, user_id=_user_id )
            conn = mysql.connection
            curr = conn.cursor()
            curr.execute( query )
            conn.commit()
            return render_template('account.html', message="Password Updated")
        else:
            return render_template('change_password.html', message="Password Not Correct")
    else:
        return {'status':'error'}


@app.route( '/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method=='GET':
        return render_template('delete_account.html')
    elif request.method=='POST':
        new_password1 = request.form['newPassword1']
        new_password2 = request.form['newPassword2']
        if new_password1 != new_password2: 
            return render_template('delete_account.html', message="Passwords Not Same")

        conn = mysql.connection
        curr = conn.cursor()
        _user_id = session['user_id']
        query = "SELECT user_password FROM users WHERE user_id = {user_id}".format(user_id=_user_id )
        curr.execute( query )
        data = curr.fetchall()
        current_password = data[0][0]
        if check_password_hash(current_password, new_password2 ):
            delete_query = "DELETE from users where user_id = {user_id}".format(user_id=_user_id )
            conn = mysql.connection
            curr = conn.cursor()
            curr.execute( delete_query )
            conn.commit()
            session['logged_in'] = False
            return redirect( "/" )
        else:
            return render_template('delete_account.html', message="Password Not Correct")
    else:
        return {'status':'error'}


def get_users():
    conn = mysql.connection
    curr = conn.cursor()
    curr.execute("SELECT user_username FROM users limit 10" )
    data = curr.fetchall()
    print(data)
    return data



def get_bets():
    conn = mysql.connection
    curr = conn.cursor()
    curr.execute("SELECT * FROM bets" )
    data = curr.fetchall()
    print(data)
    return data



@app.route( '/new-bet', methods=['GET', 'POST'])
@login_required
def bet():
    # TODO fill in information about the bet
    if request.method=='GET':
        return render_template( 'new-bet.html')
    elif request.method=='POST':
        _bet_amount = int( request.form['betAmount'] )
        _bet_league = request.form['league']
        _game_id = request.form['game']
        _OU      = request.form['OU']
        if _OU == 'over':
            _OU = 1
        else:
            _OU = 0
        _type = "OU"
        print(type(_bet_amount),_bet_league,_game_id,_OU)
        if _bet_amount and _bet_league and _game_id:
            conn = mysql.connection
            curr = conn.cursor()
            query = "INSERT INTO bets (amount, submitted_date, user_id, type, game_id, ou, league) \
                          VALUES ({_bet_amount}, \"{date}\", {user_id}, \"{_type}\", \"{_game_id}\", \"{_OU}\", \"{_bet_league}\")".format( _bet_amount=_bet_amount,  date=str(date.today()), user_id=int(session['user_id']),_type=_type, _game_id=_game_id,_OU=int(_OU), _bet_league=_bet_league )
            print(query)
            curr.execute( query )
            conn.commit()
            return {'status':'success'}
        else:
            return {'status':'fail'}


def get_odds(league):
    print('Making Request')
    try:
        URL = 'https://api.the-odds-api.com/v4/sports/{league}/odds'.format(league=league)
        print( URL )
        response = requests.get( URL, params = 
            { 'api_key':API_KEY, 
            'markets':'totals',
            'regions':'us' } )
        if response.status_code != 200:
            return {'error': 'API FAILED'}
        return response.json()
    except Exception as e:
        return False

def insert_games( league, games, bet_type ):
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
        conn = mysql.connection
        curr = conn.cursor()
        query = "INSERT INTO {league} (id, home_team, away_team, date, OU) VALUES (\"{id}\",\"{home_team}\",\"{away_team}\", \"{date}\", {OU} ) ON DUPLICATE KEY UPDATE OU={OU}, date=\"{date}\"".format( id=id, league=league, home_team=home_team, away_team=away_team, date=date, OU=OU )
        curr.execute(query) 
        conn.commit()

        print("inserted")


@app.route( '/get-games', methods=['GET'] )
def get_games():
    league = request.args.get("league")
    games = get_odds(league)
    insert_games(league, games, 'OU' )
    conn = mysql.connection
    curr = conn.cursor()
    query = "SELECT id, home_team, away_team, DATE_FORMAT(date,'%y-%m-%d'), OU FROM {league} where date > CURDATE() order by date desc limit 10".format(league=request.args['league'])  
    curr.execute(query)
    data = curr.fetchall()
    if not data:
        abort(500)
    return {'success':data}
   


@app.route( '/logout', methods=['GET'])
@login_required
def logout():
    session.clear()
    return redirect( url_for( "main", message={"status":"nothing", "message":"Logged Out"} ) )



if __name__== "__main__":
    app.run(port=5004, host="0.0.0.0")

# 0 7 * * * 7:00am everyday

