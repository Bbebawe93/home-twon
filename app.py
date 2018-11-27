from flask import Flask, render_template, url_for, flash, request, redirect, session
import sqlite3
import os

# create instance of flask app
app = Flask(__name__)

# set app secret key. used by flash, cookie and sessions
app.secret_key = os.urandom(24)


# database name
DATABASE = 'home_town.db'
# database connection, check same thread is set to false, enables reuse of connection and cursor
db = sqlite3.Connection(DATABASE, check_same_thread=False)
# database cursor
cursor = db.cursor()

# page titles list
page_title = ["Home", "Sights", "Feedback", "Admin"]
# logged in variable used to display diffrent content if the user is logged
LOGGED_IN = False
LOGGED_OUT = True

def clear_session():
    session.pop('user_id', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    session.pop('user_email', None)


def valid_name(name):
    name = name.strip()
    if name.isalpha() and (len(name) >= 2):
        return True
    else:
        return False


def valid_comment(comment):
    if len(comment.strip()) > 2:
        return True
    else:
        return False


def add_guest(first_name, last_name, email, guest_comment):  # adds guest to guest book
    cursor.execute("INSERT INTO guest_book(first_name, last_name, email, guest_comment) VALUES (?, ?, ?, ?)",
                   (first_name, last_name, email, guest_comment))
    db.commit()


def fetch_guest_comment():  # fetch guest comments from db
    cursor.execute(
        "SELECT first_name, last_name, guest_comment FROM guest_book")
    guest_comments = cursor.fetchall()
    return guest_comments


# adds registered user to the database
def register_user(first_name, last_name, age,  email, password):
    cursor.execute("INSERT INTO user(first_name, last_name, age,  email, password) VALUES (?, ?, ?, ?, ?)",
                   (first_name, last_name, age, email, password))
    db.commit()


def fetch_user():
    cursor.execute("SELECT email, password FROM user")
    users = cursor.fetchall()
    return users


def find_user(email, password):  # find user in the database table

    cursor.execute(
        "SELECT user_id, first_name, last_name, age, email, password FROM user WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchall()
    return user


def fetch_user_feedback():  # fetch user feedback from database
    cursor.execute(
        "SELECT user_feedback.user_id, first_name, last_name, feedback FROM user_feedback INNER JOIN user WHERE user_feedback.user_id = user.user_id ")
    users_feedback = cursor.fetchall()
    return users_feedback


def add_user_feedback(user_id, feedback):  # adds user feedback to the database
    cursor.execute("INSERT INTO user_feedback (user_id, feedback) VALUES (?, ?)",
                   (user_id, feedback))
    db.commit()


@app.route('/')
@app.route('/index')
def index():
    guest_comments = fetch_guest_comment()
    return render_template('index.html', page_title=page_title[0], guest_comments=guest_comments, LOGGED_IN=LOGGED_IN, LOGGED_OUT=LOGGED_OUT)


@app.route('/sights')
def sights():
    return render_template('sights.html')


@app.route('/feedback')
def feedback():
    users_feedback = fetch_user_feedback()
    return render_template('feedback.html', users_feedback=users_feedback, LOGGED_IN=LOGGED_IN, LOGGED_OUT=LOGGED_OUT)


@app.route('/account', methods=['GET', 'POST'])
def account():
    if LOGGED_IN == True:
        users_feedback = fetch_user_feedback()
        return render_template('user.html', page_title=(session['first_name'] + " " + session['last_name']), users_feedback=users_feedback)
    else:
        return render_template('account.html')


@app.route('/guest-book', methods=['GET', 'POST'])
def guest_book():
    error = []
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        guest_comment = request.form['guest-comment']
        if valid_name(first_name):
            first_name = first_name.strip()
        else:
            error.append("Invalid first name")
        if valid_name(last_name):
            last_name = last_name.strip()
        else:
            error.append("Invalid last name")
        if not valid_comment(guest_comment):
            error.append("Ivalid comment")
        if error:
            guest_comments = fetch_guest_comment()
            return render_template("index.html", error=error, guest_comments=guest_comments)
        else:
            add_guest(first_name, last_name, email, guest_comment)
            flash(f"Guest Comment added Successfully")
            flash(f"Thank you {first_name}")
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/user-feedback',  methods=['GET', 'POST'])
def user_feedback():
    if request.method == 'POST':
        user_id = session["user_id"]
        feedback = request.form['user-feedback']
        add_user_feedback(user_id, feedback)
        flash("Feedback submitted Successfully, Thank you")
        return redirect(url_for('feedback'))
    else:
        return redirect(url_for('feedback'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = []
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']
        if valid_name(first_name):
            first_name = first_name.strip()
        else:
            error.append("invalid first name")
        if valid_name(last_name):
            last_name = last_name.strip()
        else:
            error.append("invalid last name")
        try:
            age = int(age.strip())
        except ValueError:
            error.append("invalid age")
        if len(password.strip()) >= 5:
            password = password.strip()
        else:
            error.append("invalid password")
        if error:
            return render_template('account.html', error=error)
        else:
            register_user(first_name, last_name, age, email, password)
            flash(f"User added, thank you {first_name} {last_name}")
            flash("Please Login to your Account")
            return redirect(url_for('index'))
    else:
        return redirect(url_for('account'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_error = []
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = find_user(email, password)
            session['user_id'] = user[0][0]
            session['first_name'] = user[0][1]
            session['last_name'] = user[0][2]
            session['age'] = user[0][3]
            session['user_email'] = user[0][4]
            flash(f"logged in {session['first_name']} {session['last_name']}")
            global LOGGED_IN
            global LOGGED_OUT
            LOGGED_IN = True
            LOGGED_OUT = False
            return redirect(url_for('index'))
        except Exception:
            login_error.append("invalid user name or password")
            return render_template('account.html', login_error=login_error)
    else:
        return redirect(url_for('account'))


@app.route('/logout')
def logout():
    clear_session()
    global LOGGED_IN
    global LOGGED_OUT
    LOGGED_IN = False
    LOGGED_OUT = True
    flash("Logged out Successfully ")
    return redirect(url_for('index'))


# 404 error handler
@app.route('/<url>')
def get_page(url):
    try:
        return render_template('{}.html'.format(url))
    except:
        return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)
