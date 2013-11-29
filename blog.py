#all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

#confiruration
DATABASE = '/tmp/blog.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create our little application
app = Flask(__name__)
app.config.from_object(__name__) 

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

@app.route('/')
def show_entries():
	cur = g.db.execute('select id, title from entries order by id desc')
	entries = [dict(id=row[0], title=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries= entries)

@app.route('/admin')
def admin():
	cur = g.db.execute('select id, title from entries order by id desc')
	entries = [dict(id=row[0], title=row[1]) for row in cur.fetchall()]
	return render_template('admin.html', entries= entries)

@app.route('/add', methods=['GET','POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		g.db.execute('insert into entries (title, text) values (?, ?)',
				[request.form['title'], request.form['text']])
		g.db.commit()
		flash('New entry was successfully posted')
		return redirect(url_for('show_entries'))
	else:
		return render_template('add_entry.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_entry(id):
	if not session.get('logged_in'):
		abort(401)
	if request.method == 'POST':
		g.db.execute('update entries set title=?, text=? where id=?', [request.form['title'], request.form['text'],request.form['id']])
		g.db.commit()
		flash('The entry was successfully updated')
		return redirect(url_for('admin'))
	else:
		cur = g.db.execute('select * from entries where id=?', [id])
		entry = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
		return render_template('edit_entry.html', entry=entry)

@app.route('/delete/<int:id>')
def delete_entry(id):
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('delete from entries where id=?', [id])
	g.db.commit()
	flash('The entry was successfully deleted')
	return redirect(url_for('admin'))

@app.route('/entry/<int:id>')
def entry(id):
	cur = g.db.execute('select * from entries where id=?', [id])
	entry = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
	return render_template('entry.html', entry=entry)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)
	
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))
if __name__ == '__main__':
	app.run()
