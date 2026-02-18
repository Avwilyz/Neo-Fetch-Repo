import os
from dotenv import load_dotenv

load_dotenv(".env")

MAX_BOT = int(os.getenv("MAX_BOT", "999"))

DEVS = list(map(int, os.getenv("DEVS", "8251166328").split()))

API_ID = int(os.getenv("API_ID", "32550268"))

API_HASH = os.getenv("API_HASH", "be4e1f6bd9664aa9b597a413b80ec48b")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8547729160:AAE7mUCLZGDVUDnMMI-c1Br5cumQqXTGdcY")

OWNER_ID = int(os.getenv("OWNER_ID", "8251166328"))

BLACKLIST_CHAT = list(map(int, os.getenv("BLACKLIST_CHAT", "-1003817627155").split()))

RMBG_API = os.getenv("RMBG_API", "uJnKfiTFtdQGvRF5occP5xpG") 

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://neofetch:Dikzz_199A@cluster0.m5ay3ja.mongodb.net/ubot?retryWrites=true&w=majority")

LOGS_MAKER_UBOT = int(os.getenv("LOGS_MAKER_UBOT", "-1003760313244"))