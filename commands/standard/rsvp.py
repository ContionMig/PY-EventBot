from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import time
import helpers
import datetime
import telegram

class RSVP(BaseCommands):

    state = "/rsvp"
    alias = ["/rsvp", "Event RSVP"]

    private_only = True
    requires_phone = True
    users_only = True
    show_command = True

    description = "Show your interest in an event"
    roles = ["user", "event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        if not self.get_stage():

            await self.send_message("""📝 <b><u>Event RSVP</u></b> 📝

To take your RSVP for an event, please enter the <b><u>event code</u></b> associated with the event.

If you're unsure about the event code, you can always check the event details or contact the event organizer for assistance.

Let's get your RSVP recorded! 🎉""")
            
            self.set_stage("wait_code")
            return
        
        elif self.get_stage() == "wait_code":

            code = self.text
            event = globals.db.GetEventsUnsafe(code)
            today = datetime.datetime.today().date()

            if not event:
                await self.send_message("📝 <b><u>Event RSVP</u></b> 📝\n\n<b><u>Invalid Event Code</u></b> ❌\n\nOops! It seems like the event code you provided is incorrect and doesn't match any of our events.\n\nPlease double-check the code and try again. 🤔")
                await self.reset_user()
                return
            
            if today > event.end_date.date():
                await self.send_message("📝 <b><u>Event RSVP</u></b> 📝\n\nWe're sorry 🙈, but the event has ended\n\nPlease ensure that you are trying to take attendance for a event that is scheduled for the future. 😊")
                await self.reset_user()
                return

            buttons = {
                self.get_button_state("interest", "Interested"): "👍 Interested",
                self.get_button_state("interest", "Maybe"): "🤔 Maybe",
                self.get_button_state("interest", "Not Interested"): "👎 Not Interested"
            }

            self.set_var("code", code)
            await self.send_message("""📝 <b><u>Event RSVP</u></b> 📝
                                    
We're excited to hear about your interest in the event! 🌟

Please select your interest level using the options below:

👍 <b>Interested</b> - I'm looking forward to attending!
🤔 <b>Maybe</b> - I'm considering attending, but not sure yet.
👎 <b>Not Interested</b> - I won't be able to attend this time.

Your feedback helps us plan better events. 💬""", inline=self.create_buttons(buttons, 1))
            
            return
        
    async def button_handler(self):
        
        user = globals.db.GetUser(self.user_id)

        if self.button_stage == "interest":

            code = self.get_var("code")
            interest = self.button_state

            if not code:
                await self.send_message("❌ Button's session has expired, please try again!")
                await self.reset_user(False)
                return
            
            event = globals.db.GetEventsUnsafe(code)
            if not event:
                await self.send_message("❌ Button's session has expired, please try again!")
                await self.reset_user(False)
                return

            rsvp = globals.db.GetRSVP(self.user_id, code)
            rsvp.event = event.id
            rsvp.event_name = event.event_name
            rsvp.event_user_id = event.user_id
            rsvp.user_id = user.id
            rsvp.full_name = user.full_name
            rsvp.nric = user.nric
            rsvp.phone = user.number
            rsvp.office = user.office
            rsvp.interest_level = interest
            
            rsvp.date = datetime.datetime.today()

            globals.db.UpdateRSVP(rsvp)

            await self.send_message("✅ Your RSVP has been recorded successfully. 🎈")
        
        await self.reset_user()
        return



            