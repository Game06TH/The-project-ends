from flask import Flask, render_template, request, redirect, session, url_for, flash
import os, uuid, smtplib
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="motorbike_shop"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    cursor.execute("SELECT * FROM bikes WHERE approved=1")
    bikes = cursor.fetchall()
    return render_template("index.html", bikes=bikes)

@app.route('/add_bike', methods=['GET', 'POST'])
def add_bike():
    if session.get('role') != 'admin':
        return redirect('/')
    if request.method == 'POST':
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']
        mileage = request.form['mileage']
        files = request.files.getlist('images')
        cursor.execute("INSERT INTO bikes(model, year, price, mileage, approved) VALUES(%s, %s, %s, %s, 0)", (model, year, price, mileage))
        db.commit()
        bike_id = cursor.lastrowid
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                cursor.execute("INSERT INTO bike_images(bike_id, image_path) VALUES(%s, %s)", (bike_id, filename))
        db.commit()
        flash('เพิ่มรถเรียบร้อย รออนุมัติจากแอดมิน')
        return redirect('/')
    return render_template("add_bike.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect('/')
        flash("เข้าสู่ระบบไม่สำเร็จ")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/report_problem', methods=['GET', 'POST'])
def report_problem():
    if request.method == 'POST':
        msg = request.form['message']
        cursor.execute("INSERT INTO reports(user_id, message) VALUES(%s, %s)", (session.get('user_id'), msg))
        db.commit()
        flash("ส่งรายงานเรียบร้อย")
        return redirect('/')
    return render_template("report_problem.html")

if __name__ == "__main__":
    app.run(debug=True)