from datetime import datetime
from typing import Optional


class BaseChatData:
    """Base class for chat export data structure"""
    def __init__(self, *args, **kwargs):
        self.database = None
        self.app_name: Optional[str] = kwargs.get("app_name", None)
        self.room: str = None
        self.export_time: str = None
        self.start_date: datetime = None
        self.end_date: datetime = None
        self.participants: set = None
        self.n_entry: int = None

        self._date_time, self._sender, self._event, self._message = [], [] ,[] ,[]

        self.define_patterns()
    
    def __str__(self):
        _str = self.__repr__() + "\n\n"
        if self.app_name:
            _str += "Source application: " + self.app_name + "\n"
        if self.room:
            _str += "Source room: " + self.room + "\n"
        if self.export_time:
            _str += "Time this chat data is exported: " + self.export_time + "\n"
        
        _str += "Number of entries recorded in this chat data: " + str(self.n_entry)
        
        return _str.rstrip("\n")


    def define_patterns(self):
        pass
    
    def read_from_file(self, path):
        pass

    def anonymize(self):
        pass