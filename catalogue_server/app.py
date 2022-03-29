from flask import Flask, request, jsonify
import requests
import json

class MyServer:
    def __init__(self):
        self.globalData = "Hello World!"
        # self.__configs = json.load(open("config.json"))

    def get_configs(self):
        return json.load(open("config.json"))    

app = Flask(__name__)
my_server = MyServer()

@app.route('/', methods=['GET'])
def index():
    return "Welcome to the home plant manager server"

@app.route('/getconfig', methods=['GET'])
def get_configs():
    return my_server.get_configs()

# used for testing connection with the server
@app.route('/checkconnection', methods=['GET'])
def checkconnection():
    return "True"

    
if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080)


