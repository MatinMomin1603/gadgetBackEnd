from typing import Union
# import uvicorn
from fastapi import FastAPI,Request,File,UploadFile,Form
from fastapi.staticfiles import StaticFiles
import pymongo
from bson import ObjectId
import json
import time
app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

client = pymongo.MongoClient('localhost', 27017)
db = client["electronic"]

ip = "http://54.170.251.103/api"

@app.get("/")
def read_root():
    return "Welcome to electronic store"

@app.post("/admin/login")
async def adminLogin(request:Request):
    try:
        body = await request.json()
        check = db['admins'].find_one({"email" : body['email'],"password":body['password']})
        if check :
            return {"status" : True ,"message" : "Login success" ,"data":json.loads(json.dumps(check,default=str))}
        else:
            return {"status" : False ,"message" : "Wrong username or password" ,"data":{}}
    except Exception as e:
        return {"status" : False ,"message" : str(e) }

# @app.post("/admin/book")
# async def addBook(request:Request):
#     try:
#         body = await request.json()
#         db['books'].insert_one(body)
#         return {"status" : True ,"message" : "Book added" }
#     except Exception as e:
#         return {"status" : False ,"message" : "Something wrong"}

@app.post("/admin/device")
def fileupload(file:bytes = File(),name: str = Form(),category: str = Form(),description: str = Form(),qty: int = Form(),price: str = Form()):
    try:
        path = "/images/"+str(int(time.time()))+".jpg"
        with open("."+path,"wb") as f:
            f.write(file)
            f.close()
        db['devices'].insert_one({"name":name,"category":category,"description":description,"image":path,"price":price,"qty":qty})
        return {"status":True,"message":"Article added"}
    except Exception as e:
        return {"status" : False ,"message" : str(e) }

@app.get("/admin/device")
def getBooks(request:Request):
    try:
        books = []
        get = list(db['devices'].aggregate([
            {
                '$project': {
                    'name': 1, 
                    'category': 1, 
                    'description': 1, 
                    'qty': 1,
                    'price' :  1,
                    'image': {
                        '$concat': [
                           ip,'$image'
                        ]
                    }
                }
            }
        ]))
        return {"status" : True ,"message" : "Article fetch success" ,"data" :json.loads(json.dumps(get,default=str))}
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

@app.post("/admin/devices/edit")
async def updateBook(request:Request):
    try:
        body = await request.json()
        db['devices'].update_one({"_id":ObjectId(body['_id'])},{"$set":{"name":body['name'],"category":body['category'],"description":body['description'],"price":body['price'],"qty":body['qty']}})
        return {"status" : True ,"message" : "Article updated" }
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

@app.post("/admin/devices/delete")
async def deleteCategory(request:Request):
    try:
        body = await request.json()
        db['devices'].delete_one({"_id":ObjectId(body['id'])})
        return {"status" : True ,"message" : "Device deleted" }
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

@app.post("/user")
async def registerUser(request:Request):
    try:
        body = await request.json()
        db['users'].insert_one({"name":body['name'],"email":body['email'],"password":body['password'],"type":"user"})
        return {"status" : True ,"message" : "User registered" }
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

@app.post("/user/login")
async def adminLogin(request:Request):
    try:
        body = await request.json()
        check = db['users'].find_one({"email" : body['email'],"password":body['password']})
        if check :
            return {"status" : True ,"message" : "Login success" ,"data":json.loads(json.dumps(check,default=str))}
        else:
            return {"status" : False ,"message" : "Wrong username or password" ,"data":{}}
    except Exception as e:
        return {"status" : False ,"message" : str(e) }

@app.post("/user/device/view")
async def adminLogin(request:Request):
    try:
        body = await request.json()
        db['device_views'].insert_one({"user_id":ObjectId(body['user_id']),"device_id":ObjectId(body['device_id'])})
        get = list(db['devices'].aggregate([
            {"$match":{"_id":ObjectId(body['device_id'])}},
            {
                '$project': {
                    'name': 1,
                    'category': 1,
                    'description': 1,
                    'price':1,
                    'qty':1,
                    'image': {
                        '$concat': [
                            ip,'$image'
                        ]
                    }
                }
            }
            ]))
        return {"status":True,"data":json.loads(json.dumps(get,default=str))}
    except Exception as e:
        return {"status" : False ,"message" : str(e) }

@app.get("/user/dashboard")
async def adminLogin(request:Request):
    try:
        query = {}
        search = request.query_params.get('search')
        if search:
            query = {"$or":[{"name":{"$regex":search,'$options' : 'i'}},{"description":{"$regex":search,'$options' : 'i'}}]}
        get = list (db['devices'].aggregate([
            {"$match":query},
            {
                '$lookup': {
                    'from': 'device_views', 
                    'localField': '_id', 
                    'foreignField': 'device_id', 
                    'as': 'result'
                }
            }, {
                '$project': {
                    'name': 1, 
                    'category': 1, 
                    'description': 1, 
                    'qty':1,
                    'price':1,
                    'view_count': {
                        '$size': '$result'
                    },
                    'image': {
                        '$concat': [
                           ip,'$image'
                        ]
                    }
                }
            }, {
                '$sort': {
                    'view_count': -1
                }
            }
        ]))
        return {"status":True,"data":json.loads(json.dumps(get,default=str))}
    except Exception as e:
        return {"status" : False ,"message" : str(e) }

@app.post("/admin/category")
async def addCategory(request:Request):
    try:
        body = await request.json()
        db['categories'].insert_one(body)
        return {"status" : True ,"message" : "Category added" }
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

@app.get("/admin/category")
def category(request:Request):
    try:
        get = list(db['categories'].find())
        return {"status" : True ,"message" : "Category fetch success" ,"data" :json.loads(json.dumps(get,default=str))}
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

@app.post("/admin/category/delete")
async def deleteCategory(request:Request):
    try:
        body = await request.json()
        db['categories'].delete_one({"_id":ObjectId(body['id'])})
        return {"status" : True ,"message" : "Category deleted" }
    except Exception as e:
        return {"status" : False ,"message" : str(e)}

# if __name__ == "__main__":
#     uvicorn.run("main:app",host="0.0.0.0", port=80, reload=True)