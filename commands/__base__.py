from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from structs.model import Base, BanList, Users, SavedVar
from globals import globals

import telegram
import random
import datetime
import string

import pytz
import helpers

class BaseCommands:

    state = "NO_COMMAND"
    alias = []

    description = ""

    show_command = True

    update = None
    username = ""
    user = None

    private_only = True
    commands = []

    requires_phone = True
    users_only = True
    
    dont_edit_message = False

    roles = ["user"]

    def __init__(self, update=None, context=None, commands=[]) -> None:
        self.commands = commands
        self.setup_variables(update, context)

    def setup_variables(self, update, context,):
        try:
            self.update = update
            self.context = context

            self.username = update.effective_user.username

            self.user_id = str(update.effective_user.id)
            self.chat_id = str(update.effective_chat.id)

            self.text = str(update.effective_message.text).strip()
            self.thread_id = str(update.effective_message.message_thread_id)

            self.user = globals.db.GetUser(self.user_id)

        except:
            pass

    async def callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        self.username = str(update.effective_user.username)
        self.text = str(update.effective_message.text).strip()
        self.chat_id = str(update.effective_chat.id)
        self.user_id = str(update.effective_user.id)

        self.update = update

        if self.private_only and update.effective_chat.type.upper() != "PRIVATE":
            return

        self.user = globals.db.GetUser(self.user_id)

        if update.effective_chat.type.upper() == "PRIVATE":
            if self.requires_phone and not self.user.valid_phone_number():
                await self.request_contact()
                return
        

        self.init()
        self.set_state()

        if self.users_only and self.user and (not self.user.full_name or not self.user.nric or not self.user.office):
            await self.send_message("❌ You have not registered all your details! Please do /start and type in your details")
            return

        if self.users_only and self.user.get("role") != "admin" and not self.user.get("role") in self.roles:
            await self.send_message("❌ You do not have permission to use this command")
            return
        
        await self.handler(update, context)

    async def command_called(self, update: Update, context: ContextTypes.DEFAULT_TYPE, commands):
        
        self.commands = commands
        self.setup_variables(update, context)

        if self.text in self.alias or self.good_state(self.user_id):
            for x in commands:
                if x.state != self.state and self.text in x.alias:
                    return False

        if self.text == self.state or self.text in self.alias or self.good_state(self.user_id):
            await self.callback(update, context)
            return True

        return False

    async def document_received(self,  update: Update, context: ContextTypes.DEFAULT_TYPE, commands, file):

        self.commands = commands
        self.setup_variables(update, context)

        self.init()
       
        if self.good_state(self.user_id):
            await self.document_handler(file)

    async def button_pressed(self, query, update, context, commands):

        self.commands = commands
        if not query[:len(self.alias[0])] == self.alias[0]:
            return

        self.setup_variables(update, context)

        self.init()
        self.set_state()

        self.user = globals.db.GetUser(self.user_id)

        if update.effective_chat.type.upper() == "PRIVATE":
            if self.requires_phone and not self.user.valid_phone_number():
                await self.request_contact()
                return
        
        if self.user.get("role") != "admin" and not self.user.get("role") in self.roles:
            await self.send_message("❌ You do not have permission to use this command")
            return
            

        queries = str(query).split("|")

        self.button_stage = queries[1]
        self.button_state = queries[2]

        if self.button_stage == "previous_page":
            curr_page = int(self.button_state) - 1
            await self.manage_page(curr_page)
            return True
        
        elif self.button_stage == "next_page":
            curr_page = int(self.button_state) + 1
            await self.manage_page(curr_page)
            return True

        await self.button_handler()

        if not self.dont_edit_message:
            try:
                await context.edit_message_text(text=f"{context.message.text}")
            except telegram.error.BadRequest:
                pass

    async def manage_page(self, curr_page):
        pass

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass

    async def button_handler(self):
        pass

    async def document_handler(self, file):
        pass

    def init(self):

        self.username = str(self.update.effective_user.username)
        self.text = str(self.update.effective_message.text).strip()
        self.chat_id = str(self.update.effective_chat.id)
        self.user_id = str(self.update.effective_user.id)

        user_states = globals.db.get_user_states(self.user_id)
        globals.db.ensure_user_states_keys(user_states)

    async def reset_user(self, send_message=True, chat_id=None):
        
        user_states_dict = {}
        globals.db.update_user_states(self.user_id, user_states_dict)

        if send_message:
            buttons = []

            buttons.append([KeyboardButton("Take Attendance")])
            buttons.append([KeyboardButton("View Attendance"), KeyboardButton("Event RSVP")])
            buttons.append([KeyboardButton("View Event"), KeyboardButton("Edit Info")])
            
            
            if self.user.get("role") in ["event", "admin"]:
                buttons.append([KeyboardButton("Manage Events"), KeyboardButton("Export Attendance")])
            
            buttons.append([KeyboardButton("/cancel"), KeyboardButton("/start")])

            keyboard_reply = ReplyKeyboardMarkup(buttons,
                                             resize_keyboard=True,
                                             is_persistent=True,
                                             one_time_keyboard=False)

            if self.update.effective_chat.type.upper() == "PRIVATE" or chat_id is not None:
                await self.send_message("What else can I help you with?", keyboard_reply, True, chat_id=chat_id)

    def get_help_list(self):

        r = ""
        for command in self.commands:
            if command.show_command == True:
                r += f"🔹 {command.state} - {command.description}\n"
        return r

    #
    # STATE
    #

    def good_state(self, username):
        user_states = globals.db.get_user_states(username)  # Use the 'Database' class
        if not user_states:
            return False

        return user_states.get("command", "") == self.alias[0]

    def get_state(self):
        user_states = globals.db.get_user_states(self.user_id)  # Use the 'Database' class
        return user_states.get("command", "")

    def set_state(self):
        user_states = globals.db.get_user_states(self.user_id)  # Use the 'Database' class
        user_states["command"] = self.alias[0]
        globals.db.update_user_states(self.user_id, user_states)  # Update user states in the database

    #
    # STAGES
    #
    def set_stage(self, stage):
        user_states = globals.db.get_user_states(self.user_id)  # Use the 'Database' class
        user_states["stage"] = f"{self.alias[0]}_{stage}"
        globals.db.update_user_states(self.user_id, user_states)  # Update user states in the database

    def get_stage(self):
        user_states = globals.db.get_user_states(self.user_id)  # Use the 'Database' class
        stage = user_states.get("stage", "")
        if not stage.startswith(f"{self.alias[0]}_"):
            return None

        return stage[len(self.alias[0]) + 1:]

    #
    # VAR
    #
    def set_var(self, var, data):
        user_states = globals.db.get_user_states(self.user_id)  # Use the 'Database' class
        user_states["var"][var] = data
        globals.db.update_user_states(self.user_id, user_states)  # Update user states in the database

    def get_var(self, var):
        user_states = globals.db.get_user_states(self.user_id)  # Use the 'Database' class
        return user_states.get("var", {}).get(var)

    #
    # BUTTONS
    #
    def get_button_state(self, stage, state):
        return self.alias[0] + "|" + stage + "|" + state

    def create_keyboard(self, buttons):

        keyboards = []
        for x in dict(buttons).keys():
            keyboards.append(
                [InlineKeyboardButton(buttons[x], callback_data=x)])

        return ReplyKeyboardMarkup(keyboards)

    def create_buttons(self, buttons, division=2, last=None):

        keyboards = []
        pushup = []
        for x in dict(buttons).keys():
            
            pushup.append(InlineKeyboardButton(buttons[x], callback_data=x))
            
            if len(pushup) == division or buttons[x] == last:
                keyboards.append(pushup)
                pushup = []

        if len(pushup):
            keyboards.append(pushup)

        return InlineKeyboardMarkup(keyboards)


    #
    # SENDING MESSAGES
    #
    async def send_message(self, text, html=True, chat_id=None, inline=None, message_thread_id=None):

        if len(text) > 4090:
            text = str(text)[:4090] + "..."

        _chat_id = self.update.effective_chat.id
        
        if chat_id:
            _chat_id = chat_id

        if message_thread_id is None and self.thread_id is not None and chat_id is None:
            message_thread_id = self.thread_id

        if html:
            return await self.update._bot.send_message(_chat_id, text, reply_markup=inline, parse_mode=telegram.constants.ParseMode.HTML, message_thread_id=message_thread_id)
        else:
            return await self.update._bot.send_message(_chat_id, text, reply_markup=inline, message_thread_id=message_thread_id)

    async def send_document(self, path, caption=None, chat_id=None, html=True, inline=None, message_thread_id=None):
        document = open(path, 'rb')
        _chat_id = self.update.effective_chat.id

        if chat_id:
            _chat_id = chat_id

        if message_thread_id is None and self.thread_id is not None and chat_id is None:
            message_thread_id = self.thread_id

        try:
            if html:
                await self.update._bot.send_document(_chat_id, document, caption, reply_markup=inline, parse_mode=telegram.constants.ParseMode.HTML, message_thread_id=message_thread_id, protect_content=True)
            else:
                await self.update._bot.send_document(_chat_id, document, caption, reply_markup=inline, message_thread_id=message_thread_id, protect_content=True)

        except telegram.error.BadRequest:
            pass

    async def request_contact(self):

        con_keyboard = KeyboardButton(
            text="📞 Share Phone Number", request_contact=True)

        custom_keyboard = [[con_keyboard]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)

        await self.update._bot.send_message(self.update.effective_chat.id,
                                            text="""🔒 Your privacy is important to us!\n\nTo ensure a safe and spam-free experience, we kindly ask for your phone number""",
                                            reply_markup=reply_markup)


    def random_char(self, y):
        return ''.join(random.choice(string.ascii_letters) for x in range(y))

    def get_paginated_data(self, data_list, page_number=1, page_size=10):
        total_items = len(data_list)
        max_page = (total_items + page_size - 1) // page_size

        start_index = (page_number - 1) * page_size
        end_index = min(page_number * page_size, total_items)

        paginated_data = data_list[start_index:end_index]

        return paginated_data, max_page
