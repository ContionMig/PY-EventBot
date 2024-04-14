import datetime
import holidays
from urllib.parse import urlparse

class Helper:

    def ValidName(self, name):
        if name.replace(" ", "").isalpha():
            return True
        return False

    def ValidNRIC(self, nric: str):
        if len(nric) != 4:
            return False

        if not nric[:3].isdigit():
            return False

        if not nric[-1].isalpha():
            return False

        return True

    def ValidDate(self, date, format="%d/%m/%Y"):

        try:
            datetime.datetime.strptime(date, format)
            return True
        except ValueError:
            return False
    
    def find_next_weekday(self, input_datetime):
        
        next_weekday = input_datetime

        sg_holidays = holidays.Singapore(years=next_weekday.year)
        while next_weekday in sg_holidays or next_weekday.weekday() >= 5:
            next_weekday += datetime.timedelta(days=1)
            
        return next_weekday
    
    def is_valid_link(self, link):
        try:
            result = urlparse(link)
            return bool(result.netloc)  # Check if netloc is present
        except:
            return False

helper = Helper()
