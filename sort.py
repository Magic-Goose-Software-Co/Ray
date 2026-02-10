import load
import mail
import getMail
import ml

config = load.getConfig()
account = mail.Account(config["address"], load.getPassword(), config["server"])

notFoundMailboxes = list(set(config["sortMailboxes"]) - set(account.mailboxes))
for mailbox in notFoundMailboxes:
    print(f"[ERROR] Expected mailbox \"{mailbox}\" was not found.")
if len(notFoundMailboxes) != 0:
    exit()

for mailbox in list(set(account.mailboxes) - set(config["sortMailboxes"])):
    print(f"[INFO] Mailbox \"{mailbox}\" will not be a sort destination.")

trainingMail = getMail.getMail(account, config["sortMailboxes"], file="sortEmails.json")

newInbox = list(set(trainingMail) - set(load.getEmails(file="sortEmails.json")))

model = ml.Model(trainingMail)

if config["sortType"] == "subject":
    sortFunc = model.sortBySubject
elif config["sortType"] == "sender":
    sortFunc = model.sortBySender

latestUid = sorted(trainingMail["INBOX"], key=lambda email: email["uid"])[-1]["uid"] if "INBOX" in trainingMail else getMail.getLatestUID(account, "INBOX")

for email in account.getMailSinceUID("INBOX", latestUid):
    destination = sortFunc(email)
    account.moveEmail(email["uid"], "INBOX", destination)
    trainingMail[destination].append(email)
    if destination == "INBOX":
        print("[INFO] Left \""+email["subject"]+"\" (sent by \""+email["sender"]+" in the inbox.")
    else: print("[INFO] Moved \""+email["subject"]+"\" (sent by \""+email["sender"]+f"\") to \"{destination}\".")

load.writeEmails(trainingMail, file="sortEmails.json")

account.logout()

