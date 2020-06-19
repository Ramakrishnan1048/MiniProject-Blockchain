import pymongo
print("START")
client = pymongo.MongoClient("mongodb+srv://ramDbUser:pr0pIJj5ZQc3U4Ac@cluster0-komid.mongodb.net/trialDB?retryWrites=true&w=majority")

con = client["trailDB"]

for i in con.find():
	print(i)