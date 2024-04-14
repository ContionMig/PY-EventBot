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

class ManageEvent(BaseCommands):

    state = "/manage_event"
    alias = ["/manage_event", "Manage Events"]

    private_only = True
    requires_phone = True
    users_only = True
    show_command = False

    description = "Manage your events"
    roles = ["event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        if not self.get_stage():
            
            events = globals.db.GetAllUserEvents(self.user_id)
            await self.show_data(events, 1, "Events")
            await self.reset_user(False)
            return

            
        elif self.get_stage() == "create_template":

            data, err = self.get_template_data(self.text)

            if err != 0:
                await self.send_message(data)
                return
            
            event_code = self.random_char(6)

            event = globals.db.GetEvents(event_code)
            event.user_id = self.user_id

            msg, err = self.setup(data, event)
            if err != 0:
                await self.send_message(msg)
                return
        
            globals.db.UpdateEvents(event)

            await self.send_message(f"🎉 Congratulations! Your event (<code>{event_code}</code>) has been successfully created.")
            await self.reset_user()
            return
        

        elif self.get_stage() == "edit_template":

            data, err = self.get_template_data(self.text)

            if err != 0:
                await self.send_message(data)
                return
            
            event_code = self.get_var("code")

            event = globals.db.GetEvents(event_code)
            msg, err = self.setup(data, event)

            if err != 0:
                await self.send_message(msg)
                return
        
            globals.db.UpdateEvents(event)

            await self.send_message(f"🎉 Congratulations! Your event (<code>{event_code}</code>) has been successfully modified.")
            await self.reset_user()
            return
            


        elif self.get_stage() == "edit":

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
            
            self.set_var("code", code)
            msg = f"📝 <b><u>Event Modification</u></b> 📝\n\nPlease <b>fill up</b> this template and send it back:\n\nClick on template below to copy, paste and fill up in chat\n\n<b><u>📝 Template:</u></b>\n<code>"
            for x in Events().get_questions().keys():
                data = event.get(Events().get_questions()[x])
                if type(data) == datetime.datetime:
                    data = data.strftime('%d/%m/%Y')
                msg += f"{x}: {data}\n"
            msg += "</code>"
            
            await self.send_message(msg, html=True)
            self.set_stage("edit_template")


        elif self.get_stage() == "delete":
            
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
            
            globals.db.RemoveEvents(code)

            await self.send_message(f"Your event (<code>{code}</code>) has been successfully deleted.")
            await self.reset_user()
            return
            
    
    async def manage_page(self, curr_page):
        events = globals.db.GetAllUserEvents(self.user_id)
        await self.show_data(events, curr_page, "Events", edit=True)

    async def button_handler(self):

        if self.button_stage == "action":

            if self.button_state == "create":

                msg = f"📝 <b><u>Event Creation</u></b> 📝\n\nPlease <b>fill up</b> this template and send it back:\n\nClick on template below to copy, paste and fill up in chat\n\n<b><u>📝 Template:</u></b>\n<code>"
                for x in Events().get_questions().keys():
                    msg += f"{x}: \n"
                msg += "</code>"
                
                await self.send_message(msg, html=True)
                self.set_stage("create_template")

            elif self.button_state == "edit":
                
                await self.send_message("🎈 Please enter the <b><u>event code</u></b>")
                self.set_stage("edit")
                return

            elif self.button_state == "delete":
                
                await self.send_message("🎈 Please enter the <b><u>event code</u></b>")
                self.set_stage("delete")
                return
    
    def get_template_data(self, text):
        response = f"{text}\n"
        lines = response.split('\n')

        extracted_data = {}

        current_key = None
        for line in lines:
            match = re.match(r'(.*?):\s(.*?)$', line)
            if match:
                current_key, value = match.groups()
                if len(value.strip()) >= 1:
                    extracted_data[current_key.strip()] = value.strip()
            elif current_key:
                if len(line.strip()) >= 1:
                    extracted_data[current_key.strip()] += ' ' + line.strip()

        
        missing_keys = list(set(Events().get_questions().keys()) - set(list(extracted_data.keys())))

        if missing_keys:
            return f"📝 <b><u>Event Parser</u></b> 📝\n\nOops! 😅 It seems like we couldn't parse the template correctly. Please ensure that you copy and paste the template <b>exactly</b> as provided! 📝\n\n<b><u>Missing Inputs</u></b>:\n{'\n'.join(missing_keys)}", 1
        
        return extracted_data, 0
    
    def setup(self, data: dict, event: Events):
        
        for key in data.keys():
            
            data[key] = str(data[key]).strip()

            if event.get_questions()[key] == "public":
                public = data[key]
                if not public in ["F", "T"]:
                    data[key] = "F"

            elif event.get_questions()[key] == "start_date":
                start_date = data[key]
                if not helpers.helper.ValidDate(start_date):
                    return "Oops! 🙈 Please use the format 'DD/MM/YYYY' for the start date. Let's try that again! 😊", -1
                
                data[key] = datetime.datetime.strptime(start_date, "%d/%m/%Y").date()
                
            elif event.get_questions()[key] == "end_date":
                end_date = data[key]

                if not helpers.helper.ValidDate(end_date):
                    return "Oops! 🙈 Please use the format <b>'DD/MM/YYYY'</b> for the end date. Let's try that again! 😊", -1
                
                end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").date()
                if end_date < datetime.datetime.today().date():
                    return "Oops! 🙈 Please make sure the end date is set in the <b>future</b>. Let's try that again! 😊", -1

                data[key] = end_date


            event.set(event.get_questions()[key], data[key])
        
        return "", 0
    

    async def show_data(self, data, curr_page, list_name, edit=False):
        
        curr_list = self.get_paginated_data(data, curr_page)
        if curr_page <= 0 or curr_page > curr_list[1]:
            curr_page = 1
            curr_list = self.get_paginated_data(data, curr_page)


        msg = f"<b><u>Page {curr_page}/{curr_list[1]} - {list_name}:</u></b>\n\n"
        
        for x in curr_list[0]:
            msg += f"<code>{x.id}</code>: <b>{x.event_name}</b>\n"

        buttons = {
            self.get_button_state("action", "create"): "Create Event 🎉",
            self.get_button_state("action", "edit"): "Edit Event 🖊️",
            self.get_button_state("action", "delete"): "Delete Event ❌",
            self.get_button_state('previous_page', f'{curr_page}'): f"<",
            self.get_button_state('next_page', f'{curr_page}'): f">",
        }

        if edit:
            try:
                await self.context.edit_message_text(text=msg, parse_mode=telegram.constants.ParseMode.HTML, reply_markup=self.create_buttons(buttons, last="Delete Event ❌"))
            except telegram.error.BadRequest:
                pass
        else:
            await self.send_message(text=msg, html=True, inline=self.create_buttons(buttons, last="Delete Event ❌"))
        
        await self.reset_user(False)