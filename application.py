from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask import Flask
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_login import login_user,LoginManager

import random


app =  Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = '' #MySQL username
app.config['MYSQL_PASSWORD'] = '' #MySQl password
app.config['MYSQL_DB'] = ''#MySql database 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)




def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login')
            return redirect(url_for('login'))

    return wrap


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        uemail = request.form['email']
        password_candidate = request.form['password']
        umail=str(uemail)
        
        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("select * from users where email= %s",[umail] )

        if result > 0:
           
            data = cur.fetchone()
            password = data['password']

           

            if password_candidate==password :

                session['logged_in'] = True
                session['email'] = uemail
                return redirect(url_for('contacts'))
            else:
                flash("Check the Username and Password")
                return render_template('login.html')

            cur.close()
        else:
            
            flash('Username not found! Create an account!')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        uemail=request.form['email']
        upass=request.form['password']
        usecret=request.form['secret']
        cur = mysql.connection.cursor()
        result = cur.execute("select * from users where email= %s",[uemail] )
        if result>0:
            flash('Username already exists!')
            return render_template('signup.html')
        else:
            cur.execute("insert into users(email, password, secret)values(%s, %s, %s)", (uemail, upass, usecret))
            mysql.connection.commit()
            flash("account created!")
            return render_template('login.html')
    
    
    return render_template('signup.html')

@app.route('/add_con', methods=['GET', 'POST'])
@login_required
def addcon():
    if request.method == 'POST':

        
        uname=request.form['cname']
        unum=request.form['cnumber']
        umail=request.form['cmail']
        cur = mysql.connection.cursor()
        omail=session['email'] 
        
        cur.execute("insert into contacts(email,name,number,mail)values(%s, %s, %s, %s)", (omail, uname, unum,umail))
        v=mysql.connection.commit()
        flash("contact created!")
        return redirect(url_for('contacts'))
    


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    #logout
    if request.method == 'POST':
        session.clear()
        flash("Successfully Logged Out")
        return redirect(url_for('login'))
    
@app.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    omail=session['email']
    
    cur = mysql.connection.cursor()
    contact = cur.execute("select * from contacts where email= %s",[omail] )
    if contact > 0:  
        contacts=cur.fetchall()
        return render_template('contacts.html',contacts=contacts,uemail=omail)
    return render_template('contacts.html',uemail=omail)

 
 


    
if __name__=="__main__":
    
    app.secret_key='secret123'
    app.run(host='127.0.0.1', debug=True)
