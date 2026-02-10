import load

"""
def getLatestUID(account, mailbox):
    try:
        response = account.mail.select(mailbox)
        status, data = account.mail.search(None, "ALL")
        if data[0]:
            uids = sorted([int(uid) for uid in data[0].split()])
            return int(uids[-3]) if len(uids) >= 3 else (int(uids[0]) - 1 if uids else 0)
        return 0
    except Exception as e:
        print(e)
        return 0
"""
def getLatestUID(account, mailbox):
    try:
        account.mail.select("\""+mailbox+"\"")
        status, messages = account.mail.uid("search", None, "ALL")

        if status != "OK" or not messages[0]:
            return 0

        uids = [int(uid) for uid in messages[0].split()]

        return uids[-10] if len(uids) >= 10 else 0

    except Exception as e:
        print(e)
        return 0

def getMail(account, mailboxes, file="emails.json"):
    mail = load.getEmails(file=file)

    for mailbox in mailboxes:
        sortedMail = sorted(mail[mailbox], key=lambda email: email["uid"], reverse=True) if mailbox in mail else []

        newMail = []

        if len(sortedMail) > 0:
            latestUid = sortedMail[0]["uid"] if mailbox in mail else getLatestUID(account, mailbox)
        else:
            latestUid = getLatestUID(account, mailbox)

        newMail = account.getMailSinceUID(mailbox, latestUid)


        for email in newMail:
            for checkMailbox in mail:
                mail[checkMailbox] = [existingEmail for existingEmail in mail[checkMailbox] if existingEmail["messageId"] != email["messageId"]]

        try:
            mail[mailbox] += newMail
        except KeyError:
            mail[mailbox] = newMail


    return mail