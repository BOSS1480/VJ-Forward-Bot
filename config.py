from os import environ 

class Config:
    API_ID = int(environ.get("API_ID", "22558238"))
    API_HASH = environ.get("API_HASH", "41abc14dd9f760887a50f9cd2cc1bb73")
    BOT_TOKEN = environ.get("BOT_TOKEN", "") 
    BOT_SESSION = environ.get("BOT_SESSION", "vjbot") 
    DATABASE_URI = environ.get("DATABASE_URI", "mongodb+srv://y0534150646:330833039@cluster0.ysd9p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = environ.get("DATABASE_NAME", "vj-forward-bot")
    BOT_OWNER = int(environ.get("BOT_OWNER", "6335855540"))


class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
