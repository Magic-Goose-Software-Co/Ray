import json
from pathlib import Path
from datetime import datetime
import subprocess
import mail

print("Installing dependencies...")
for package in ["scikit-learn", "python-dotenv"]:
    installSuccess = subprocess.run(["pip", "install", package]).returncode == 0
    if installSuccess:
        print(f"Package installed: {package}!")
    else:
        print(f"Error installing {package}.")
        exit()

print("")
print("What is your email address?")
address = input("Address: ")

print("")
print("What is your password?")
print("Some mail servers such as iCloud and Gmail require this to be an \"App Specific Password\".")
print("This will be stored in the .env file instead of config.json.")
password = input("Password: ")
print("\033[1APassword: "+"•"*len(password))

print("")
print("What is the IMAP server?")
server = input("Server: ")

print("")
print("You should now create any mailboxes you will want Ray to move emails to (if you haven't already done so).")
print("Press return when you have created them.")
input("")

account = mail.Account(address, password, server)

mailboxes = []
print("Press Y for each of the following mailboxes if you want Ray to move emails to it.")
for mailbox in account.mailboxes:
    if input(mailbox+": (y/n) ").lower() == "y": mailboxes.append(mailbox)

print("")
print("Would you like Ray to sort based on the sender or the subject? ")
print("Type \"sender\" or \"subject\" (case-insensitive).")
sortType = input("Sort Type: ").lower()

with (Path(__file__).resolve().parent / "config.json").open("w") as configFile:
    json.dump({"address": address, "server": server, "mailboxes": mailboxes, "sortType": sortType}, configFile, indent=4)

with (Path(__file__).resolve().parent / ".env").open("w") as dotEnv:
    dotEnv.write("PASSWORD="+password)

with (Path(__file__).resolve().parent / "emails.json").open("w") as emailsFile:
    json.dump({"lastRun": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "emails": {}}, emailsFile, indent=4)

print("")
print("Ray is now fully configured and set up! Next time you receive an email, put it in the mailbox you would like Ray to put similar emails in. Run \"python .\" from inside the Ray directory or \"python path/to/ray/dir\" from outside.")
