import sqlite3
DATABASE = 'home_town.db'
def find_user(email, password):
    conn = sqlite3.Connection(DATABASE)
    c = conn.cursor()
    c.execute("SELECT first_name, last_name, email, password FROM user WHERE email = ? AND password = ?", (email, password))
    user = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return user

email = "bbebawe93@gmail.com"
password = "admin"
user = find_user(email, password)
print(user[0][0])
