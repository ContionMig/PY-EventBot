import pandas as pd
import time
import datetime
import os
import xlsxwriter

from structs.model import Base, BanList, Users, SavedVar


class Excel:

    db_path = ""

    def __init__(self, path, globals) -> None:
        self.db_path = path + "datasheets/"
        self.globals = globals

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

    def ExportSingleEvent(self, event_id="all", user_id="-1"):
        
        curr_time = str(time.time())
        final_path = f"{self.db_path}{event_id}_{curr_time}.xlsx"

        workbook = xlsxwriter.Workbook(final_path)
        
        header_format = workbook.add_format({"border": 1, "bold": True, 'bg_color': '#000000', 'color': "#FFFFFF", 'align': 'center', 'valign': 'vcenter'})
        normal_format = workbook.add_format({"border": 1, 'bg_color': '#FFFFFF', 'color': "#000000"})

        sheets = [
            "Attendance",
            "RSVP"
        ]

        all_worksheet = {}
        for sheet in sheets:
            worksheet = workbook.add_worksheet(sheet)

            if sheet == "Attendance":
                worksheet.write(0, 0, "Event Code", header_format)
                worksheet.write(0, 1, "Event Name", header_format)
                worksheet.write(0, 2, "Event Creator ID", header_format)
                worksheet.write(0, 3, "Attendee ID", header_format)
                worksheet.write(0, 4, "Attendee Full Name", header_format)
                worksheet.write(0, 5, "Attendee NRIC", header_format)
                worksheet.write(0, 6, "Attendee Phone", header_format)
                worksheet.write(0, 7, "Attendee Office", header_format)
                worksheet.write(0, 8, "Date", header_format)
            
            elif sheet == "RSVP":
                worksheet.write(0, 0, "Event Code", header_format)
                worksheet.write(0, 1, "Event Name", header_format)
                worksheet.write(0, 2, "Event Creator ID", header_format)
                worksheet.write(0, 3, "Attendee ID", header_format)
                worksheet.write(0, 4, "Attendee Full Name", header_format)
                worksheet.write(0, 5, "Attendee NRIC", header_format)
                worksheet.write(0, 6, "Attendee Phone", header_format)
                worksheet.write(0, 7, "Attendee Office", header_format)
                worksheet.write(0, 8, "Interest", header_format)
                worksheet.write(0, 9, "Date", header_format)

            all_worksheet[sheet] = {}
            all_worksheet[sheet]["sheet"] = worksheet
            all_worksheet[sheet]["row"] = 1
            all_worksheet[sheet]["serial_number"] = 1

        for sheet in sheets:

            if sheet == "Attendance":
                
                if event_id == "all":
                    dataset= self.globals.db.GetAllEventUserAttendance(user_id)
                else:
                    dataset = self.globals.db.GetAllEventAttendance(event_id)

                for data in dataset:
                    
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 0, data.event, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 1, data.event_name, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 2, data.event_user_id, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 3, data.user_id, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 4, data.full_name, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 5, data.nric, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 6, data.phone, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 7, data.office, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 8, data.date, normal_format)
            
                    all_worksheet[sheet]["row"] += 1
                    all_worksheet[sheet]["serial_number"] += 1
            
            elif sheet == "RSVP":

                if event_id == "all":
                    dataset= self.globals.db.GetAllEventUserRSVP(user_id)
                else:
                    dataset = self.globals.db.GetAllEventRSVP(event_id)

                for data in dataset:
                    
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 0, data.event, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 1, data.event_name, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 2, data.event_user_id, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 3, data.user_id, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 4, data.full_name, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 5, data.nric, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 6, data.phone, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 7, data.office, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 8, data.interest_level, normal_format)
                    all_worksheet[sheet]["sheet"].write(all_worksheet[sheet]["row"], 9, data.date, normal_format)
            
                    all_worksheet[sheet]["row"] += 1
                    all_worksheet[sheet]["serial_number"] += 1

        for sheets in all_worksheet.keys():
            all_worksheet[sheets]["sheet"].autofit()
        
        workbook.close()
        return final_path