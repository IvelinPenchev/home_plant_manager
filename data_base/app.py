from flask import Flask, jsonify
from flask import request as rq
import requests
import json

class myPlants:
    def __init__(self):
        self.plants = json.load(open("plants.json"))
        self.config = json.load(open("config.json"))

        try:
            self.conf = json.load(open("config.json"))
            self.update_conf_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["get_config_url"]
            self.update_conf()
            self.is_connection_url = self.conf['catalogue']["server_url"] + ":" + self.conf['catalogue']["port"] + self.conf['catalogue']["test_connection_url"]
            self.server_down_msg = "Our server is down. Please try again later. We apologize for the inconvenience!"
            self.db_server = [self.conf['data_base']["db_url"],self.conf['data_base']["port"]]       
        except: 
            print("Initialisation error: Could not read from config.")
    
    def update_plants(self):
        self.plants = json.load(open("plants.json"))

    def is_server_connection(self):
        try:
            requests.get(self.is_connection_url)
        except requests.exceptions.ConnectionError:
            print("ERROR: Server is down.")
            return False
        except:
            print("ERROR: Unknown server error!" + str(self.is_connection_url))
            return False
        return True

    def update_conf(self):
        if(self.is_server_connection):
            try:
                r = requests.get(self.update_conf_url)
                with open("config.json", "w") as myfile:
                    myfile.write(str(r.text))
            except:
                print("Error: Could not update configs although server is up")
        else: print("Server is down. Could not update configs")

    def get_plants_json(self, chat_id):
        return str(self.plants[chat_id])
    

app = Flask(__name__)
my_plants = myPlants()
db_host = my_plants.db_server[0].replace("http://","",1)
db_port = my_plants.db_server[1]

@app.route('/plants/listplants', methods=['GET'])
def list_plants():
    my_plants.update_plants()
    try:
        chat_id = rq.args.get('chat_id')
        list = my_plants.get_plants_json(chat_id)
    except KeyError:
        return "error 404: no such chat id."
    except:
        return "error 400: Something went wrong."
    return str(list)

# @app.route('/plants/add_plant2', methods=['POST'])
# def add_plants2():
#     try:
#         data = rq.args.get('data')
#         print(data)
#     except:
#         print("1")
#     try:
#         data = rq.form['data']
#         print(data)
#     except:
#         print("2")
#     try:
#         data = rq.get_json('data')
#         print(data)
#     except:
#         print("3")
#     try:
#         data = rq.json
#         print(data)
#     except:
#         print("4")
#     return data

@app.route('/plants/add_plant', methods=['POST'])
def add_plants():
    my_plants.update_plants()
    try:
        chat_id = rq.args.get('chat_id')
        my_plants.get_plants_json(chat_id)
    except KeyError:
        return "error 400: no such chat id."
    except:
        return "error 400: Something went wrong with the chat_id"

    try:
        plant = rq.json
    except ValueError:
        return "error 400: Input is not in the correct form (json)."
    except:
        return "error 400: Something went wrong with the json."
    if plant is dict or type(plant)== dict:
        with open('plants.json', 'r+') as f:
            all_plants = json.load(f)
            all_plants[chat_id].append(plant)
            f.seek(0)
            json.dump(all_plants, f, indent=4)
            f.truncate()     # remove remaining part
    else:
        return "error 400: Input is not a dict"

    return "200"



if __name__ == '__main__':
    app.run(host=db_host, port=db_port)
    