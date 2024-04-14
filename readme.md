# Event Bot

This is a mini project for a simple Telegram bot that keeps track of user's attendance for in-house events. The bot uses python-telegram-bot library for handling Telegram's APIs and SQLAlchemy for its databases. The code is really messy and hacked together within a short period of time, but it's easy enough to get a quick bot up and running with basic functionalities.

## Installation

To install and run the Event Bot locally, follow these steps:

1. Clone the repository:
2. Navigate to the project directory:
```bash
cd event-bot
```

3. Install dependencies using pip:
```bash
pip install -r requirements.txt
```

4. Configure the bot as described in the section below.

5. Run the bot:
```bash
python main.py
```

## Welcome Message
🎉 **Welcome to the Event Bot!** 🎉

👋 Hello there! We're thrilled to have you join us. With our bot, keeping track of your event attendance has never been easier!

Here's what you can do with our bot:

📅 View the details for an event  
🔔 Submit your attendance for an event  
📝 View your attendance history  
✅ RSVP to events you're planning to attend  

To get started, simply provide your information or explore the commands using the menu below.

Let's make attending events a breeze together! 🌟

## Commands
- `/start` - Register your details
- `/help` - Get assistance and learn more about the bot
- `/debug` - Displays server stats and chat details (admin only)
- `/attendance` - Check your attendance history
- `/here` - Take your attendance
- `/view` - Check details of an event
- `/rsvp` - Show your interest in an event
- `/manage_event` - Manage your events
- `/export` - Export attendees to your events

## File Structure
```
└───event
    │   database.py
    │   excel.py
    │   globals.py
    │   helpers.py
    │   main.py
    │   requirements.txt
    │
    ├───commands
    │   │   base.py
    │   │
    │   ├───admin
    │   │       debug.py
    │   │
    │   ├───organizers
    │   │       export.py
    │   │       manage_event.py
    │   │
    │   └───standard
    │           attendance.py
    │           help.py
    │           here.py
    │           rsvp.py
    │           start.py
    │           view.py
    │
    ├───database
    │   │   data.db
    │   │
    │   └───datasheets
    └───structs
            model.py
```

## Adding Commands

To add a new command, simply create a Python file in the appropriate directory under `/commands`. The structure should follow:

```python
class NewCommand(BaseCommands):
    state = "/newcommand" # Unique command
    alias = ["/newcommand"]  # Add aliases if necessary

    description = "" # Details shown when doing /help
    show_command = True # Whether to show the command in /help

    private_only = True # Limit command to DMs only

    requires_phone = True # Requires users to share their phone number
    users_only = True # Limit command to registered users
    
    dont_edit_message = False # Automatically remove buttons from messages
    roles = ["user", "event"]  # Specify roles allowed to use the command
    
    # This method is meant to deal with text messages
    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # Implement your command logic here
        pass
    
    # This method is meant to deal with button presses
    async def button_handler(self):
        # Implement your button logic here
        # These two saved data is set by self.get_button_state(stage, state) 
        # when creating buttons
        stage = self.button_stage
        state = self.button_state
        pass
        
    # This method is used for pages
    async def show_data(self, data, curr_page, list_name, edit=False):
        pass
        
    # This method is to handle next/prev pages button presses
    async def manage_page(self, curr_page):
        pass
```

Replace `NewCommand` with your desired command name and update the class attributes accordingly.

### Using `get_stage()` and `set_var()`

These methods are helpful when you need to maintain the state and store temporary data during the user interaction with your bot.

Example:
```python
# Inside your command handler method
async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stage = self.get_stage()  # Get the current stage of the command
    if stage == "some_stage":
        data = self.get_var("some_data")  # Get temporary data stored
        # Do something with the data
    else:
        # Set the stage and store temporary data
        self.set_stage("some_stage")
        self.set_var("some_data", "some_value")
        # Proceed with the command logic
```

### Using `get_button_state()`

This method helps in generating unique button states for handling button callbacks in your bot.

Example:
```python
# Inside your command handler method
button_state = self.get_button_state("some_stage", "some_state")
# Use the button_state when creating inline buttons
```

### Using `create_buttons()`

This method simplifies the creation of inline keyboard buttons for your bot.

Example:
```python
# Inside your command handler method
buttons = {
    self.get_button_state("confirm", "-"): "✅ Confirm",
    self.get_button_state("cancel", "-"): "❌ Cancel"
}

inline_keyboard = self.create_buttons(buttons)
# Send message with the created inline keyboard
await self.send_message("Choose an option:", inline=inline_keyboard)
```

### Using `reset_user(send_message=True, chat_id=None)`

This method resets a user's saved states, stages, variables from the database.

Example:
  ```python
  # Resetting user state and sending a message
  await self.reset_user()
  ```
### Using Pages and Buttons

The provided command `Export` utilizes pages and buttons to manage exporting attendance data.

Showing the page:
```python
if not self.get_stage():
    events = globals.db.GetAllUserEvents(self.user_id)
    await self.show_data(events, 1, "Events")
    await self.reset_user(False)
    return
```

Managing next/prev buttons
```python
async def manage_page(self, curr_page):
    events = globals.db.GetAllUserAttendance(self.user_id)
    await self.show_data(events, curr_page, "Past Events", edit=True)
```

Displaying the data for the pages:
```python
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
```

This method `show_data` displays paginated data with navigation buttons for exporting attendance information. It demonstrates how to generate dynamic buttons based on the current page and handle pagination for large datasets.

