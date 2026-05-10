import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder='template')
app.secret_key = "secret"

# 1. DATABASE CONFIGURATION
# SQLAlchemy sathi (Media Page)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. SQLALCHEMY MODELS (Media Section)
class PressRelease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)

class ImageGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))

# 3. DATABASE INITIALIZATION
def init_db():
    # SQLAlchemy tables create karane
    with app.app_context():
        db.create_all()

    # Tumche junya sqlite3 tables (ngo.db)
    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS admin(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS banners(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS initiatives(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT)')
    
    c.execute("SELECT * FROM admin")
    if not c.fetchone():
        c.execute("INSERT INTO admin(username,password) VALUES(?,?)", ("admin", "admin123"))
    
    conn.commit()
    conn.close()

    # Project database (database.db)
    conn2 = sqlite3.connect('database.db')
    c2 = conn2.cursor()
    c2.execute('CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, status TEXT, image TEXT)')
    conn2.commit()
    conn2.close()

init_db()

# 4. ROUTES
@app.route('/')
def home():
    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM banners")
    banners = c.fetchall()
    c.execute("SELECT * FROM initiatives")
    initiatives = c.fetchall()
    conn.close()
    return render_template('home.html', banners=banners, initiatives=initiatives)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['admin'] = username
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session: return redirect('/login')
    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM banners")
    banners = c.fetchall()
    c.execute("SELECT * FROM initiatives")
    initiatives = c.fetchall()
    conn.close()
    return render_template('dashboard.html', banners=banners, initiatives=initiatives)

# MEDIA ROUTES (Assignment 5)
@app.route('/media')
def media_page():
    press = PressRelease.query.all()
    images = ImageGallery.query.all()
    return render_template('media.html', press=press, images=images)

@app.route('/admin/add-media', methods=['GET', 'POST'])
def add_media():
    if request.method == 'POST':
        if 'title' in request.form: # Press release form logic
            new_press = PressRelease(
                title=request.form['title'],
                description=request.form['desc'],
                date=request.form['date']
            )
            db.session.add(new_press)
        
        if 'img_url' in request.form: # Gallery form logic
            new_img = ImageGallery(
                img_url=request.form['img_url'],
                caption=request.form['caption']
            )
            db.session.add(new_img)
            
        db.session.commit()
        return redirect(url_for('media_page'))
    return render_template('admin_media.html')

# OTHER ROUTES
@app.route('/about')
def about(): return render_template('about.html')

@app.route('/projects')
def projects():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    data = cursor.fetchall()
    conn.close()
    return render_template('projects.html', projects=data)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
