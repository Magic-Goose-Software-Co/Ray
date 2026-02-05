import argparse

from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from . import mail
from .config import console, saveDir


def runSetup():
    # Email Setup console.print(Panel("[bold cyan]Step1: Email Configuration[/bold cyan]", title="Account Setup", border_style="cyan"))
    address = Prompt.ask("[cyan]What is your email address?[/cyan]")

    console.print()
    password = Prompt.ask(
        "[cyan]What is your password?[/cyan]\n[dim](Some mail servers such as iCloud and Gmail require this to be an \"App Specific Password\")[/dim]",
        password=True)

    console.print()
    server = Prompt.ask("[cyan]What is the IMAP server?[/cyan]")

    # Mailbox Setup console.print()
    console.print(Panel("[bold yellow]Step2: Mailbox Setup[/bold yellow]", title="Mailbox Configuration",
                        border_style="yellow"))
    console.print(
        "[dim]You should now create any mailboxes you will want Ray to move emails to (if you haven't already done so).[/dim]")
    Prompt.ask("[cyan]Press return when you have created them[/cyan]")

    account = mail.Account(address, password, server)

    mailboxes = []
    console.print("\n[bold]Select mailboxes for Ray to manage:[/bold]")
    for mailbox in account.mailboxes:
        if Prompt.ask(f"[cyan]{mailbox}[/cyan]", choices=["y", "n"], default="n") == "y":
            mailboxes.append(mailbox)

    # Sort Configuration
    console.print(Panel("[bold yellow]Step3: Sort Configuration[/bold yellow]", title="Sort Type",
                        border_style="yellow"))
    console.print("[dim]Ray can sort emails based on the sender or subject line.[/dim]")
    sortType = Prompt.ask(
        "[cyan]Sort by[/cyan]",
        choices=["sender", "subject"],
        default="sender"
    ).lower()

    # Save Configuration
    from .load import saveConfig
    saveConfig(address, server, password, mailboxes, sortType)
    # Summary console.print()
    summary_table = Table(title="Configuration Summary", box=box.ROUNDED, show_header=False, border_style="cyan")
    summary_table.add_column("Key", style="cyan")
    summary_table.add_column("Value", style="green")
    summary_table.add_row("Email", address)
    summary_table.add_row("Server", server)
    summary_table.add_row("Mailboxes", ", ".join(mailboxes))
    summary_table.add_row("Sort Type", sortType)
    console.print(summary_table)

    console.print()
    console.print(Panel(
        "[bold green]✓ Ray is now fully configured![/bold green]\n[dim]Next time you receive an email, put it in the mailbox you would like Ray to manage. Then run: [cyan]ray[/cyan][/dim]",
        border_style="green"
    ))


def start():
    parser = argparse.ArgumentParser(description="A simple to use email sorter")

    # 2. Add arguments
    parser.add_argument("setup", nargs='?', help="Run the setup script")  # make it optional
    # 3. Parse arguments
    args = parser.parse_args()

    config_path = saveDir / "config.json"
    if not config_path.exists() or args.setup:
        runSetup()
    else:
        from . import __main__ as app
        app.runApp()
