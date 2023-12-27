import glob
import logging
from tqdm import tqdm
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import JSONResponse
from fastapi import Query



# Configure logging
logging.basicConfig(
    filename="/home/auishik/EDA/speaker_verification/biometric_logfile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

connection_url = "mongodb://mongo:edfrty5&!%406*65@119.148.4.20:27017/?authMechanism=DEFAULT"
client = MongoClient(connection_url)
db = client.test_db
collection = db.test_collection

# Create an instance of the FastAPI class
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your allowed origins
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Define a route using a decorator and an asynchronous function
@app.get("/")
async def home():
    return {"message": "Hello, Users!"}


# Define a route with path parameters
@app.get("/delete_user/")
async def delete(
    guid: str = Query(...)):
    try:
        # Convert the guid to ObjectId
        guid_object_id = ObjectId(guid)
        
        # Delete the document with the specified _id
        result = collection.delete_one({"_id": guid_object_id})
        
        # Log the successful deletion
        logging.info(f"User with GUID {guid} deleted successfully")
        
        return JSONResponse(content={"message": f"User with GUID {guid} deleted successfully"}, status_code=200)
    
    except Exception as e:
        logging.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


if __name__ == "__main__":
    
    uvicorn.run('delete_user_api:app', host="0.0.0.0", port=8005, reload=True,
                ssl_certfile='/etc/letsencrypt/live/dev.revesoft.com/cert.pem',
        ssl_keyfile='/etc/letsencrypt/live/dev.revesoft.com/privkey.pem')
