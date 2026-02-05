import json
import os
from datetime import datetime

from .config import saveDir


def getConfig(file="config.json"):
    with (saveDir / file).open("r") as configFile:
        return json.load(configFile)


def getPassword():
    return os.getenv("PASSWORD")


def getEmails(file="emails.json"):
    if saveDir / file not in os.listdir():
        return {"lastRun": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "emails": {}}
    with (saveDir / file).open("r") as emailsFile:
        return json.load(emailsFile)


def saveConfig(address, server, password, mailboxes, sortType):
    # Ensure the save directory exists
    saveDir.mkdir(parents=True, exist_ok=True)

    # Save Configuration
    with (saveDir / "config.json").open("w") as configFile:
        json.dump({"address": address, "server": server, "mailboxes": mailboxes, "sortType": sortType}, configFile,
                  indent=4)

    with (saveDir / ".env").open("w") as dotEnv:
        dotEnv.write("PASSWORD=" + password)

    with (saveDir / "emails.json").open("w") as emailsFile:
        json.dump({"lastRun": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "emails": {}}, emailsFile, indent=4)
