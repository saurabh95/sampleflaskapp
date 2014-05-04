import os, sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='saurabh',
    PASSWORD='kathpalia'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True) 

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/add_user', methods = ['GET', 'POST'])
def add_user():
    db = get_db()
    db.execute('insert into users (username, password) values (?, ?)', [request.form['username'], request.form['password']])
    db.commit()
    flash('New User Added Successfully')
    return redirect(url_for('userlist'))
 

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/userlist')
def userlist():
    db = get_db()
    cur = db.execute('select username from users')
    users = cur.fetchall()
    cur = db.execute('select username, password from users')
    temp =  cur.fetchall()
    print temp[0]['username']
    return render_template('userlist.html',users = users)


@app.route('/new_user')
def new_user():
    return render_template('add_user.html')


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select username, password from users')
        temp =  cur.fetchall()
        for users in temp:
            if request.form['username'] == users['username'] and request.form['password'] == users['password']:
                session['logged_in'] = True
                flash('You were logged in')
                return redirect(url_for('show_entries'))
        error = 'Invalid Credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    init_db()
    app.run()
