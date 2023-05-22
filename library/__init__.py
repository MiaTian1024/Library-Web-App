from flask import Flask

app=Flask(__name__)

from library import routes, queries, connect
