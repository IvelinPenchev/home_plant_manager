from flask import Flask, request, jsonify
import requests as rq

class MyServer:
    def __init__(self):
        self.globalData = "hello2"


app = Flask(__name__)

my_server = MyServer()


@app.route('/foo', methods=['POST']) 
def foo():
    data = request.json
    print(str(data))
    return "good"

@app.route('/post', methods=['GET'])
def post_message_route_post():
    r = rq.post("http://127.0.0.1:5000/foo", json = {'data': '1', 'type': 'int'})
    print("r is: " + str(r))
    return my_server.globalData
