from flask import Flask,Response,render_template,jsonify,request,abort,url_for
import requests
import csv
import re
import pymongo
import web3
import hashlib
from web3 import Web3
import json
import bson
import ast # convert "[{}]" to list and then to json

# connect to db in cloud: a cluster was created with username ramDbUser and password pr0pIJj5ZQc3U4Ac.
# db name is blockchain_db as noticed in url
client = pymongo.MongoClient("mongodb+srv://ramDbUser:pr0pIJj5ZQc3U4Ac@cluster0-komid.mongodb.net/blockchain_db?retryWrites=true&w=majority")
db_handle = client['blockchain_db_v2']
collection_handle = db_handle['blockchain_col_v2'] # Collection is analogous to table

app=Flask(__name__)

# Helper function: to convert string to 32 bytes hash value
def my_hash32(input_data):
	# Input: string - the string that needs to be hashed into 32 bytes
	# Return: string - the hexadecimal value of the hash
	sha_val = hashlib.sha256(str(input_data).encode()) # sha256 takes unicode object as input
	hex_val = int(sha_val.hexdigest(), 16) # convert result object to hex string and then to hexadecimal integer
	# val_32 = hex_val % 0xFFFFFFFF # max size of solidity uint32 is 0x FFFF FFFF. So only store the remainder
	return hex(hex_val)

#Node1 in the Iot ecosystem
def node1(id,data):
	ganache_url="http://127.0.0.1:7545"
	web3=Web3(Web3.HTTPProvider(ganache_url))
	
	node1_address="0xf49437Dd2E96f1249815c82727Cc17c8388d9349"
	node1_pk="22aaa185ee18e1b169fa7192d6428fcfc4db2f0386dffb1eee100c2cfdf94bd5"
	fp = open('abi.json', 'r')
	abi=json.load(fp)
	contract_address=web3.toChecksumAddress("0xbd12Ef3a93b06a72374188017Ef67b9FD8f6717e")
	contract=web3.eth.contract(address=contract_address,abi=abi)
	nonce=web3.eth.getTransactionCount(node1_address)
	transaction=contract.functions.addData(id,data).buildTransaction({
		'gas':70000,
		'gasPrice':web3.toWei('1','gwei'),
		'from': node1_address,
		'nonce': nonce
		
	})
	
	signed_transaction=web3.eth.account.signTransaction(transaction, node1_pk)
	transaction_hash=web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
	
	return web3.toHex(transaction_hash)

#Node2 in the Iot ecosystem
def node2(id,data):
	ganache_url="http://127.0.0.1:7545"
	web3=Web3(Web3.HTTPProvider(ganache_url))
	
	node2_address="0xe8652965ed04Bce6C9764e7eA80a26e61b434f8F"
	node2_pk="b28fc4327c99022b087d79e8edadada2e2d71d029d3552d4700bf78b7a3968f2"
	fp = open('abi.json', 'r')
	abi=json.load(fp)
	contract_address=web3.toChecksumAddress("0xbd12Ef3a93b06a72374188017Ef67b9FD8f6717e")
	contract=web3.eth.contract(address=contract_address,abi=abi)
	nonce=web3.eth.getTransactionCount(node2_address)

	# print("CMP! ADD TO BLOCKCHAIN id", id, "data", data, "readable", data.hex())
	transaction=contract.functions.addData(id,data).buildTransaction({
		'gas':70000,
		'gasPrice':web3.toWei('1','gwei'),
		'from': node2_address,
		'nonce': nonce
		
	})
	
	signed_transaction=web3.eth.account.signTransaction(transaction, node2_pk)
	transaction_hash=web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
	
	return web3.toHex(transaction_hash)

#Node3 in the Iot ecosystem
def node3(id,data):
	ganache_url="http://127.0.0.1:7545"
	web3=Web3(Web3.HTTPProvider(ganache_url))
	
	node3_address="0x4eD6E3e8102A2cE2924EabF5f9916BB3bD6B66d5"
	node3_pk="4058bc0213a462b74deb3bfc42eba9d35e6e0e15debbbc92fcfebe414fae6058"
	fp = open('abi.json', 'r')
	abi=json.load(fp)
	contract_address=web3.toChecksumAddress("0xbd12Ef3a93b06a72374188017Ef67b9FD8f6717e")
	contract=web3.eth.contract(address=contract_address,abi=abi)
	nonce=web3.eth.getTransactionCount(node3_address)
	transaction=contract.functions.addData(id,data).buildTransaction({
		'gas':70000,
		'gasPrice':web3.toWei('1','gwei'),
		'from': node3_address,
		'nonce': nonce
		
	})
	
	signed_transaction=web3.eth.account.signTransaction(transaction, node3_pk)
	transaction_hash=web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
	
	return web3.toHex(transaction_hash)

