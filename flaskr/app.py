from flask import Flask, render_template, request, json, session, redirect, url_for
# import MySQLdb
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


mysql = MySQL()

app = Flask(__name__)
 
# MySQL configurations
 
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
    return render_template('index.html')


@app.route('/sign-up-page')
def signUpPage():
    return render_template('signup.html')

@app.route('/sign-up', methods=['POST'])
def signUp():
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    if _name and _email and _password:
        conn = mysql.connection
        curr = conn.cursor()
        _hashed_password = generate_password_hash(_password)
        curr.execute("INSERT INTO users (user_username, user_password, user_email) VALUES (%s, %s, %s)", 
                                                ( _name, _hashed_password, _email ) )
        conn.commit()
        session['logged_in'] = True
        return json.dumps({'message':'usermade'})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        _username = request.form['inputName']
        _password = request.form['inputPassword']
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
            query_password = data[0][3]

            # TODO fix so that the returns are better
            if check_password_hash(query_password, _password):
                session['logged_in'] = True
                return redirect( url_for( 'account') )
            return json.dumps( {'fail': "fail"})


@app.route( '/account', methods=['GET'])
@login_required
def account():
    return render_template('account.html')

@app.route( '/logout', methods=['GET'])
@login_required
def logout():
    session.clear()
    return redirect( "/" )

if __name__== "__main__":
    app.run(port=5001)

