import logging
import time
from pymongo import MongoClient
from Abg import patch
from nexichat.userbot.userbot import Userbot
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import ChatMemberUpdatedHandler
from pyrogram.types import ChatMemberUpdated
import config
import uvloop

# Initialize logging
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

# Initialize MongoDB
mongodb = MongoCli(config.MONGO_URL)
db = mongodb.Anonymous
mongo = MongoClient(config.MONGO_URL)
mongodb = mongo.VIP

# Global variables
ID_CHATBOT = None
SUDOERS = filters.user()
CLONE_OWNERS = {}
uvloop.install()
boot = time.time()
clonedb = None

def dbb():
    global db, clonedb
    clonedb = {}
    db = {}

def sudo():
    global SUDOERS
    OWNER = config.OWNER_ID
    if config.MONGO_URL is None:
        SUDOERS.add(OWNER)
    else:
        sudoersdb = mongodb.sudoers
        sudoers = sudoersdb.find_one({"sudo": "sudo"})
        sudoers = [] if not sudoers else sudoers["sudoers"]
        SUDOERS.add(OWNER)
        if OWNER not in sudoers:
            sudoers.append(OWNER)
            sudoersdb.update_one(
                {"sudo": "sudo"},
                {"$set": {"sudoers": sudoers}},
                upsert=True,
            )
        if sudoers:
            for x in sudoers:
                SUDOERS.add(x)
    LOGGER.info("Sudoers Loaded.")

# Initialize sudoers
sudo()

class NexiChat(Client):
    def __init__(self):
        super().__init__(
            name="nexichat",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.DEFAULT,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        # Register event handlers
        self.add_handler(ChatMemberUpdatedHandler(self.user_joined, filters.chat_member_updated.new_chat_members))
        self.add_handler(ChatMemberUpdatedHandler(self.user_left, filters.chat_member_updated.left_chat_member))
        LOGGER.info("Event handlers for user join and leave registered successfully.")

    async def stop(self):
        await super().stop()

    async def user_joined(self, client: Client, chat_member_updated: ChatMemberUpdated):
        for member in chat_member_updated.new_chat_members:
            LOGGER.info(f"New member joined: {member.mention}")
            bio = (await client.get_users(member.id)).bio
            welcome_message = (
                "🎉🎉🎉🎉🎉🎉🎉🎉🎉\n\n"
                f"🌟 Welcome {member.mention} 🌟\n\n"
                f"👤 Name: {member.first_name} {member.last_name or ''}\n"
                f"🔗 Username: @{member.username}\n"
                f"📜 Bio: {bio or 'No bio available'}\n\n"
                "🎉🎉🎉🎉🎉🎉🎉🎉🎉"
            )
            try:
                await client.send_message(
                    chat_id=chat_member_updated.chat.id,
                    text=welcome_message
                )
                LOGGER.info(f"Welcome message sent to {member.mention}")
            except Exception as e:
                LOGGER.error(f"Failed to send welcome message: {e}")

    async def user_left(self, client: Client, chat_member_updated: ChatMemberUpdated):
        member = chat_member_updated.left_chat_member
        LOGGER.info(f"Member left: {member.mention}")
        bio = (await client.get_users(member.id)).bio
        goodbye_message = (
            "👋👋👋👋👋👋👋👋👋\n\n"
            f"💔 Goodbye {member.mention} 💔\n\n"
            f"👤 Name: {member.first_name} {member.last_name or ''}\n"
            f"🔗 Username: @{member.username}\n"
            f"📜 Bio: {bio or 'No bio available'}\n\n"
            "👋👋👋👋👋👋👋👋👋"
        )
        try:
            await client.send_message(
                chat_id=chat_member_updated.chat.id,
                text=goodbye_message
            )
            LOGGER.info(f"Goodbye message sent to {member.mention}")
        except Exception as e:
            LOGGER.error(f"Failed to send goodbye message: {e}")

# Start the bot
nexichat = NexiChat()
userbot = Userbot()

if __name__ == "__main__":
    nexichat.run()
