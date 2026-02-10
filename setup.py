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

import load

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
print("You should now create any mailboxes you will want Ray Sort to move emails to.")
print("Press return when you have created them.")
input("")

account = mail.Account(address, password, server)

mailboxes = []
print("Press Y for each of the following mailboxes if you want Ray Sort to move emails to it.")
for mailbox in account.mailboxes:
    if input(mailbox+": (y/n) ").lower() == "y": mailboxes.append(mailbox)

print("")
print("Would you like Ray Sort to sort based on the sender or the subject? ")
print("Type \"sender\" or \"subject\" (case-insensitive).")
sortType = input("Sort Type: ").lower()

load.writeConfig({"address": address, "server": server, "sortMailboxes": mailboxes, "sortType": sortType})
load.writePassword(password)
load.writeEmails({})
load.writeEmails({}, "sortEmails.json")

print("")
print("Ray is now fully configured and set up! To use Ray Sort, next time you receive an email, put it in the mailbox you would like Ray to put similar emails in and run \"python ./sort.py\" from inside the Ray directory or \"python path_to_ray_dir/sort.py\" from outside.")
