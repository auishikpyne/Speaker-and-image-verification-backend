import glob
from tqdm import tqdm
import numpy as np
# import nemo.collections.asr as nemo_asr
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

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

@app.get("/")
async def home():
    return {"message": "Hello, Users!"}

# Define a route with path parameters
@app.post("/sign_up/")
async def sign_up(
    email: str = Form(...),
    password: str = Form(...),
    audio_file: UploadFile = File(...),
    facial_image: UploadFile = File(...)
):
    if collection.find_one({"email" : email}):
        logging.warning(f"Email {email} already exists")
        raise HTTPException(status_code=400, detail="Email already exists")
        
    audio_file_location = f"/home/auishik/EDA/speaker_verification/saved_audios/{audio_file.filename}"
    
    # Save the audio file to the specified location
    with open(audio_file_location, "wb") as audio_file_sample:
        audio_file_sample.write(audio_file.file.read())
    
    facial_image_file_location = f"/home/auishik/EDA/speaker_verification/saved_images/{facial_image.filename}"

    with open(facial_image_file_location, "wb") as image_file_sample:
        image_file_sample.write(facial_image.file.read())
    
    data = {
        'email': email,
        'password': password,
        'audio_file_location': audio_file_location,
        'facial_image_file_location': facial_image_file_location
    }
    
    result = collection.insert_one(data)
    inserted_id = result.inserted_id

    print(f"Received data - Email: {email} Password: {password}, Audio File location: {audio_file_location}, facial image location: {facial_image_file_location}, ID: {inserted_id}")
    # Log the request
    logging.info(f"Sign Up has been completed! Received data - Email: {email}, Password: {password}, Audio File location: {audio_file_location}, Facial Image location: {facial_image_file_location}, ID: {inserted_id}")

    # Your actual logic to store the data in a database or perform other operations

    return JSONResponse(content={"message": "Registration succesfull", "guid": f"{inserted_id}"}, status_code=200)
    

if __name__ == "__main__":
    
    uvicorn.run('sign_up_api:app', host="0.0.0.0", port=8001, reload=True,
            ssl_certfile='/etc/letsencrypt/live/dev.revesoft.com/cert.pem',
        ssl_keyfile='/etc/letsencrypt/live/dev.revesoft.com/privkey.pem')