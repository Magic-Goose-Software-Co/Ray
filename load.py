from dotenv import load_dotenv
import os
import json
from pathlib import Path

def getConfig(file="config.json"):
    with (Path(__file__).resolve().parent / file).open("r") as configFile:
        return json.load(configFile)

def getPassword():
    load_dotenv()
    return os.getenv("PASSWORD")

def getEmails(file="emails.json"):
    with (Path(__file__).resolve().parent / file).open("r") as emailsFile:
        return json.load(emailsFile)