from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import time
import helpers
import datetime
import telegram

class Here(BaseCommands):

    state = "/here"
    alias = ["/here", "Take Attendance"]

    private_only = True
    requires_phone = True
    users_only = True
    show_command = True

    description = "Take your attendance"
    roles = ["user", "event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        if not self.get_stage():

            await self.send_message("""📝 <b><u>Attendance Check-in</u></b> 📝

To take your attendance for an event, please enter the <b><u>event code</u></b> associated with the event you're attending.

If you're unsure about the event code, you can always check the event details or contact the event organizer for assistance.

Let's get your attendance recorded! 🎉""")
            
            self.set_stage("wait_code")
            return
        
        elif self.get_stage() == "wait_code":

            code = self.text
            event = globals.db.GetEventsUnsafe(code)
            today = datetime.datetime.today().date()

            if not event:
                await self.send_message("📝 <b><u>Attendance Check-in</u></b> 📝\n\n<b><u>Invalid Event Code</u></b> ❌\n\nOops! It seems like the event code you provided is incorrect and doesn't match any of our events.\n\nPlease double-check the code and try again. 🤔")
                await self.reset_user()
                return
            
            if today < event.start_date.date() or today > event.end_date.date():
                await self.send_message("📝 <b><u>Attendance Check-in</u></b> 📝\n\nWe're sorry 🙈, but the event isn't hosted today\n\nPlease ensure that you are trying to take attendance for a event that is scheduled for today. 😊")
                await self.reset_user()
                return

            buttons = {
                self.get_button_state("confirm", "-"): "✅ Confirm",
                self.get_button_state("cancel", "-"): "❌ Cancel"
            }

            self.set_var("date", today.strftime("%d/%m/%Y"))
            self.set_var("code", code)

            await self.send_message("""📝 <b><u>Attendance Check-in</u></b> 📝

Are you sure you want to confirm your attendance for this event?

<b><u>Event:</u></b> <code>{event.event_name}</code>
<b><u>Event Code:</u></b> <code>{event.id}</code>

Please double-check that you're attending the correct event before confirming your attendance. 😊""".format(event=event), inline=self.create_buttons(buttons))
    

    async def button_handler(self):
        
        user = globals.db.GetUser(self.user_id)

        if self.button_stage == "confirm":
            
            date = self.get_var("date")
            code = self.get_var("code")

            if not date or not code:
                await self.send_message("❌ Button's session has expired, please try again!")
                await self.reset_user(False)
                return
            
            event = globals.db.GetEventsUnsafe(code)
            if not event:
                await self.send_message("❌ Button's session has expired, please try again!")
                await self.reset_user(False)
                return

            attendance = globals.db.GetAttendance(date, self.user_id, code)
            attendance.event = event.id
            attendance.event_name = event.event_name
            attendance.event_user_id = event.user_id
            attendance.user_id = user.id
            attendance.full_name = user.full_name
            attendance.nric = user.nric
            attendance.phone = user.number
            attendance.office = user.office
            attendance.date = datetime.datetime.today()

            globals.db.UpdateAttendance(attendance)

            await self.send_message("✅ Your attendance has been recorded successfully. 🎈")
        
            

        elif self.button_stage == "cancel":
            await self.send_message("❌ Your action has been cancelled!")

        await self.reset_user()
        return
            
