from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import time
import helpers
import datetime
import telegram

class View(BaseCommands):

    state = "/view"
    alias = ["/view", "View Event"]

    private_only = True
    requires_phone = True
    users_only = True
    show_command = True

    description = "Check details of a event"
    roles = ["user", "event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        if not self.get_stage():

            await self.send_message("🎈 Please enter the <b><u>event code</u></b>")
            self.set_stage("code")
            return

        elif self.get_stage() == "code":

            code = self.text
            event = globals.db.GetEventsUnsafe(code)

            if not event:
                await self.send_message("🙈 Oops! It seems like the event code you provided is incorrect and doesn't match any of our events.")
                await self.reset_user()
                return
            
            await self.send_message("""Hey there! 🌟 Here are the details for the event you're interested in:

<b><u>Event Name:</u></b> {event.event_name}
<b><u>Venue:</u></b> {event.venue}
                                    
<b><u>Start Date:</u></b> {start}
<b><u>End Date:</u></b> {end}

Feel free to reach out if you have any questions or need further information. Enjoy the event! 🎉
""".format(event=event, start=event.start_date.strftime('%d/%m/%Y'), end=event.end_date.strftime('%d/%m/%Y')))
            
            await self.reset_user()
            return
        
