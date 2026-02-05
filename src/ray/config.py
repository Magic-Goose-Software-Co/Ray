from os.path import expanduser
from pathlib import Path

from dotenv import load_dotenv
from rich import console

saveDir = Path(expanduser("~"), '.ray').resolve()
console = console.Console()

load_dotenv(saveDir / '.env')
