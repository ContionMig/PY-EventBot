from database import database
from helpers import Helper
from excel import Excel
import os

class globals_class:

    def __init__(self) -> None:
        self.dump_path = os.getcwd() + "/database/"
        self.token = "<FILL ME>"
        self.db = database(self.dump_path)
        self.excel = Excel(self.dump_path, self)
        self.helper = Helper()
        self.commands = []
        self.developer = "<telegram user id>"


globals = globals_class()
