import json
import time
import datetime

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from structs.model import Base, BanList, Users, SavedVar, PersistantStorage, Events, Attendance, RSVP

import time, pickle


class database:

    def __init__(self, path) -> None:
        self.db_path = path + "data.db"
        
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        Base.metadata.create_all(self.engine)

    def remove_all_records_from_table(self):
        self.session.query(SavedVar).delete()
        self.commit()

    def commit(self):
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()  # Explicitly rollback the transaction
    
    def get_user_states(self, user_id):
        user_states = self.session.query(SavedVar).filter(SavedVar.id == user_id).first()
        if user_states and user_states.var:
            user_states_dict = self.ensure_user_states_keys(pickle.loads(user_states.var))
            return user_states_dict
        return {}

    def update_user_states(self, user_id, user_states_dict):
        user_states = self.session.query(SavedVar).filter(SavedVar.id == user_id).first()
        if not user_states:
            user_states = SavedVar(id=user_id, type="user_states")
            user_states.var = pickle.dumps(self.ensure_user_states_keys(user_states_dict))
            self.session.add(user_states)
        else:
            user_states.var = pickle.dumps(self.ensure_user_states_keys(user_states_dict))
        self.commit()

    def ensure_user_states_keys(self, user_states_dict):
        if user_states_dict is None or user_states_dict == "null":
            user_states_dict = {}

        if not user_states_dict.get("command"):
            user_states_dict["command"] = ""

        if not user_states_dict.get("stage"):
            user_states_dict["stage"] = ""

        if not user_states_dict.get("var"):
            user_states_dict["var"] = {}
            

        return user_states_dict

    #
    # USERS
    #
    def AddUser(self, user: Users):
        self.session.add(user)
        self.commit()

    def UpdateUser(self, user: Users):
        self.AddUser(user)

    def RemoveUser(self, key: str):
        user = self.GetUser(key)
        if user:
            self.session.delete(user)
            self.commit()

    def GetUser(self, key: str):
        return self.session.query(Users).filter(Users.id == key).first() or Users(id=key)

    def GetUserUnsafe(self, key: str):
        return self.session.query(Users).filter(Users.id == key).first() or Users(id=key)

    def ExistUser(self, key: str):
        return self.session.query(Users).filter(Users.id == key).first() is not None

    def GetAllUsers(self):
        users = self.session.query(Users).all()
        return users
    
    def GetUserNumber(self, number):
        return self.session.query(Users).filter(Users.number == number).first()

    #
    # Events
    #
    def AddEvents(self, obj: Events):
        self.session.add(obj)
        self.commit()

    def UpdateEvents(self, obj: Events):
        self.AddEvents(obj)

    def RemoveEvents(self, key: str):
        obj = self.GetEvents(key)
        if obj:
            self.session.delete(obj)
            self.commit()

    def GetEvents(self, key: str):
        return self.session.query(Events).filter(Events.id == key).first() or Events(id=key)

    def GetEventsUnsafe(self, key: str):
        return self.session.query(Events).filter(Events.id == key).first()

    def ExistEvents(self, key: str):
        return self.session.query(Events).filter(Events.id == key).first() is not None

    def GetAllEvents(self):
        obj = self.session.query(Events).all()
        return obj
    
    def GetAllUserEvents(self, user_id):
        obj = self.session.query(Events).filter(Events.user_id == user_id).all()
        return obj
    


    #
    # Attendance
    #
    def AddAttendance(self, obj: Attendance):
        self.session.add(obj)
        self.commit()

    def UpdateAttendance(self, obj: Attendance):
        self.AddAttendance(obj)

    def RemoveAttendance(self, key: str):
        obj = self.GetAttendance(key)
        if obj:
            self.session.delete(obj)
            self.commit()

    def GetAttendance(self, date: str, userid: str, event_code: str):
        key = f"{date}_{userid}_{event_code}"
        return self.session.query(Attendance).filter(Attendance.id == key).first() or Attendance(id=key)

    def GetAttendanceUnsafe(self, date: str, userid: str, event_code: str):
        key = f"{date}_{userid}_{event_code}"
        return self.session.query(Attendance).filter(Attendance.id == key).first()

    def ExistAttendance(self, date: str, userid: str, event_code: str):
        key = f"{date}_{userid}_{event_code}"
        return self.session.query(Attendance).filter(Attendance.id == key).first() is not None

    def GetAllAttendance(self):
        obj = self.session.query(Attendance).all()
        return obj
    
    def GetAllUserAttendance(self, user_id):
        obj = self.session.query(Attendance).filter(Attendance.user_id == user_id).all()
        return obj

    def GetAllEventAttendance(self, event_code):
        obj = self.session.query(Attendance).filter(Attendance.event == event_code).all()
        return obj
    
    def GetAllEventUserAttendance(self, user_id):
        obj = self.session.query(Attendance).filter(Attendance.event_user_id == user_id).all()
        return obj
    


    #
    # RSVP
    #
    def AddRSVP(self, obj: RSVP):
        self.session.add(obj)
        self.commit()

    def UpdateRSVP(self, obj: RSVP):
        self.AddRSVP(obj)

    def RemoveRSVP(self, key: str):
        obj = self.GetRSVP(key)
        if obj:
            self.session.delete(obj)
            self.commit()

    def GetRSVP(self, userid: str, event_code: str):
        key = f"{userid}_{event_code}"
        return self.session.query(RSVP).filter(RSVP.id == key).first() or RSVP(id=key)

    def GetRSVPUnsafe(self, userid: str, event_code: str):
        key = f"{userid}_{event_code}"
        return self.session.query(RSVP).filter(RSVP.id == key).first()

    def ExistRSVP(self, userid: str, event_code: str):
        key = f"{userid}_{event_code}"
        return self.session.query(RSVP).filter(RSVP.id == key).first() is not None

    def GetAllRSVP(self):
        obj = self.session.query(RSVP).all()
        return obj
    
    def GetAllUserRSVP(self, user_id):
        obj = self.session.query(RSVP).filter(RSVP.user_id == user_id).all()
        return obj

    def GetAllEventRSVP(self, event_code):
        obj = self.session.query(RSVP).filter(RSVP.event == event_code).all()
        return obj
    
    def GetAllEventUserRSVP(self, user_id):
        obj = self.session.query(RSVP).filter(RSVP.event_user_id == user_id).all()
        return obj

    
    #
    # BLACKLIST
    #

    def AddBan(self, ban: BanList):
        self.session.add(ban)
        self.commit()


    def UpdateBan(self, ban: BanList):
        self.AddBan(ban)

    def RemoveBan(self, key: str):
        ban = self.GetBan(key)
        if ban:
            self.session.delete(ban)
            self.commit()


    def GetBan(self, key):
        return self.session.query(BanList).filter(BanList.id == key).first() or BanList(id=key)


    def ExistBan(self, key):
        return  self.session.query(BanList).filter(BanList.id == key).first() is not None

    #
    # Persistant Storage
    #
    def AddPersistantStorage(self, store: PersistantStorage):
        self.session.add(store)
        self.commit()

    def UpdatePersistantStorage(self, store: PersistantStorage):
        self.AddPersistantStorage(store)

    def RemovePersistantStorage(self, key: str):
        PersistantStorage = self.GetPersistantStorageOBJ(key)
        if PersistantStorage:
            self.session.delete(PersistantStorage)
            self.commit()

    def GetPersistantStorage(self, key: str):
        obj = self.session.query(PersistantStorage).filter(PersistantStorage.id == key).first()
        return obj.value

    def GetPersistantStorageOBJ(self, key: str):
        obj = self.session.query(PersistantStorage).filter(PersistantStorage.id == key).first()
        return obj