from dotenv import load_dotenv
import os
import json
from pathlib import Path

home = Path.home()
rayDir = home / ".ray"
rayDir.mkdir(parents=True, exist_ok=True)

def getConfig(file="config.json"):
    with open(rayDir/file, "r") as configFile:
        return json.load(configFile)

def getPassword():
    load_dotenv(dotenv_path=rayDir/".env")
    return os.getenv("PASSWORD")

def getEmails(file="emails.json"):
    with open(rayDir/file, "r") as emailsFile:
        return json.load(emailsFile)

def writeConfig(config, file="config.json"):
    with open(rayDir/file, "w") as configFile:
        json.dump(config, configFile, indent=4)

def writePassword(password):
    with open(rayDir/".env", "w") as dotEnv:
        dotEnv.write("PASSWORD="+password)

def writeEmails(emails, file="emails.json"):
    with open(rayDir/file, "w") as emailsFile:
        json.dump(emails, emailsFile, indent=4)





