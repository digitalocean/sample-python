from dotenv import load_dotenv
import os
import json

# Load environment variables from the .env file
load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

# Save the Google Cloud credentials JSON to a temporary file
with open("google_key.json", "w") as f:
    f.write(GOOGLE_APPLICATION_CREDENTIALS)

# Update the GOOGLE_APPLICATION_CREDENTIALS variable to point to the temporary file
GOOGLE_APPLICATION_CREDENTIALS = "google_key.json"
