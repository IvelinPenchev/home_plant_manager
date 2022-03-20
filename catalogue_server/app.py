from flask import Flask, request, jsonify
import requests as rq

class MyServer:
    def __init__(self):
        self.globalData = "Hello World!"


app = Flask(__name__)

my_server = MyServer()


# @app.route('/foo', methods=['POST']) 
# def foo():
#     data = request.json
#     print(str(data))
#     return "good"

# @app.route('/post', methods=['GET'])
# def post_message_route_post():
#     r = rq.post("http://127.0.0.1:5000/foo", json = {'data': '1', 'type': 'int'})
#     print("r is: " + str(r))
#     return my_server.globalData
# @app.route('/test', methods=['PUT'])
# def post_message_username_pass():
#     # json is: {'username': 'xxxx', 'password': 'xxxx'}
#     data = request.json
#     output = "username is: " + str(data["username"]) + ", and password is: " + str(data["password"])
#     return output

# used for testing connection with the server
@app.route('/checkconnection', methods=['GET'])
def checkconnection():
    return "True"

@app.route('/list_plants', methods=['GET'])
def list_plants():
    return "True"
