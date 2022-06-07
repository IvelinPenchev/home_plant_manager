import pymongo

# client = pymongo.MongoClient("mongodb+srv://ivo_penchev:***REMOVED***@cluster0.o8rmbp3.mongodb.net/?retryWrites=true&w=majority")
client = pymongo.MongoClient("mongodb+srv://***REMOVED***:***REMOVED***@cluster0.o8rmbp3.mongodb.net/?retryWrites=true&w=majority")
db = client.test


# mydb = client["mydatabase"]
# mycol = mydb["customers"]

# print(mydb.list_collection_names())

mydb = client["mydatabase"]
mycol = mydb["customers"]

mydict = {"_id": 2, "name": "Bai Ivan", "address": "Highway 37" }

# x = mycol.insert_one(mydict)

# print(mydb.list_collection_names())

myquery = { "_id": 12 }

mydoc = mycol.find(myquery)

list_1 = []

# for x in mycol.find():
#   print(x)
#   list_1.append(x)
# print(type(mydoc))

# print(type(mydoc[0]))

# for x in mydoc:
#   print(x)
#   list_1.append(x)

# print(str(list_1))

# # print(str(list_1==[]))
myquery = { "name": "Bai Ivan" }

print(mycol.delete_one(myquery))
