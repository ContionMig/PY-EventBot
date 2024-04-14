from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

class PersistantStorage(Base):
    
    __tablename__ = 'persistant_storage'
    
    id = Column(String, primary_key=True)
    value = Column(String, default="")
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")
    
    def __str__(self):
        # Initialize an empty list to store column names and values
        columns_and_values = []

        # Loop through the columns and fetch their names and values
        for col in self.__table__.columns:
            column_name = col.name
            column_value = getattr(self, col.name)
            columns_and_values.append(f"{column_name}: {column_value}")

        # Join the list elements with line breaks to create the string
        return "\n".join(columns_and_values)

class SavedVar(Base):
    __tablename__ = 'saved_var'
    
    id = Column(String, primary_key=True)
    type = Column(String)
    var = Column(String)
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")
   
class BanList(Base):
    __tablename__ = 'ban_list'

    id = Column(String, primary_key=True)
    handle = Column(String)
    banned_by = Column(String)
    reason = Column(String)
    date = Column(String)
    number = Column(String)
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")

class RSVP(Base):
    __tablename__ = "rsvp"

    id = Column(String, primary_key=True)

    event = Column(String)
    event_name = Column(String)
    event_user_id = Column(String)
    user_id = Column(String)
    full_name = Column(String)
    nric = Column(String)
    phone = Column(String)
    office = Column(String)
    interest_level = Column(String)
    
    date = Column(DateTime(True))

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True)

    event = Column(String)
    event_name = Column(String)
    event_user_id = Column(String)
    user_id = Column(String)
    full_name = Column(String)
    nric = Column(String)
    phone = Column(String)
    office = Column(String)
    
    date = Column(DateTime(True))

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")

class Events(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)

    user_id = Column(String)

    event_name = Column(String)
    venue = Column(String)

    public = Column(String)

    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    def get_questions(self):
        questions = {
            "Event Name": "event_name",
            "Venue": "venue",
            "Public (T/F)": "public",
            "Start (DD/MM/YYYY)": "start_date",
            "End (DD/MM/YYYY)": "end_date"
        }
        return questions

    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")

class Users(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)

    full_name = Column(String)
    nric = Column(String)
    number = Column(String)
    office = Column(String)
    role = Column(String, default="user")
    
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    def valid_phone_number(self):
        number = self.get("number")
        
        if number is None:
            return False
        
        if len(number) != 10 and number[:2] != "65":
            return False
        
        return True
    
    def get(self, column_name):
        if hasattr(self, column_name):
            return getattr(self, column_name)
        return None
    
    def set(self, col_name, value):
        if hasattr(self, col_name):
            setattr(self, col_name, value)
        else:
            raise AttributeError(f"Column '{col_name}' not found in model.")
