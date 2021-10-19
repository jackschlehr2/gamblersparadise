from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/sign-up')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__== "__main__":
    app.run()