#Read from Blockchain
def validate(id):
	ganache_url="HTTP://127.0.0.1:7545"
	web3=Web3(Web3.HTTPProvider(ganache_url))
	fp = open('abi.json', 'r')
	abi=json.load(fp)
	contract_address=web3.toChecksumAddress("0xbd12Ef3a93b06a72374188017Ef67b9FD8f6717e")
	contract=web3.eth.contract(address=contract_address,abi=abi)
	
	web3.eth.defaultAccount=web3.eth.accounts[2]
	
	ret=contract.functions.getData(id).call()
	# print("CMP! DATA FROM BLOCKCHAIN id", id, ret.hex())
	print("value in blockchain for id", id, "is", "0x"+ret.hex())
	return "0x"+ret.hex()


@app.route("/")
def home():
	return render_template('home.html',title="HOME")

#################################### Write to the blockchain ########################################
#### Camera
@app.route("/camera",methods=['POST'])
def camera():
	if(request.method=='POST'):
		bid=request.get_json()['bid']
		value=request.get_json()['value']
		value=my_hash32(value)#convert this to uint32
		ret=node1(bid,value)
		if(ret):
			write_res=requests.post('http://localhost:5000/write_db',json={'txn_id':ret,'bid':bid,'value':value})
			if(write_res):
				return Response(status=201)
			else:
				return Response(status=400)

		else:
			return jsonify('Not authenticated'),400

#### HVAC
@app.route("/hvac",methods=['POST'])
def hvac():
	# Input: bid -> integer, value -> bytes
	bid=request.get_json()['bid']
	value=request.get_json()['value']
	print("/hvac got bid", bid, "value", value)
	value=json.dumps(value) # Convert to bytes
	print("convert to", type(value), "using json.dumps", value)
	value=my_hash32(value) # hash it and fit into 32 bytes
	print("hashed with sha256", value, "\nCall to node2")
	ret=node2(bid,value)
	if(ret):
		write_data = {'txn_id':ret,'bid':bid,'value':value}
		print("node2 returned", ret, "\ncall to write_db with data", write_data)
		write_res=requests.post('http://localhost:5000/write_db',json=write_data)
		print("write_db returned", write_res)
		if(write_res):
			return Response(status=201)
		else:
			return Response(status=400)
	else:
		return jsonify('Not authenticated'),400

#### Voice assistant
@app.route("/voice",methods=['POST'])
def voice():
	if(request.method=='POST'):
		bid=request.get_json()['bid']
		value=request.get_json()['value']
		value=my_hash32(value)#convert this to uint32
		ret=node3(bid,value)
		if(ret):
			write_res=requests.post('http://localhost:5000/write_db',json={'txn_id':ret,'bid':bid,'value':value})
			if(write_res):
				return Response(status=201)
			else:
				return Response(status=400)

		else:
			return jsonify('Not authenticated'),400

###################################### Read from blockchain ################################################
@app.route("/verify_and_read",methods=['POST'])
def verify_and_read():
	if(request.method=='POST'):
		bid=request.get_json()['bid']
		read_res=requests.post('http://localhost:5000/read_db',json={'bid':bid})
		# print("START")
		a=ast.literal_eval(read_res.json())[0]
		# a = dict(list(read_res.json())[0])
		# print(type(a), a, a['value'])
		encrypt=a['value']
		b_encrypt=validate(bid)
		# print(encrypt.to_bytes(32, byteorder='little').hex(), b_encrypt.hex())
		print("comparing", encrypt, b_encrypt)
		# print("readable", encrypt.hex(), b_encrypt.hex())
		if(encrypt==b_encrypt):
			return jsonify('Data not corrupted'),200
		else:
			return jsonify('Data is corrupted'),200



########################### Database related APIs ###########################################
@app.route("/read_db", methods=['POST'])
def read_db():
	input_data = request.get_json()
	# print("read_db INP data", type(input_data), input_data)
	data = collection_handle.find(input_data, {"_id":0})
	ret = []
	for i in data:
		ret.append(i)
	data_json=json.dumps(ret)
	# print("read_db OUT data", type(data_json), data_json)
	return jsonify(data_json), 200

@app.route("/write_db", methods=['POST'])
def write_db():
	data = request.get_json()
	# print(data, type(data))
	ret = collection_handle.insert_one(data)
	# print("write_db INP data", type(data), data)
	if ret.acknowledged == True:
		return jsonify("Write successful. Wrote: "+str(data)), 201
	else:
		return jsonify("Write failed. Attempted to write: "+str(data)+". Check connection and try again"), 404

if __name__ == '__main__':
	app.run(debug=True)


