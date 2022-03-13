import json

class deviceHandler():
    """jsonHandler()"""
    def __init__(self):
        pass

    def jsonprint(self):
        with open("devices.json", 'r') as file:
            json_object = json.load(file)
            return json.dumps(json_object)
            
    def addDevice(self, device):
        # add sensor to "sensors" in Json object"
        deviceType = device["deviceType"] + "s"
        with open("devices.json", 'r') as file:
            # Reading from json file
            json_devices = json.load(file)
            if device not in json_devices[deviceType]:
                for element in json_devices[deviceType]:
                    if device["id"] == element["id"]:
                        print("ERROR: id %s is not unique, please specify another id" % (device["id"]))
                        return "ERROR: id %s is not unique, please specify another id" % (device["id"])
                        
               
                del device['deviceType']
                json_devices[deviceType].append(device)
                print("SUCCESS: Added new device")
            else: 
                print("ERROR: New device completely identical therefore not added")
                return "ERROR: New device completely identical therefore not added"
                       
        with open("devices.json", 'w') as outfile:
            temp = json.dumps(json_devices, indent=4)
            outfile.write(temp)
        self.createDeviceTopic(device, deviceType)
        return "Successfully added " + deviceType[:-1] + ": id=" + device["id"] + ", building=" + device["building"] +", floor="+ device["floor"] + ", room=" + device["room"]
            
    def getDeviceTopics(self):        
        with open("mqttTopics.json", 'r') as file:
            topics = json.load(file)
            topics = json.dumps(topics)
            
        return topics

    def getDevices(self):        
        with open("devices.json", 'r') as file:
            devices = json.load(file)
            devices = json.dumps(devices)
            
        return devices

    def createDeviceTopic(self, device, deviceType):
        topic = '/'.join([deviceType[:-1], device["id"], device["building"], device["floor"], device["room"]])
        with open("mqttTopics.json", 'r') as file:
            mqtt_object = json.load(file)
            mqtt_object[deviceType].append(topic)
        with open("mqttTopics.json", 'w') as outfile:
            temp = json.dumps(mqtt_object, indent=4)
            outfile.write(temp)
      

    def delDeviceTopic(self, device, deviceType):
        topic = '/'.join([deviceType[:-1], device["id"], device["building"], device["floor"], device["room"]])
        with open("mqttTopics.json", 'r') as file:
            mqtt_object = json.load(file)
            mqtt_object[deviceType].remove(topic)
        with open("mqttTopics.json", 'w') as outfile:
            temp = json.dumps(mqtt_object, indent=4)
            outfile.write(temp)


    def delDevice(self, device):
        # add device to "sensors" in Json object"
        deviceType = device["deviceType"] + "s"   
        with open("devices.json", 'r') as file:
            # Reading from json file
            json_devices = json.load(file)
            del device["deviceType"]
            if device in json_devices[deviceType]:                   
                json_devices[deviceType].remove(device)
                print("SUCCESS: device succesfully removed from catalog and mqtt topic")
            else: 
                print("ERROR: Device not found")
                return "ERROR: Device not found"

        with open("devices.json", 'w') as outfile:
            temp = json.dumps(json_devices, indent=4)
            outfile.write(temp)
        self.delDeviceTopic(device, deviceType)
        return "Successfully removed " + deviceType[:-1] + ": id=" + device["id"] + ", building=" + device["building"] +", floor="+ device["floor"] + ", room=" + device["room"]
                
    
# Unit test
if __name__ == "__main__":
    # json structure that fits with the device adder:
    newDevice = {
        "id": "4",
        "building": "factory",
        "floor": "4",
        "room": "0"
    }
    newDevice2 = {
        "deviceType": "actuator",
        "id": "3459",
        "building": "factory",
        "floor": "34",
        "room": "1"
    }
    deviceCatalog = deviceHandler()
    # config.jsonprint()
    # deviceCatalog.addDevice(newDevice)
    # deviceCatalog.addDevice(newDevice2.copy())
    deviceCatalog.addDevice(newDevice2.copy())
    # deviceCatalog.delDevice(newDevice2)
    # deviceCatalog.delDevice(newDevice)
    # deviceCatalog.jsonprint()

    # deviceCatalog.delDevice('airsensor')
    # deviceCatalog.jsonprint()
