import logging
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import uvicorn

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
@app.post("/sign_in/")
async def sign_in(
    email: str = Form(...),
    password: str = Form(...)
):
    
    # Check if the email exists in the database
    user = collection.find_one({"email": email})
    
    if user is None:
        logging.warning(f"User not found for email: {email}")
        raise HTTPException(status_code=404, detail="Invalid credentials! User not found.")
    else:
        if password == user['password']:
            # Log successful sign-in
            logging.info(f"User signed in successfully - Email: {email}, ID: {user['_id']}")
            return JSONResponse(content={"message": "Password correct", "guid": str(user['_id'])}, status_code=200)
        else:
            # Log failed sign-in attempt
            logging.warning(f"Invalid credentials for user - Email: {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    

if __name__ == "__main__":
    
    uvicorn.run('sign_in_api:app', host="0.0.0.0", port=8002, reload=True,
        ssl_certfile='/etc/letsencrypt/live/dev.revesoft.com/cert.pem',
        ssl_keyfile='/etc/letsencrypt/live/dev.revesoft.com/privkey.pem')