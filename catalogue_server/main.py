class MyServer:
    def __init__(self):
        self.globalData = "hello"

from flask import Flask
app = Flask(__name__)

my_server = MyServer()

@app.route("/getSomeData")
def getSomeData():
    return my_server.globalData
