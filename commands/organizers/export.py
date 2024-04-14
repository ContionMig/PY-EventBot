from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar, Events
from globals import globals

import time
import helpers
import datetime
import telegram
import re
import os

class Export(BaseCommands):

    state = "/export"
    alias = ["/export", "Export Attendance"]

    private_only = True
    requires_phone = True
    users_only = True
    show_command = False

    description = "Export attendees to your events"
    roles = ["event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        if not self.get_stage():
            events = globals.db.GetAllUserEvents(self.user_id)
            await self.show_data(events, 1, "Events")
            await self.reset_user(False)
            return
        

        elif self.get_stage() == "export_event":

            code = self.text
            event = globals.db.GetEventsUnsafe(code)

            if not event:
                await self.send_message("🙈 Oops! It seems like the event code you provided is incorrect and doesn't match any of our events.")
                await self.reset_user()
                return
            
            if event.user_id != self.user_id:
                await self.send_message("🙈 Oops! It seems like you are not the owner of this event.")
                await self.reset_user()
                return
            
            await self.reset_user(False)

            await self.send_message(f"📊 We're whipping up an Excel file. This might take a moment, so grab a coffee and we'll be right back! ☕⏳📁")
            path = globals.excel.ExportSingleEvent(event_id=code)
            await self.send_document(path)
            os.remove(path)

    
    async def manage_page(self, curr_page):
        events = globals.db.GetAllUserEvents(self.user_id)
        await self.show_data(events, curr_page, "Events", edit=True)

    async def button_handler(self):

        if self.button_stage == "action":

            if self.button_state == "export_all":
                await self.send_message(f"📊 We're whipping up an Excel file. This might take a moment, so grab a coffee and we'll be right back! ☕⏳📁")
                path = globals.excel.ExportSingleEvent(user_id=self.user_id)
                await self.send_document(path)
                os.remove(path)

            elif self.button_state == "export_event":
                await self.send_message("🎈 Please enter the <b><u>event code</u></b>")
                self.set_stage("export_event")
                return

    async def show_data(self, data, curr_page, list_name, edit=False):
        
        curr_list = self.get_paginated_data(data, curr_page)
        if curr_page <= 0 or curr_page > curr_list[1]:
            curr_page = 1
            curr_list = self.get_paginated_data(data, curr_page)


        msg = f"<b><u>Page {curr_page}/{curr_list[1]} - {list_name}:</u></b>\n\n"
        
        for x in curr_list[0]:
            msg += f"<code>{x.id}</code>: <b>{x.event_name}</b>\n"

        buttons = {
            self.get_button_state("action", "export_all"): "Export All 📤",
            self.get_button_state("action", "export_event"): "Export Event 🎟️",
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