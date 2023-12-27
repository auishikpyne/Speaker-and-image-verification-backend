import glob
from tqdm import tqdm
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import JSONResponse
import logging
import requests
import os
from deepface import DeepFace

url = 'http://119.148.4.20:9080/face_detection/'

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
@app.post("/image_verification/")
async def verify_images(
    facial_image: UploadFile = File(...)
):

    filename = facial_image.filename
    # print(filename)
    image_content = facial_image.file.read()
    guid = filename.split('.')[0]
    print(guid)
    # Specify the path where you want to save the image file
    sign_in_image_path = f"/home/auishik/EDA/speaker_verification/request_images/{filename}"

    # Write the image content to the specified path
    with open(sign_in_image_path, "wb") as image_output:
        image_output.write(image_content)
        
    user_data = collection.find_one({"_id": ObjectId(guid)})
    sign_up_image_path = user_data['facial_image_file_location']
    # response = requests.post(url, files={'facial_image': image_content}, data={'guid':guid})

    # print(response.json())
    

    
    
    result = DeepFace.verify(img1_path = sign_in_image_path, img2_path = sign_up_image_path, enforce_detection=False, model_name='VGG-Face')
    print(result)
    distance = result['distance']
    similarity_score = (1 - distance) * 100
    similarity_score = round(similarity_score, 2)
    print(similarity_score)
    
    # Log successful image verification
    logging.info(f"Image verification successful for file: {filename}. Similarity score: {similarity_score}%")

    return JSONResponse(content={"facial_similarity_score": similarity_score}, status_code=200)

    # except Exception as e:
    #     # Log the error
    #     logging.error(f"An error occurred during image verification: {str(e)}")
    #     raise HTTPException(status_code=500, detail="Internal Server Error. Please try again.")
    
if __name__ == "__main__":
    
    uvicorn.run('image_verification_api:app', host="0.0.0.0", port=8004, reload=True, workers=2,
                ssl_certfile='/etc/letsencrypt/live/dev.revesoft.com/cert.pem',
        ssl_keyfile='/etc/letsencrypt/live/dev.revesoft.com/privkey.pem')