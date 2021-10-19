from flask import Flask, render_template, request, json
# import MySQLdb
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

mysql = MySQL()

app = Flask(__name__)
 
# MySQL configurations
 
app.config['MYSQL_DATABASE_USER'] = 'jschlehr'
app.config['MYSQL_PASSWORD'] = 'notr3dam3'
app.config['MYSQL_DATABASE_DB'] = 'jschlehr'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

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
    print(_name, _email, _password )
    if _name and _email and _password:
        curr = mysql.connection.cursor()
        _hashed_password = generate_password_hash(_password)
        # curr.execute("INSERT INTO users ")
        return json.dumps({'message':'usermade'})

    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route('/login')
def login():
    return render_template('login.html')


if __name__== "__main__":
    app.run()

