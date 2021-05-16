from chatlib.date_tools import check_complete_date, infer_date
import re
from datetime import datetime

from chatlib.base import BaseChatData

class WhatsAppChatData(BaseChatData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_name = "WhatsApp", *args, **kwargs)
        
    def read_from_file(self, path):
        self._date_time, self._sender, self._event, self._message = [], [], [], []
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                self.parse_row(line.rstrip("\n")) # Every line's rightmost \n is read; here I truncate it
        
        date_pattern = infer_date(self._date_time)
        self._date_time = [datetime.strptime(i, date_pattern) for i in self._date_time]
        self.database = [self._date_time, self._sender, self._event, self._message] # Not pandas dataframe?
        self.participants = set(self._sender)
        self.n_entry = len(self._date_time)
        self.start_date, self.end_date = self._date_time[0].date(), self._date_time[-1].date()

        # NOTE(Rayhan) sort by _date_time to account for slight connection problems or deal ad hoc?
        # I'm inclined to leave it as it is and let user deal ad hoc
        # Why? Sorting will hide unexpected behaviors
        
    def define_patterns(self):
        self.DA_SEP = " - " # Datetime and Anything SEPARATOR
        self.SE_SEP = ": "  # Sender and Event SEPARATOR

        self.OBJECT_RE = re.compile(r"""
            (
                ^<          # Begins with <
                [^>]+       # Followed by one or more of something other than >
                >$          # Followed by > and ends. (Media, such as image or video)
            ) | (
                .+          # Begins with anything, once or more
                \.vcf       # Followed by .vcf (Contact, usually in vcf)
            )
        """, re.VERBOSE)
    
    def parse_row(self, row):
        timestamp, rest_of_line = self._separate_timestamp(row)
        if not timestamp:
            # row is continuation
            self._record_continuation(rest_of_line)
            return
            
        # row is not continuation, ...
        sender, message = self._separate_sender(rest_of_line)
        if not sender or self.OBJECT_RE.match(message):
            # row is non-chat event. Sidenote: sender is not always None, can be "" theoretically
            self._record_new_row(date_time=timestamp, sender=sender, event=message)
            return
        
        # row is new chat event
        self._record_new_row(date_time=timestamp, sender=sender, message=message)
    
    def _separate_timestamp(self, line_segment):
        if self.DA_SEP not in line_segment:
            return None, line_segment
        
        date_time, rest = line_segment.split(self.DA_SEP, 1)

        # Replace any dots with colons (dateutil refuses to understand dot as hour-minute separator)
        # Note: it's a decimal second separator, it makes sense for dateutil to refuse to parse
        # But chat exports won't be recorded to milliseconds anyway
        date_time = date_time.replace(".", ":")

        if not check_complete_date(date_time):
            # Validate: try parse into datetime object here, return None if turns out before DA_SEP is not a date
            # Only try, not actually convert. Conversion will be done after inferring its date pattern.
            date_time, rest = None, line_segment

        return date_time, rest
    
    def _separate_sender(self, line_segment):
        if self.SE_SEP not in line_segment:
            return None, line_segment
        
        sender, message = line_segment.split(self.SE_SEP, 1)
        return sender, message

    def _record_continuation(self, line):
        if line:
            self._message[-1] += "\n" + line

    def _record_new_row(self, *args, **kwargs):
        self._date_time.append(kwargs["date_time"]) # For a new row, a timestamp must exist. Others may be None.

        self._sender.append(kwargs.get("sender"))
        self._event.append(kwargs.get("event"))
        self._message.append(kwargs.get("message"))
