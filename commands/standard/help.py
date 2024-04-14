from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import time


class Help(BaseCommands):

    state = "/help"
    alias = ["/help", "Command List"]

    private_only = True
    requires_phone = False
    users_only = False
    show_command = True
    
    description = "Get assistance and learn more about the bot"
    roles = ["user", "event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        await self.send_message(f"Explore the commands:\n{self.get_help_list()}")
        await self.reset_user()
