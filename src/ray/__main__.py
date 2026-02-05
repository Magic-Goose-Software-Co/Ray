import json
from datetime import datetime

from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .config import saveDir, console
from . import load
from . import mail
from . import sort


def runApp():
    with console.status("[bold] Starting Ray... [/bold]", spinner="bouncingBar"):
        config = load.getConfig()
        account = mail.Account(config["address"], load.getPassword(), config["server"])

        notFoundMailboxes = list(set(config["mailboxes"]) - set(account.mailboxes))
        for mailbox in notFoundMailboxes:
            console.log(f"[red][ERROR] Expected mailbox \"{mailbox}\" was not found.[/red]")
        if len(notFoundMailboxes) != 0:
            exit()

        for mailbox in list(set(account.mailboxes) - set(config["mailboxes"])):
            console.log(f"[dim][INFO] Mailbox \"{mailbox}\" will not be a sort destination.[/dim]")

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

        # Check if we have training data
        totalEmails = sum(len(emails) for emails in trainingMail.values())
        if totalEmails == 0:
            console.log(
                "[yellow][INFO] No training data available yet. Please add emails to your configured mailboxes and run Ray again.[/yellow]")
            account.logout()
            return

    model = sort.Model(trainingMail)

    if config["sortType"] == "subject":
        sortFunc = model.sortBySubject
    elif config["sortType"] == "sender":
        sortFunc = model.sortBySender
    else:
        console.log(f"[red][ERROR] Unknown sort type \"{config['sortType']}\" in configuration.[/red]")
        account.logout()
        return

    inbox_emails = account.getMail("INBOX", lastRun)
    # rich progress bar
    if inbox_emails:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )

        with Live(progress, console=console, refresh_per_second=10):
            task = progress.add_task("Sorting emails", total=len(inbox_emails))

            for email in inbox_emails:
                progress.update(task, description=f"Sorting \"{email['subject'][:50]}...\"")
                destination = sortFunc(email)
                account.moveEmail(email["uid"], "INBOX", destination)
                trainingMail.setdefault(destination, []).append(email)
                console.log(
                    f"[light_blue][INFO] Moved \"[green]{email['subject']}[/green]\" (sender \"[green]{email['sender']}[/green]\") to \"[green]{destination}[/green]\".[/light_blue]")
                progress.advance(task)
    else:
        console.print("[yellow]No new emails found, ending execution.[/yellow]")
        account.logout()
        return

    with (saveDir / "emails.json").open("w") as emailsFile:
        json.dump({"lastRun": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "emails": trainingMail}, emailsFile,
                  indent=4)
    console.print("[green]Sorting complete & training data saved.[/green]")
    account.logout()
