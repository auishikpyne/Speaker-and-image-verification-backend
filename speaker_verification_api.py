import glob
import logging
from tqdm import tqdm
import numpy as np
import nemo.collections.asr as nemo_asr
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from fastapi.responses import JSONResponse


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

# Load the speaker model
speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large", map_location='cpu')


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
@app.post("/speaker_verification/")
async def verify_speakers(
    audio_file: UploadFile = File(...)
):
    try:
        
        filename = audio_file.filename
        print(filename)
        audio_content = audio_file.file.read()
        
        # Specify the path where you want to save the audio file
        saved_audio_path = f"/home/auishik/EDA/speaker_verification/request_audios/{filename}.wav"
        
        # Write the audio content to the specified path
        with open(saved_audio_path, "wb") as audio_output:
            audio_output.write(audio_content)
            
        incoming_audio_path = saved_audio_path
        guid = filename.split('.')[0]
        # print(guid)
        # Convert the guid to ObjectId
        guid_object_id = ObjectId(guid)

        # Check if the guid (as ObjectId) exists in the MongoDB collection
        user = collection.find_one({"_id": guid_object_id})
        print(user)
        original_audio_sample_path = user['audio_file_location']
        # print(original_audio_sample_path)
        similarity_score = speaker_model.verify_speakers(incoming_audio_path, original_audio_sample_path)
        similarity_percentage = round(similarity_score.item() * 100, 2)
        
        # Log the successful verification
        logging.info(f"Speaker verification successful for user {guid}. Similarity score: {similarity_percentage}%")
        
        return JSONResponse(content={ "similarity_score": similarity_percentage}, status_code=200)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Log the error
        logging.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error. Please try again.")
        


if __name__ == "__main__":
    
    uvicorn.run('speaker_verification_api:app', host="0.0.0.0", port=8000, reload=True, workers=2,
                ssl_certfile='/etc/letsencrypt/live/dev.revesoft.com/cert.pem',
        ssl_keyfile='/etc/letsencrypt/live/dev.revesoft.com/privkey.pem')
