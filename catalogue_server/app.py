from flask import Flask, request, jsonify
import requests as rq
import json

class MyServer:
    def __init__(self):
        self.globalData = "Hello World!"
        # self.__configs = json.load(open("config.json"))

    def get_configs(self):
        return json.load(open("config.json"))

    

app = Flask(__name__)
my_server = MyServer()

@app.route('/get_configs', methods=['GET'])
def get_configs():
    return my_server.get_configs()

# used for testing connection with the server
@app.route('/checkconnection', methods=['GET'])
def checkconnection():
    return "True"



