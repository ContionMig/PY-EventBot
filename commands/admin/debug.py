from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import psutil
import time

import helpers

class Debug(BaseCommands):

    state = "/debug"
    alias = ["/debug"]

    private_only = False
    requires_phone = True
    users_only = True
    show_command = False

    roles = ["admin"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        chat = update.message.chat

        # Get system stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent

        # Create a debug message
        debug_message = f"<b><u>Debug Info:</u></b>\n\n"
        debug_message += f"<b>Chat Title</b>: {chat.title}\n"
        debug_message += f"<b>Chat ID</b>: {chat.id}\n"
        debug_message += f"<b>Message ID</b>: {update.message.message_id}\n"
        debug_message += f"<b>Message Thread ID</b>: {update.effective_message.message_thread_id}\n"
        debug_message += f"<b>Is Topic</b>: {update.effective_message.is_topic_message}\n\n"
        debug_message += f"<b><u>Server Stats:</u></b>\n"
        debug_message += f"<b>CPU Usage</b>: {cpu_percent}%\n"
        debug_message += f"<b>Memory Usage</b>: {memory_percent}%"
        
        if self.chat_id == globals.developer:
            debug_message += f"\n\n<b>IP</b>: {helpers.helper.get_public_ip()}"

        await self.send_message(debug_message, html=True)
        await self.reset_user(False)