import imaplib
import email
from email.header import decode_header
from datetime import datetime


def decodeMimeWords(s):
    decodedFragments = decode_header(s)
    decodedString = ""

    for fragment, encoding in decodedFragments:
        if isinstance(fragment, bytes):
            decodedString += fragment.decode(
                encoding or "utf-8",
                errors="replace"
            )
        else:
            decodedString += fragment

    return decodedString

class Account:
    def __init__(self, address, password, server):
        self.address = address
        self.password = password
        self.server = server

        self.mail = imaplib.IMAP4_SSL(self.server)
        self.mail.login(self.address, self.password)
        self.mailboxes = [mailbox.decode().split("\"")[3] for mailbox in self.mail.list()[1]]

    def getMail(self, mailbox, sinceDate, limit=None):
        emails = []

        try:
            self.mail.select(mailbox)

            imapDate = sinceDate.strftime("%d-%b-%Y")

            status, messages = self.mail.uid("search", None, f"SINCE \"{imapDate}\"")

            if status != "OK":
                return emails

            if not messages[0]:
                return []

            uids = messages[0].split()

            if limit:
                uids = uids[-limit:]

            for uid in uids:
                status, data = self.mail.uid("fetch", uid, "(BODY.PEEK[HEADER])")

                if status != "OK":
                    continue

                if not data or not isinstance(data[0], tuple):
                    continue

                rawEmail = data[0][1]

                if not isinstance(rawEmail, bytes):
                    continue

                msg = email.message_from_bytes(rawEmail)

                subject = decodeMimeWords(msg.get("subject", ""))

                sender = decodeMimeWords(msg.get("from", ""))

                date = msg.get("date", "")

                emails.append({
                    "uid": int(uid),
                    "sender": sender,
                    "subject": subject,
                    "date": date
                })

            return emails

        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
            return []

    def moveEmail(self, uid, source, destination):
        self.mail.select(source)
        self.mail.uid("MOVE", str(uid), destination)

    def logout(self):
        self.mail.logout()
