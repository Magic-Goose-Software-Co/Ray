from math import floor, ceil
import copy
import re
import load
import mail
import os
import getMail
import sys
import termios
import tty
import textwrap

def readKey():
    fileDescriptor = sys.stdin.fileno()
    originalSettings = termios.tcgetattr(fileDescriptor)

    try:
        tty.setraw(fileDescriptor)
        char = sys.stdin.read(1)

        if char == "\x1b":
            char += sys.stdin.read(2)

        return char
    finally:
        termios.tcsetattr(fileDescriptor, termios.TCSADRAIN, originalSettings)

def clear():
    os.system("clear")

class Panel:
    def __init__(self, content, title="", textColor=0, titleColor=0, boxColor=0, margins=1, alignment="center"):
        self.content = content.split("\n")
        self.title = " "+title+" " if title != "" else ""
        self.textColor = textColor
        self.titleColor = titleColor
        self.boxColor = boxColor
        self.margins = margins
        self.alignment = alignment

    def string(self):
        contentLength = len(sorted([re.sub(r"\x1b\[[0-9;]*m", "", line) for line in self.content]+[self.title], key=len, reverse=True)[0]) + self.margins*2
        topHalve = (contentLength-len(self.title))/2
        lines = []
        lines.append(f"\033[{self.boxColor}m╭"+"─"*floor(topHalve)+f"\033[{self.titleColor}m"+self.title+f"\033[{self.boxColor}m"+"─"*ceil(topHalve)+"╮")
        for line in self.content:
            margins = contentLength-len(re.sub(r"\x1b\[[0-9;]*m", "", line))
            if self.alignment == "center":
                leftMargin = " "*floor(margins/2)
                rightMargin = " "*ceil(margins/2)
            elif self.alignment == "left":
                leftMargin = ""
                rightMargin = " "*margins
            elif self.alignment == "right":
                leftMargin = " "*margins
                rightMargin = " "
            lines.append(f"\033[{self.boxColor}m│"+f"\033[{self.textColor}m"+leftMargin+line+f"\033[{self.boxColor}m"+rightMargin+"│")
        lines.append(f"\033[{self.boxColor}m╰"+"─"*contentLength+"╯\033[0m")
        return lines

    def draw(self):
        for line in self.string():
            print(line)

"""def drawMergedPanels(panel1, panel2, boxColor=0):
    topHalve1 = (len(panel1.content)-len(panel1.title))/2
    topHalve2 = (len(panel2.content)-len(panel2.title))/2

    print(f"\033[{boxColor}m╭"+"─"*floor(topHalve1)+f"\033[{panel1.titleColor}m"+panel1.title+f"\033[{boxColor}m"+"─"*ceil(topHalve1)+"┬"+"─"*floor(topHalve2)+f"\033[{panel2.titleColor}m"+panel2.title+f"\033[{boxColor}m"+"─"*ceil(topHalve2)+"╮")
    print(f"│\033[{panel1.textColor}m"+panel1.content+f"\033[{boxColor}m│\033[{panel2.textColor}m"+panel2.content+f"\033[{boxColor}m│")
    print("╰"+"─"*len(panel1.content)+"┴"+"─"*len(panel2.content)+"╯\033[0m")"""

def drawMergedPanels(*panels, boxColor=0):
    panels = [copy.deepcopy(panel) for panel in panels]

    longest = len(sorted(panels, key=lambda panel: len(panel.content), reverse=True)[0].content)

    for panel in panels:
        panel.content += [" "]*(longest-len(panel.content))

    for i in range(len(panels[0].string())):
        if i == 0:
            print(panels[0].string()[i][:-1], end="")
            for panel in panels[1:]:
                print("┬"+"m".join(panel.string()[i].split("m")[1:])[1:-1], end="")
            print("╮")
        elif i == len(panels[0].string())-1:
            print(panels[0].string()[i][:-5], end="")
            for panel in panels[1:]:
                print("┴"+"m".join(panel.string()[i].split("m")[1:])[1:-5], end="")
            print("╯")
        else:
            print(panels[0].string()[i], end="")
            for panel in panels[1:]:
                print("m".join(panel.string()[i].split("m")[1:])[1:], end="")
            print("")


