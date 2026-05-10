import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='template')
app.secret_key = "ngo_secret_key_123"

# 1. DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. MODELS
class PressRelease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)

class ImageGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))

# 3. DATABASE INIT
def init_db():
    with app.app_context():
        db.create_all()
    
    # NGO Main DB
    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS admin(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS banners(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS initiatives(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT)')
    c.execute("SELECT * FROM admin WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO admin(username,password) VALUES(?,?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

    # Projects DB
    conn2 = sqlite3.connect('database.db')
    c2 = conn2.cursor()
    c2.execute('CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, status TEXT, image TEXT)')
    conn2.commit()
    conn2.close()

init_db()

# 4. PUBLIC ROUTES
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

@app.route('/media')
def media_page():
    press = PressRelease.query.all()
    images = ImageGallery.query.all()
    return render_template('media.html', press=press, images=images)

@app.route('/projects')
def projects():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    data = cursor.fetchall()
    conn.close()
    return render_template('projects.html', projects=data)

# 5. ADMIN & DASHBOARD ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['admin'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html')

# ADD CONTENT ROUTES (Check spelling with your dashboard.html)
@app.route('/add_banner', methods=['GET', 'POST'])
def add_banner():
    if 'admin' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()
        c.execute("INSERT INTO banners(title) VALUES(?)", (title,))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_banner.html')

@app.route('/add_initiative', methods=['GET', 'POST'])
def add_initiative():
    if 'admin' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()
        c.execute("INSERT INTO initiatives(title,description) VALUES(?,?)", (title, description))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_initiative.html')

@app.route('/admin/add-media', methods=['GET', 'POST'])
def add_media():
    if 'admin' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        if 'title' in request.form:
            new_press = PressRelease(title=request.form['title'], description=request.form['desc'], date=request.form['date'])
            db.session.add(new_press)
        if 'img_url' in request.form:
            new_img = ImageGallery(img_url=request.form['img_url'], caption=request.form['caption'])
            db.session.add(new_img)
        db.session.commit()
        return redirect(url_for('media_page'))
    return render_template('admin_media.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
