def get_plants_json(self, chat_id):
        return str(self.plants[chat_id])

@app.route('/plants/list_plants', methods=['GET'])
def list_plants():
    try:
        chat_id = request.args.get('chat_id')
        list = my_server.get_plants_json(chat_id)
    except KeyError:
        return "error: no such chat id."
    except:
        return "error: Something went wrong."
    return list

@app.route('/plants/add_plants', methods=['POST'])
def list_plants():
    try:
        chat_id = request.args.get('chat_id')
        list = my_server.get_plants_json(chat_id)
    except KeyError:
        return "error: no such chat id."
    except:
        return "error: Something went wrong."
    return list