#Account setup and mail retrieval
config = load.getConfig()
account = mail.Account(config["address"], load.getPassword(), config["server"])
emails = getMail.getMail(account, account.mailboxes)
load.writeEmails(emails)

selectedMailbox = "INBOX"
shownSelectedMailbox = "INBOX"
selectedEmail = 0
shownSelectedEmail = 0
offset = 0
maxEmails = 7

emailSelection = False

newEmail = True

while True:

    #Mailbox panel
    mailboxPanels = []
    width = 15

    widest = len(sorted(account.mailboxes, key=len, reverse=True)[0])+3
    if widest>width: width = widest

    for mailbox in account.mailboxes:
        margins = width-len(mailbox)
        mailboxPanels.append(Panel(mailbox+" "*margins, margins=0, boxColor=(32 if shownSelectedMailbox == mailbox and not emailSelection else (34 if selectedMailbox == mailbox else 0))))

    mailboxesPanel = Panel("\n".join(["\n".join(panel.string()) for panel in mailboxPanels]), titleColor=34, title="Mailboxes", margins=0)

    #Email panel
    emailPanels = []
    emailsInMailbox = emails[selectedMailbox][::-1]
    width = 125

    if len(emailsInMailbox) == 0:
        emailsPanel = Panel(f"No emails found in \"{selectedMailbox}\".", textColor=31, titleColor=34, title="Emails (0)")
        bodyPanel = Panel("No email to display.", textColor=31, titleColor=31, title="Error")
    else:
        widest = len(sorted([email["subject"] for email in emailsInMailbox]+[email["sender"] for email in emailsInMailbox], key=len, reverse=True)[0])+3
        if widest>width: width = widest

        for i in range(len(emailsInMailbox[:maxEmails])):
            i = i+offset
            subject = emailsInMailbox[i]["subject"].replace("\n", "").replace("\r", "")
            sender = emailsInMailbox[i]["sender"].replace("\n", "").replace("\r", "")

            subjectMargins = width-len(subject)
            senderMargins = width-len(sender)

            emailPanels.append(Panel(subject+" "*subjectMargins+"\n"+sender+" "*senderMargins, margins=0, boxColor=(32 if shownSelectedEmail == i and emailSelection else (34 if selectedEmail == i else 0))))

        emailsPanel = Panel("\n".join(["\n".join(panel.string()) for panel in emailPanels]), titleColor=34, title=f"Emails ({len(emailsInMailbox)})", margins=0)
        if newEmail:
            width = 100
            body = account.getBody(selectedMailbox, emailsInMailbox[selectedEmail]["uid"]).replace("\r", "")
            body = body.split("\n")
            wrappedBody = []
            for line in body:
                if len(line) > width:
                    wrappedBody += textwrap.wrap(line, width)

            bodyPanel = Panel("\n".join(wrappedBody), titleColor=34, title=emailsInMailbox[selectedEmail]["subject"].replace("\n", "").replace("\r", ""), alignment="left")
            bodyPanel.content = bodyPanel.content[:40]

    #Rendering
    clear()
    drawMergedPanels(mailboxesPanel, emailsPanel, bodyPanel)

    key = readKey()

    while key not in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "\x03", "\r"]:
        key = readKey()

    newEmail = key == "\r"

    if key == "\x03": break
    elif key == "\x1b[C": emailSelection = True
    elif key == "\x1b[D": emailSelection = False
    elif key == "\r":
        if emailSelection: selectedEmail = shownSelectedEmail
        else:
            selectedMailbox = shownSelectedMailbox
            selectedEmail = 0
            offset = 0
    else:
        if key == "\x1b[A": selection = -1
        elif key == "\x1b[B": selection = 1

        if emailSelection:
            shownSelectedEmail = max(0, min(shownSelectedEmail+selection, len(emails[selectedMailbox])-1))
            if shownSelectedEmail >= offset+maxEmails: offset += 1
            elif shownSelectedEmail < offset: offset -= 1
        else: shownSelectedMailbox = account.mailboxes[max(0, min(account.mailboxes.index(shownSelectedMailbox)+selection, len(account.mailboxes)-1))]
