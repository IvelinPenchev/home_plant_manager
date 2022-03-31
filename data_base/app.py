from flask import Flask, jsonify, abort
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
        self.update_plants()
        return str(self.plants[chat_id])

    def create_user_if_not_exist(self, chat_id):
        self.update_plants()
        if len(chat_id) > 4:
            try:
                self.plants[chat_id]
            except KeyError:
                with open('plants.json', 'r+') as f:
                    all_plants = json.load(f)
                    all_plants[chat_id] = []
                    f.seek(0)
                    json.dump(all_plants, f, indent=4)
                    f.truncate()     # remove remaining part
                my_plants.update_plants()

    

app = Flask(__name__)
my_plants = myPlants()
db_host = my_plants.db_server[0].replace("http://","",1)
db_port = my_plants.db_server[1]

@app.route('/plants/listplants', methods=['GET'])
def list_plants():
    my_plants.update_plants()
    try:
        pass
        chat_id = rq.args.get('chat_id')
        my_plants.create_user_if_not_exist(chat_id)
        list = my_plants.get_plants_json(chat_id)
    except:
        print("error 500: Something went wrong with listing plants.")
        abort(500)
    return str(list)

@app.route('/plants/getlastid', methods=['GET'])
def get_last_id():
    my_plants.update_plants()
    try:
        chat_id = rq.args.get('chat_id')
        my_plants.create_user_if_not_exist(chat_id)
        if not bool(my_plants.plants[chat_id]): return str(0)
        last_plant_id = my_plants.plants[chat_id][-1]['id']
    except KeyError:
        print ("error 500: invalid id.")
        abort(500)
    except:
        print ("error 500: Something went wrong with getting last id.")
        abort(500)
    return str(last_plant_id)

@app.route('/plants/add_plant', methods=['POST'])
def add_plants():
    my_plants.update_plants()
    print("attempting to add a new plant!")
    try:
        chat_id = rq.args.get('chat_id')
        my_plants.create_user_if_not_exist(chat_id)
        my_plants.get_plants_json(chat_id)
    except KeyError:
        print("error 500: invalid chat id.")
        abort(500)
    except:
        print("error 500: Something went wrong with adding plants")
        abort(500)
    try:
        plant = rq.json
        print(plant)
    except:
        print("error 500: Something went wrong with the json while adding plants.")
        abort(500)
    if plant is dict or type(plant)== dict:
        with open('plants.json', 'r+') as f:
            all_plants = json.load(f)
            all_plants[chat_id].append(plant)
            f.seek(0)
            json.dump(all_plants, f, indent=4)
            f.truncate()     # remove remaining part
        print("New plant added!")
    else:
        print( "error 500: Input was not a dict")
        abort(500)

    return "True"

@app.route('/plants/delete_plant', methods=['DELETE'])
def delete_plant():
    try:
        chat_id = rq.args.get('chat_id')
        plant_id = rq.args.get('plant_id')
        with open('plants.json', 'r+') as f:
            all_plants = json.load(f)
            list = all_plants[chat_id]
            success = False
            for count, dict in enumerate(list):
                if dict['id'] == plant_id:
                    del all_plants[chat_id][count]
                    success = True
                    break
            f.seek(0)
            json.dump(all_plants, f, indent=4)
            f.truncate()     # remove remaining part
        if not success: 
            print("Could not delete that plant from that user.")
            abort(404)
    except:
        print("Something went wrong with deleting a plant")
        abort(500)
    return "True"



if __name__ == '__main__':
    app.run(host=db_host, port=db_port)
    