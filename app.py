from flask import Flask, render_template, url_for, flash, request, redirect, session
import sqlite3, os


app = Flask(__name__)
# set app secret key for flash, cookie and sessions 
app.secret_key = os.urandom(24)
# database name
DATABASE = 'home_town.db'
# page titles list
page_title = ["Home", "Sights", "Feedback", "Admin"]

LOGGED_IN = False
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
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO guest_book(first_name, last_name, email, guest_comment) VALUES (?, ?, ?, ?)",
              (first_name, last_name, email, guest_comment))
    conn.commit()
    c.close()
    conn.close()

def fetch_guest_comment(): # fetch guest comments from db
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("SELECT first_name, last_name, guest_comment FROM guest_book")
    guest_comments = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return guest_comments

def register_user(first_name, last_name, email, password):
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO user(first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
              (first_name, last_name, email, password))
    conn.commit()
    c.close()
    conn.close()

def fetch_user():
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("SELECT email, password FROM user")
    users = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return users

def find_user(email, password):
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("SELECT user_id, first_name, last_name, email, password FROM user WHERE email = ? AND password = ?", (email, password))
    user = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return user

def fetch_user_feedback():
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("SELECT user_feedback.user_id, first_name, last_name, feedback FROM user_feedback INNER JOIN user WHERE user_feedback.user_id = user.user_id ")
    users_feedback = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return users_feedback

def add_user_feedback(user_id, feedback):
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO user_feedback (user_id, feedback) VALUES (?, ?)",
              (user_id, feedback))
    conn.commit()
    c.close()
    conn.close()

@app.route('/')
@app.route('/index')
def index():
    guest_comments = fetch_guest_comment()
    return render_template('index.html', page_title=page_title[0], guest_comments=guest_comments)


@app.route('/sights')
def sights():
    return render_template('sights.html')


@app.route('/feedback')
def feedback():
    users_feedback = fetch_user_feedback()
    return render_template('feedback.html', users_feedback=users_feedback)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # if not session:
    #     return render_template('admin.html', page_title=page_title[3])
    # elif session['user_id'] != None:
    #     users_feedback = fetch_user_feedback()
    #     return render_template('user.html', page_title=(session['first_name'] + " " + session['last_name']), users_feedback=users_feedback)
    if LOGGED_IN == True:
        users_feedback = fetch_user_feedback()
        return render_template('user.html', page_title=(session['first_name'] + " " + session['last_name']), users_feedback=users_feedback)
    else:
        return render_template('admin.html') 
       


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
            return redirect( url_for('index') ) 
    else: 
        return redirect( url_for('index') ) 


@app.route('/user-feedback',  methods=['GET', 'POST'])     
def user_feedback():
    if request.method == 'POST':
        user_id = session["user_id"]
        feedback = request.form['user-feedback']
        add_user_feedback(user_id, feedback)
        flash("Feedback submitted Successfully, Thank you")
        return redirect( url_for('feedback') )
    else:
        return redirect( url_for('feedback') )



@app.route('/register', methods=['GET', 'POST'])
def register(): 
    error = []
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        password = request.form['password']
        register_user(first_name, last_name, email, password)
        flash(f"User added, thank you {first_name}")
        return redirect( url_for('admin'))
    else:
        return redirect( url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_error = []
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'] 
        user = find_user(email, password)
        if user:
            session['user_id'] = user[0][0]
            session['first_name'] = user[0][1]
            session['last_name'] = user[0][2]
            session['user_email'] = user[0][3]
            flash(f"logged in {session['first_name']} {session['last_name']}")
            global LOGGED_IN 
            LOGGED_IN = True
            return redirect( url_for('index'))
        else:
            login_error.append("invalid user name or password")
            return render_template('admin.html', login_error=login_error)
    else:
        return redirect( url_for('admin'))

@app.route('/logout')
def logout():
    clear_session()
    global LOGGED_IN 
    LOGGED_IN = False
    flash("Logged out Successfully ")
    return redirect( url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)
