import re
from datetime import datetime
from chatlib.date_tools import parse_or_none, infer_date
from chatlib.base import BaseChatData

UNICODE_LS = "\u2028"
UNICODE_PS = "\u2029"

class LineChatData(BaseChatData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_name = "LINE", *args, **kwargs)
    
    def read_from_file(self, path, anonymize=False):
        self._date_time, self._sender, self._event, self._message = [], [], [], []
        with open(path, encoding="utf-8", errors="ignore") as f:
            self.room = f.readline().rstrip()
            self.export_time = f.readline().rstrip()

            self._temp_date = None      # LINE uses hour as timestamps, dates are on different special row
            for line in f:
                self.parse_row(line.rstrip())
        
        for i, message in enumerate(self._message):
            if message is None:
                continue
            
            self._message[i] = message.replace(UNICODE_LS, "\n").replace(UNICODE_PS, "\n")

            if self.OBJECT_PATTERN.match(message):
                self._event[i] = message
                self._message[i] = None
        
        # Find senders of events, if possible
        self.participants = {sender for sender in self._sender if sender is not None}
        find_sender_of_event = lambda message: next((sender for sender in self.participants if message.startswith(tuple(self.participants))), None)
        for i, event in enumerate(self._event):
            if event and (sender := find_sender_of_event(event)):
                self._sender[i] = sender
                self._event[i] = self._event[i].lstrip(sender).lstrip()

        date_pattern = infer_date(self._date_time)
        self._date_time = [datetime.strptime(i, date_pattern) for i in self._date_time]
        self.database = [self._date_time, self._sender, self._event, self._message] # Not pandas dataframe?
        self.n_entry = len(self._date_time)
        self.start_date, self.end_date = self._date_time[0].date(), self._date_time[-1].date()

        if anonymize:
            self.anonymize()

    def define_patterns(self):
        self.SEP = "\t"  # SEPARATOR, in LINE they only use \t as separators, TIME\tSENDER\tMESSAGE
        
        self.HOUR_PATTERN = re.compile(r"""
            ^\d{2}      # Begins with two digits (HOURS)
            [:\.]       # Followed by a colon or a dot (HOUR-MINUTE SEPARATOR)
            \d{2}       # Followed by two digits (MINUTES)
            \t          # Followed by a tab (TSA SEPARATOR)
        """, re.VERBOSE)

        self.OBJECT_PATTERN = re.compile(r"""
            ^\[          # Begins with a [
            [^\]]+       # Followed by one or more of something other than a ]
            \]           # Followed by a ] (Stickers and media e.g. photo)
            $            # Ends (this is to prevent header-messages, it is quite popular i.e. [ANNOUNCEMENT])
        """, re.VERBOSE)

    def parse_row(self, row):
        timestamp, rest_of_line = self._separate_timestamp(row)
        if not timestamp:
            # row does not contain timestamp
            if (date_ := parse_or_none(row)):
                self._temp_date = date_
                try: self._message[-1] = self._message[-1].rstrip("\n")
                except (IndexError, AttributeError): pass # IndexError to ignore first date ever, AttributeError to ignore None before a date
            else:
                self._record_continuation(row)
            return
        
        timestamp = self._temp_date + " " + timestamp
        # row is a new record
        sender, message = self._separate_sender(rest_of_line)
        if not sender:
            # row is an event
            # sender can be '' or None; it's okay (i think) to keep passing it as function arg
            self._record_new_row(date_time=timestamp, sender=sender, event=message)
            return

        # row is a chat
        self._record_new_row(date_time=timestamp, sender=sender, message=message)
    
    def anonymize(self):
        """Replace the known usernames from sender and message list
        
        Known usernames i.e. those contained in sender list will be replaced with integers
        Unknown usernames i.e. perhaps mentioned social media @s etc. will be replaced with @_
        """

        UNKNOWN = "Unknown" # LINE standard name for unknown/deleted accounts
        sender_to_number = {j: str(i) for i, j in enumerate(self.participants) if j != UNKNOWN}

        # Anonymize sender list
        self._sender = [sender_to_number.get(sender, sender) for sender in self._sender if sender != UNKNOWN]
        
        # Anonymize usernames in messages
        USERNAME_PATTERN = re.compile(
            "|".join([
                "(@" + sender + ")" for sender in self._sender
                if sender not in {None, UNKNOWN} # Every sender names known is compiled to one
            ]) +
            r"""(
                @       # Begins with @
                \w+     # Followed by one or more non-whitespace characters
            )""", re.VERBOSE)
        for i, message in enumerate(self._message):
            for match in USERNAME_PATTERN.finditer(message):
                message = message[:match.start()] + ("@" + sender_to_number.get(match.lstrip("@"), "_")) + message[match.end():]
            self._message[i] = message


    def _separate_timestamp(self, line):
        if not self.HOUR_PATTERN.match(line):
            return None, line
        
        hour, rest = line.split(self.SEP, 1)
        return hour, rest
    
    def _separate_sender(self, line_segment):
        if self.SEP not in line_segment:
            return None, line_segment
        
        sender, message = line_segment.split(self.SEP, 1)
        return sender, message
    
    def _record_continuation(self, line):
        if line:
            self._message[-1] += "\n" + line

    def _record_new_row(self, *args, **kwargs):
        self._date_time.append(kwargs["date_time"]) # For a new row, a timestamp must exist. Others may be None.

        self._sender.append(kwargs.get("sender"))
        self._event.append(kwargs.get("event"))
        self._message.append(kwargs.get("message"))