This example illustrates how to effectively utilize pages and buttons in your Telegram bot commands.
### Other Useful Methods:

- `init()`: Initializes command-related variables.
- `send_message(text, html=True, chat_id=None, inline=None, message_thread_id=None)`: Sends a message to the chat.
- `send_document(path, caption=None, chat_id=None, html=True, inline=None, message_thread_id=None)`: Sends a document to the chat.
- `request_contact()`: Requests the user to share their phone number.
- `random_char(y)`: Generates a random string of length `y`.
- `get_paginated_data(data_list, page_number=1, page_size=10)`: Paginates data for displaying.

These methods provide a foundation for creating custom commands and managing user interactions within your Telegram bot. You can utilize them to build upon the existing functionality and tailor it to your specific requirements.

These methods, along with other helper methods provided in the `BaseCommands` class, can assist in creating new commands. Feel free to customize and expand upon these examples based on your specific bot requirements.

### Adding a Custom Model in `model.py`

1. **Define Your Model Class**: Create a new class that represents your database table. Ensure it inherits from `Base` provided by `declarative_base()`. Define the necessary columns using SQLAlchemy's `Column` class.

Example:
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class CustomModel(Base):
    __tablename__ = 'custom_table'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    # Define other columns as needed
```

2. **Add Methods (Optional)**: You can add methods to your model class to perform custom operations on the data associated with the model.

Example:
```python
class CustomModel(Base):
    # Existing class definition...

    def custom_method(self, param):
        # Custom logic goes here
        pass
```

### Adding Custom Methods in `database.py`

1. **Define Your Methods**: Define methods within your `database` class to interact with the database table associated with your custom model. These methods typically perform CRUD operations (Create, Read, Update, Delete) on the database.

Example:
```python
from model import CustomModel

class database:
    # Existing class definition...

    def add_custom_data(self, data):
        # Create a new instance of your custom model
        custom_obj = CustomModel(name=data['name'], age=data['age'])
        # Add the instance to the database session
        self.session.add(custom_obj)
        # Commit the transaction
        self.commit()

    def get_custom_data_by_id(self, id):
        # Retrieve a specific record from the database based on its ID
        return self.session.query(CustomModel).filter_by(id=id).first()

    # Define other CRUD methods as needed...
```

2. **Use Custom Model Methods**: You can also use custom methods defined within your model class directly from instances of that model.

Example:
```python
# Get an instance of CustomModel
custom_instance = database.get_custom_data_by_id(1)
# Use the custom method defined in CustomModel
custom_instance.custom_method(param)
```

By following these steps, you can add your own custom models and methods to your Python application's database layer. Ensure that your model and database classes are properly configured and interact with each other effectively.

### Understanding Global Variables

In `globals.py`, the `globals_class` contains various global variables such as `dump_path`, `token`, `db`, `excel`, `helper`, `commands`, and `developer`. These variables are initialized when the `globals` object is instantiated.

- `dump_path`: Specifies the directory path for storing database dumps.
- `token`: Represents the API token required for accessing the Telegram Bot API.
- `db`: Instance of the `database` class, allowing interaction with the application's database.
- `excel`: Instance of the `Excel` class, facilitating operations related to Excel files.
- `helper`: Instance of the `Helper` class, which provides various helper functions.
- `commands`: Holds a list of commands available in the application.
- `developer`: Identifies the Telegram user ID of the developer.

### How to Use Global Variables

Users can access these global variables from any module within their Python application by importing the `globals` object from `globals.py`.

Example Usage:
```python
from globals import globals

# Accessing global variables
event = globals.db.GetEventsUnsafe(code)
app = ApplicationBuilder().token(globals.token).read_timeout(300).build()

# Example condition based on developer ID
if self.chat_id == globals.developer:
    debug_message += f"\n\n<b>IP</b>: {globals.helper.get_public_ip()}"

# Exporting data using Excel instance
path = globals.excel.ExportSingleEvent(event_id=code)
```

By referencing `globals`, you can easily access and utilize the predefined global variables throughout the application's codebase. This ensures consistency and ease of maintenance when managing configuration settings, database connections, and other shared resources.

## Docker Compose

You can run the Event Bot using Docker Compose. Follow these steps to set it up:

1. Install Docker & Docker Compose if you haven't already.
2. Create a `docker-compose.yml` file in the root directory of your project.
3. Add the following configuration to the `docker-compose.yml` file:
```yaml
version: '3'
services:
  event:
    image: python:3
    container_name: event-py
    restart: unless-stopped
    volumes:
      - ./event:/event
    command: sh -c "pip install -r /event/requirements.txt && cd /event/ && python -u main.py"
```

4. Replace `./event` with the path to your project directory if it's different.
5. Navigate to the directory containing the `docker-compose.yml` file.
6. Run the following command to start the bot:
```bash
docker-compose up -d
```

This command will build the Docker image, create a container named `event-py`, and start the bot in the background.

To stop the bot, run:
```bash
docker-compose down
```

That's it! Your Event Bot is now running in a Docker container, isolated from your local environment. You can use Docker Compose to manage the lifecycle of the bot easily.

## Requirements
```
emoji
pandas
Pillow
python-telegram-bot
XlsxWriter
SQLAlchemy
psutil
python-telegram-bot-calendar
holidays
openpyxl
```

## Contact

For support or questions about the Event Bot, please contact [contionmig@gmail.com](mailto:contionmig@gmail.com).