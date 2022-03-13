from pydoc_data.topics import topics
from requests import api
import cherrypy
import json
import requests
from jsonhandling import deviceHandler

#docs for requests:
#https://requests.readthedocs.io/en/master/

# >>> payload = {'deviceType': 'sensor', "id": '0', building': 'factory', "floor": '0', "room": '0'}
# For web testing /API/ADDDEVICE?deviceType=sensor&id=2&building=factory&floor=0&room=0
# >>> r = requests.get('127.0.0.1:8080/API/ADDDEVICE/', params=payload)
# /API/ADDDEVICE/json: r = requests.get('127.0.0.1:8080/API/ADDDEVICE/', params=payload)
# /API/DELDEVICE/json: r = requests.get('127.0.0.1:8080/API/DELDEVICE/', params=payload)
# /API/DISPLAYDEVICES: r = requests.get('127.0.0.1:8080/API/DISPLAYDEVICES/', params=payload) cherrypy.log(str(params))
# 127.0.0.1:8080/GET/TOPICS 
# 127.0.0.1:8080/GET/TELEGRAMTOKEN 

class Catalogue:
    exposed=True
    def __init__(self):
        self.deviceHandler = deviceHandler()

    @cherrypy.expose
    
    def GET(self, *uri, **params):		
        if len(uri) > 0:
            if uri[0].lower() == "graphs":
                return open('graphs.html')
            if uri[0].lower() == "get":
                if uri[1].lower() == "topics":
                    return self.deviceHandler.getDeviceTopics()
                elif uri[1].lower() == "telegramtoken":
                    with open("config.json", 'r') as file:
                        json_object = json.load(file)                        
                        return json_object
                elif uri[1].lower() == "devices":
                    return self.deviceHandler.getDevices()
            if uri[0].lower() == "devices":
                return open('index.html')

    
    @cherrypy.expose
    def PUT(self, *uri, **params):
        output = "PUT"
        if len(uri) > 0:# check if the URI is used:
            if uri[0].lower() == "api":
                if uri[1].lower() == "adddevice":
                    if params != {}:
                        return self.deviceHandler.addDevice(params)
                if uri[1].lower() == "deldevice":
                    if params != {}:      
                        return self.deviceHandler.delDevice(params)
        else:
            return output
    
    @cherrypy.expose       
    def POST(self, *uri, **params):
        output = "POST"
        if len(uri) > 0:# check if the URI is used:
            if uri[0].lower() == "api":
                if uri[1].lower() == "adddevice":
                    if params != {}:
                        return self.deviceHandler.addDevice(params)
                if uri[1].lower() == "deldevice":
                    if params != {}:      
                        return self.deviceHandler.delDevice(params)
        else:
            return output
if __name__=="__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    conf={
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True,
		}
    }
    cherrypy.tree.mount(Catalogue(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()

  