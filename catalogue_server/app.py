from flask import Flask, request, jsonify
import requests
import json

# main server used as a catalogue for services. It distributes the file "config.json" to other nodes
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

# main endpoint, returning the configurations with all services
@app.route('/getconfig', methods=['GET'])
def get_configs():
    return my_server.get_configs()

# endpoint used for testing connection with the server
@app.route('/checkconnection', methods=['GET'])
def checkconnection():
    return "True"

    
if __name__ == '__main__':
    app.run(host = my_server.get_configs['catalogue']["server_url_stripped"], port = get_configs['catalogue']["port"])


