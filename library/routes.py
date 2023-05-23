from flask import Flask, render_template, request, redirect, url_for, session

from library import app, queries, connect
import mysql.connector
import bcrypt


dbconn = None
connection = None

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

# Define a route for public to list all books available in the library, include book title,author,category and year of publication.
@app.route("/booklist")
def booklist():
    connection = getCursor()
    sql = """ select bookid, booktitle, author, 
              category, yearofpublication 
              from books;"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("booklist.html", booklist = bookList)  


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
    return render_template("bookdetail.html", bookdetail = bookDetail)  
    