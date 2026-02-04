from datetime import datetime
from pathlib import Path
import json
import load
import mail
import sort

config = load.getConfig()
account = mail.Account(config["address"], load.getPassword(), config["server"])

notFoundMailboxes = list(set(config["mailboxes"]) - set(account.mailboxes))
for mailbox in notFoundMailboxes:
    print(f"[ERROR] Expected mailbox \"{mailbox}\" was not found.")
if len(notFoundMailboxes) != 0:
    exit()

for mailbox in list(set(account.mailboxes) - set(config["mailboxes"])):
    print(f"[INFO] Mailbox \"{mailbox}\" will not be a sort destination.")


emails = load.getEmails()

trainingMail = emails["emails"]
lastRun = datetime.strptime(emails["lastRun"], "%Y-%m-%d %H:%M:%S")

for mailbox in config["mailboxes"]:
    if mailbox != "INBOX":
        newMail = account.getMail(mailbox, lastRun)
        try:
            trainingMail[mailbox] += newMail
        except KeyError:
            trainingMail[mailbox] = newMail

model = sort.Model(trainingMail)

if config["sortType"] == "subject":
    sortFunc = model.sortBySubject
elif config["sortType"] == "sender":
    sortFunc = model.sortBySender

for email in account.getMail("INBOX", lastRun):
    destination = sortFunc(email)
    account.moveEmail(email["uid"], "INBOX", destination)
    trainingMail[destination].append(email)
    print("[INFO] Moved \""+email["subject"]+"\" (sender \""+email["sender"]+f"\") to \"{destination}\".")

with (Path(__file__).resolve().parent / "emails.json").open("w") as emailsFile:
    json.dump({"lastRun": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "emails": trainingMail}, emailsFile, indent=4)

account.logout()

