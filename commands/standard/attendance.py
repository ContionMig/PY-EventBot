from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import time
import helpers
import datetime
import telegram

class Attendance(BaseCommands):

    state = "/attendance"
    alias = ["/attendance", "View Attendance"]

    private_only = True
    requires_phone = True
    users_only = True
    show_command = True

    description = "Check your attendance history"
    roles = ["user", "event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        if not self.get_stage():
            
            events = globals.db.GetAllUserAttendance(self.user_id)
            await self.show_data(events, 1, "Past Events")
            await self.reset_user(False)
            return

    async def manage_page(self, curr_page):
        events = globals.db.GetAllUserAttendance(self.user_id)
        await self.show_data(events, curr_page, "Past Events", edit=True)

    async def show_data(self, data, curr_page, list_name, edit=False):
        
        curr_list = self.get_paginated_data(data, curr_page)
        if curr_page <= 0 or curr_page > curr_list[1]:
            curr_page = 1
            curr_list = self.get_paginated_data(data, 1)


        msg = f"<b><u>Page {curr_page}/{curr_list[1]} - {list_name}:</u></b>\n\n"
        
        for x in curr_list[0]:
            msg += f"[{x.date.strftime('%d/%m/%Y')}]: <b>{x.event_name}</b>\n"

        buttons = {
            self.get_button_state('previous_page', f'{curr_page}'): f"<",
            self.get_button_state('next_page', f'{curr_page}'): f">",
        }

        if edit:
            try:
                await self.context.edit_message_text(text=msg, parse_mode=telegram.constants.ParseMode.HTML, reply_markup=self.create_buttons(buttons))
            except telegram.error.BadRequest:
                pass
        else:
            await self.send_message(text=msg, html=True, inline=self.create_buttons(buttons))
        
        await self.reset_user(False)