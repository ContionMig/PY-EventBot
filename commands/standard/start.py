from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from commands.__base__ import BaseCommands

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import time
import helpers
import datetime
import telegram

class Start(BaseCommands):

    state = "/start"
    alias = ["/start", "Edit Info"]

    private_only = True
    requires_phone = False
    users_only = False
    show_command = True

    description = "Register your details"
    roles = ["user", "event"]

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        if not self.user.get("number"):
            await self.request_contact()
            return

        if not self.get_stage():
            
            await self.send_message("""🎉 <b><u>Welcome to the Event Bot!</u></b> 🎉

👋 Hello there! We're thrilled to have you join us. With our bot, keeping track of your event attendance has never been easier!

Here's what you can do with our bot:

📅 View the details for an event
🔔 Submit your attendance for an event
📝 View your attendance history.
✅ RSVP to events you're planning to attend.

To get started, simply your information or explore the commands using the menu below.

{help}
Let's make attending events a breeze together! 🌟""".format(help=self.get_help_list()))

            if self.user.full_name and self.user.nric and self.user.office:
                self.set_var("use_db", "yes")
                
                buttons = {
                    f"{self.get_button_state('final', 'edit')}": f"Edit Info",
                    f"{self.get_button_state('final', 'cancel')}": f"Cancel",
                }

                await self.send_message(f"Please <b><u>validate</u></b> the information you have entered!\n\n" +
                                            f"🪪 <b><u>Name:</u></b> {self.user.full_name}\n" +
                                            f"✍🏻 <b><u>NRIC:</u></b> {self.user.nric}\n" +
                                            f"🪖 <b><u>Office:</u></b> {self.user.office}\n", self.create_buttons(buttons), html=True)

                self.set_stage("wait")
                return

            await self.send_message("🪪 Please enter your Name (e.g. Xavier Tan)")
            self.set_stage("enter_name")
            return

        elif self.get_stage() == "enter_name":
            
            self.set_var("use_db", "no")
            self.set_var("full_name", self.text)
            
            await self.send_message("🪖 Please enter your Office")
            self.set_stage("enter_office")
            return

        elif self.get_stage() == "enter_office":
            
            self.set_var("office", self.text)
            
            await self.send_message("✍🏻 Please enter the last 4 characters of your NRIC (e.g. 844C)")
            self.set_stage("enter_nric")
            return

        elif self.get_stage() == "enter_nric":
            
            if not globals.helper.ValidNRIC(self.text):
                await self.send_message("✍🏻 Please enter the last 4 characters of your NRIC (e.g. 844C)")
                return

            self.set_var("nric", self.text)

            buttons = {
                f"{self.get_button_state('final', 'confirm')}": f"Confirm",
                f"{self.get_button_state('final', 'cancel')}": f"Cancel",
            }

            full_name = self.get_var('full_name')
            nric = self.get_var('nric')
            office = self.get_var('office')

            await self.send_message(f"Please <b><u>validate</u></b> the information you have entered!\n\n" +
                                        f"🪪 <b><u>Name:</u></b> {full_name}\n" +
                                        f"✍🏻 <b><u>Appointment:</u></b> {nric}\n" +
                                        f"🪖 <b><u>Office:</u></b> {office}\n", self.create_buttons(buttons), html=True)

            self.set_stage("wait")
            return
            
    
    async def button_handler(self):

        user = globals.db.GetUser(self.user_id)

        if self.button_stage == "final":

            self.dont_edit_message = True
            
            if self.button_state == "confirm":
                
                if self.get_var("use_db") == "no":
                    user.set("full_name", self.get_var('full_name').upper())
                    user.set("nric", self.get_var('nric').upper())
                    user.set("office", self.get_var('office'))

                    if not user.get("role"):
                        user.set("role", "user")

                    globals.db.UpdateUser(user)
                

                try:
                    await self.context.edit_message_text(text=f"🎉 Welcome to our Attendance Tracker Bot! 🎉\n\nCongratulations! 🥳 You have successfully registered with our bot. We're excited to have you on board!")
                except telegram.error.BadRequest:
                    pass

                await self.reset_user()
                return
            
            elif self.button_state == "edit":

                try:
                    await self.context.edit_message_text(text=f"📝 You may edit your details below")
                except telegram.error.BadRequest:
                    pass

                await self.send_message("🪪 Please enter your Full Name (e.g. Xavier Tan)")
                self.set_stage("enter_name")
                return
            
            elif self.button_state == "cancel":
                try:
                    await self.context.edit_message_text(text=f"🤖 Action has been cancelled!")
                except telegram.error.BadRequest:
                    pass
            
            await self.reset_user()