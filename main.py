from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import Defaults

import asyncio
import datetime
import telegram
import threading
import time
from globals import globals

from structs.model import Base, BanList, Users, SavedVar

# commands
from commands.standard.attendance import Attendance
from commands.standard.here import Here
from commands.standard.view import View
from commands.standard.rsvp import RSVP

from commands.standard.start import Start
from commands.standard.help import Help

from commands.organizers.manage_event import ManageEvent
from commands.organizers.export import Export

from commands.admin.debug import Debug

from commands.__base__ import BaseCommands
import inspect
import traceback

from database import database

class EventsTracker:

    commands = []

    def __init__(self) -> None:

        df = Defaults(block=False)
        self.app = ApplicationBuilder().token(globals.token).read_timeout(300).write_timeout(300).pool_timeout(300).connect_timeout(300).defaults(df).build()
        self.add_handler()

        commands = self.setup_commands()
        for command in commands:
            print(f"{command.alias[0].replace('/', '')} - {command.description} {command.roles}")

        print("# Done __init__")

    def run(self):
        print("# FINISHED STARTING THREADS")
        self.app.run_polling()

    def setup_commands(self):

        commands = []
        commands.append(Start())
        commands.append(Help())
        commands.append(Debug())

        commands.append(Attendance())
        commands.append(Here())
        commands.append(View())
        commands.append(RSVP())

        commands.append(ManageEvent())
        commands.append(Export())

        return commands

    async def handle_errors(self, e, username, content, update: Update):

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        error_message = f"‼️ <b>Error @ <u>{timestamp}</u></b> ‼️\n\n"
        error_message += f"<b><u>Error Type:</u></b> {type(e).__name__}\n"
        error_message += f"<b><u>Error Details:</u></b> {str(e)}\n\n"
        error_message += f"<b><u>Triggerred By:</u></b> @{username}\n"
        error_message += f"<b><u>Content:</u></b> {content}"

        long_message = error_message + f"\n\n<b><u>Traceback:</u></b>\n{str(traceback.format_exc())}"
        
        if len(long_message) > 4000:
            long_message = long_message[:3999]
        
        await self.update._bot.send_message(globals.developer, long_message, parse_mode=telegram.constants.ParseMode.HTML)
        await self.update._bot.send_message(globals.db.GetPersistantStorage("error_logs"), error_message, parse_mode=telegram.constants.ParseMode.HTML, message_thread_id=globals.db.GetPersistantStorage("error_thread_id"))
        await self.update._bot.send_message(update.effective_user.id, "‼️ Oh no! There has been an internal error. The error report has been sent to the programmers, please try again later.")
    

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        self.update = update
        self.context = context

        if update.effective_user.is_bot == True:
            return

        commands = self.setup_commands()

        msg = update.effective_message
        text = msg.text
        username = update.effective_user.username
        user_id = str(update.effective_user.id)
        
        print(f"[{user_id}] {username}: {text}")
        
        start_cmd = Start(update, context, commands)

        if globals.db.ExistBan(user_id):
            check_ban = globals.db.GetBan(user_id)
            await update.message.reply_text("🚫 We're sorry, but it appears that your account has been flagged and banned from our services due to a violation of bot's guidelines and policies.\n\n" +
                                            f"The reason for the ban: {check_ban.get('reason')}\n\n" +
                                            "If you believe this is a mistake, please reach out to our customer support team for further assistance.\n\n" +
                                            "We take security and integrity of our community seriously and appreciate your understanding. 🙏")
                                            
            return

        try:
            if text == "/cancel":
                await start_cmd.reset_user()
                return

            #
            # HANDLE SINGLE COMMANDS
            #
            for command in commands:
                if await command.command_called(update, context, commands):
                    return
            
            if update.effective_chat.type.upper() == "PRIVATE":
                await start_cmd.send_message(f"😔 Unknown command! Use the commands below:\n\n{start_cmd.get_help_list()}")
                
            await start_cmd.reset_user(False)
            return

        except Exception as e:
            await self.handle_errors(e, username, text, update)

    async def buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        self.update = update
        self.context = context

        query = update.callback_query
        await query.answer()

        commands = self.setup_commands()
        username = update.effective_user.username
        user_id = str(update.effective_user.id)

        print(f"[{user_id}] {username}: {query.data}")
        
        try:
            for command in commands:
                await command.button_pressed(query.data, update, query, commands)

        except Exception as e:
            await self.handle_errors(e, username, query.data, update)

    async def contact_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        self.update = update
        self.context = context

        phone = update.effective_message.contact.phone_number
        con_user_id = str(update.effective_message.contact.user_id) 
        
        phone = phone.replace("+", "")

        if str(con_user_id) != str(update.effective_user.id):
            await update.message.reply_text("⚠️ Oops! It seems that the phone number you provided may have been used by someone else in our system.")
            return

        if len(phone) < 5:
            await update.message.reply_text("⚠️ Oops! It seems that the phone number is invalid!")
            return

        if globals.db.GetUserNumber(phone):
            await update.message.reply_text("⚠️ Oops! It seems that the phone number has already been used before!")
            return

        user = globals.db.GetUser(con_user_id)
        user.set("number", phone)

        globals.db.UpdateUser(user)
        await update.message.reply_text("✅ Great news! Your phone number has been successfully updated in our system. Thank you for your cooperation.")
        await Start(update, context).handler(update, context)

    async def file_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        self.update = update
        self.context = context

        user_id = str(update.effective_user.id)
        commands = self.setup_commands()
        username = update.effective_user.username
        msg = update.effective_message
        
        print(f"[{user_id}] {username}: <document>")

        file = None

        if msg.photo:
            file = await self.context.bot.get_file(self.update.message.photo[-1].file_id)
            
        elif msg.document:
            file = await self.context.bot.get_file(self.update.message.document.file_id)
        
        elif msg.voice:
            file = await self.context.bot.get_file(self.update.message.voice.file_id)
        
        elif msg.video:
            file = await self.context.bot.get_file(self.update.message.video.file_id)

        if not file:
            return

        try:
            for command in commands:
                await command.document_received(update, context, commands, file)

        except Exception as e:
            await self.handle_errors(e, username, "document", update)
    
    def add_handler(self):
        self.app.add_handler(CallbackQueryHandler(self.buttons))

        self.app.add_handler(MessageHandler(filters.TEXT, self.handle))
        self.app.add_handler(MessageHandler(filters.CONTACT, self.contact_callback))
        self.app.add_handler(MessageHandler(filters.ATTACHMENT, self.file_callback))
    


bot = EventsTracker()
bot.run()
