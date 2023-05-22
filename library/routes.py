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

@app.route("/")
def home():
    return render_template("login.html")
    