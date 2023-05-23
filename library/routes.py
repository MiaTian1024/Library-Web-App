from flask import Flask, render_template, request, redirect, url_for, session

from library import app, queries, connect
import mysql.connector
import re
import bcrypt
from datetime import datetime


dbconn = None
connection = None

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your_secret_key'

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, port=connect.dbport, \
    database=connect.dbname, autocommit=True)
    dbconn=connection.cursor()
    return dbconn

# Define a route which display a homepage for public.
@app.route("/")
def home():
    return render_template("public.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']
        # Check if account exists 
        connection = getCursor()
        connection.execute('select * from member where username = %s', (username,))
        # Fetch one record and return result
        account = connection.fetchone()
        if account is not None:
            password = account[2]
            if bcrypt.checkpw(user_password.encode('utf-8'),password.encode('utf-8')):
            # If account exists in accounts table in out database
            # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                # Redirect to member page   
                return redirect(url_for('member'))
            else:
                # password incorrect
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist or username incorrect
            msg = 'Incorrect username'
    # Show the login form with message (id any)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists
        connection = getCursor()
        connection.execute('select * from member where username = %s', (username,))
        account = connection.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            print(hashed)
            connection.execute('insert into member (username, password, email) values (%s, %s, %s)', (username, hashed, email,))
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty...(no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# Define a route for public to list all books available in the library, include book title,author,category and year of publication.
@app.route("/booklist")
def booklist():
    connection = getCursor()
    sql = """ select bookid, booktitle, author, 
              category, yearofpublication 
              from books;"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("booklist.html", booklist = bookList, session=session)  


# Define a route for public to display details for a book, allow users to see the availability of all copies of a book, whether a copy is on loan and if so, the due date.
@app.route("/bookdetail")
def bookdetail():
    id = request.args.get('id') # Get id of a book and then pass it to SQL to get data for this id.
    connection = getCursor()
    sql="""SELECT b.booktitle, b.author, bc.bookcopyid, bc.format,l.returned, DATE_ADD(l.loandate, INTERVAL 28 DAY) AS Duedate
           FROM books b
           LEFT JOIN bookcopies bc ON b.bookid = bc.bookid
           LEFT JOIN loans l ON bc.bookcopyid = l.bookcopyid
           WHERE b.bookid = %s
           ORDER BY Duedate DESC;"""
    connection.execute(sql, (id,))
    bookDetail = connection.fetchall()
    return render_template("bookdetail.html", bookdetail = bookDetail, session=session)  
    

@app.route('/member')
def member():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the member page
        return render_template('member.html', username=session['username'])
    # User is not loggein redirect to login page
    return redirect(url_for('login'), session=session)


@app.route("/searchbooks", methods=["GET","POST"])
def searchbooks():
    if request.method == "POST":
        book = request.form.get('book')
        connection = getCursor()
        Title = "%" + book + "%"
        Author = "%" + book + "%"   # use LIKE operators with % in SQL to support partial text searches.
        sql = """select bookid, booktitle, author, 
		        category, yearofpublication 
                from books
                WHERE booktitle LIKE %s OR author LIKE %s;""" 
        connection.execute(sql, (Title, Author))
        bookList = connection.fetchall()
        return render_template("booklist.html", booklist = bookList, session=session)
    return render_template("public.html")

@app.route("/loanlist")
def loanlist():
    connection = getCursor()
    sql=""" SELECT b.booktitle, bc.format, l.bookcopyid
            FROM bookcopies bc
            INNER JOIN books b ON bc.bookid = b.bookid
            INNER JOIN loans l ON bc.bookcopyid = l.bookcopyid
            WHERE returned <> 1;"""
    connection.execute(sql)
    loanlist = connection.fetchall()
    return render_template("loanlist.html", loanlist = loanlist, session=session)

@app.route("/loanbook")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    # This SQL query allows physical books only be loaned once at a time (are not already on loan), but eBooks and Audio Books can be loaned multiple times (no need to care about on loan status)
    sql = """ SELECT * FROM bookcopies
            inner join books on books.bookid = bookcopies.bookid
            WHERE format = "eBook" or format = "Audio Book" or bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate = todaydate, session=session, books= bookList)

@app.route("/loan/add", methods=["POST"])
def addloan():
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (memberid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(session['id'], bookid, str(loandate),))
    return redirect("/loanlist")


@app.route("/bookreturn", methods=["GET","POST"])
def bookreturn():
    if request.method == "POST":
        id = request.form.get('loan')
        cur = getCursor()
        # set returned equal to 1.
        sql = "UPDATE loans SET returned=%s WHERE loanid = %s;"
        parameters = (1, id)
        cur.execute(sql,parameters)
        return redirect("/loanlist")
    connection = getCursor()
    sql = """ SELECT l.loanid, bc.bookcopyid, bc.format, b.booktitle
            FROM loans l
            JOIN bookcopies bc ON bc.bookcopyid=l.bookcopyid
            JOIN books b ON bc.bookid=b.bookid
            WHERE returned <> 1 and l.memberid=%s;"""
    connection.execute(sql, (session['id'], ))
    bookLoans = connection.fetchall()
    return render_template("returnbook.html",loans = bookLoans)


@app.route("/book/return")
def returnloan():
    id = request.args.get('id')
    print(id)
    cur = getCursor()
    # set returned equal to 1.
    sql = "UPDATE loans SET returned=%s WHERE loanid = %s;"
    parameters = (1, id)
    cur.execute(sql,parameters)
    return redirect("/loanlist")