from flask_sqlalchemy import SQLAlchemy
# Media models sathi ha code vapara
class PressRelease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(50), nullable=False)

class ImageGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
import sqlite3
import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__,
template_folder='template')
app.secret_key = "secret"
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT,
    image TEXT
)
''')

conn.commit()
conn.close()
# DATABASE
def init_db():
    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS banners(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS initiatives(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    ''')

    # default admin
    c.execute("SELECT * FROM admin")
    if not c.fetchone():
        c.execute("INSERT INTO admin(username,password) VALUES(?,?)",
                  ("admin", "admin123"))

    conn.commit()
    conn.close()

init_db()

# HOME PAGE
@app.route('/')
def home():
    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()

    c.execute("SELECT * FROM banners")
    banners = c.fetchall()

    c.execute("SELECT * FROM initiatives")
    initiatives = c.fetchall()

    conn.close()

    return render_template('home.html',
                           banners=banners,
                           initiatives=initiatives)

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()

        c.execute("SELECT * FROM admin WHERE username=? AND password=?",
                  (username, password))

        user = c.fetchone()
        conn.close()

        if user:
            session['admin'] = username
            return redirect('/dashboard')

    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect('ngo.db')
    c = conn.cursor()

    c.execute("SELECT * FROM banners")
    banners = c.fetchall()

    c.execute("SELECT * FROM initiatives")
    initiatives = c.fetchall()

    conn.close()

    return render_template('dashboard.html',
                           banners=banners,
                           initiatives=initiatives)

# ADD BANNER
@app.route('/add_banner', methods=['GET', 'POST'])
def add_banner():
    if request.method == 'POST':
        title = request.form['title']

        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()

        c.execute("INSERT INTO banners(title) VALUES(?)", (title,))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('add_banner.html')

# ADD INITIATIVE
@app.route('/add_initiative', methods=['GET', 'POST'])
def add_initiative():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        conn = sqlite3.connect('ngo.db')
        c = conn.cursor()

        c.execute("INSERT INTO initiatives(title,description) VALUES(?,?)",
                  (title, description))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('add_initiative.html')
from flask import render_template, request, redirect, url_for

@app.route('/media')
def media_page():
    press = PressRelease.query.all()
    images = ImageGallery.query.all()
    return render_template('media.html', press=press, images=images)

@app.route('/admin/add-media', methods=['GET', 'POST'])
def add_media():
    if request.method == 'POST':
        # Press Release logic
        if 'title' in request.form:
            new_press = PressRelease(
                title=request.form['title'],
                description=request.form['desc'],
                date=request.form['date']
            )
            db.session.add(new_press)
        
        # Image Gallery logic
        if 'img_url' in request.form:
            new_img = ImageGallery(
                img_url=request.form['img_url'],
                caption=request.form['caption']
            )
            db.session.add(new_img)
            
        db.session.commit()
        return redirect(url_for('media_page'))
    return render_template('admin_media.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')


@app.route('/')
def route():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/projects')
def projects():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM projects")
    data = cursor.fetchall()
    conn.close()

    return render_template('projects.html', projects=data)

@app.route('/admin_projects')
def admin_projects():
    return render_template('admin_projects.html')


@app.route('/add_project', 
methods=['POST'])
def add_project():

    title = request.form['title']
    description = request.form['description']
    status = request.form['status']

    image = request.files['image']

    filename = image.filename

    image.save(os.path.join('static/uploads', filename))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO projects (title, description, status, image) VALUES (?, ?, ?, ?)",
        (title, description, status, filename)
    )
   
 

    conn.commit()
    conn.close()

    return redirect('/projects')
    
if __name__ == '__main__':
    app.run(debug=True)
