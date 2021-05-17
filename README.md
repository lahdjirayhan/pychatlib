# pychatlib

Provides functionality to read messenger/chat application exports.

# Installation

```
pip install pychatlib
```
# Usage

Suppose you have exported your group conversation in LINE to a `.txt` file (which is what LINE does when exporting). If you want to read the `.txt` file into Python, you can use the following commands.

```
from chatlib.line import LineChatData
line = LineChatData("E:/my_line_export.txt")
```

The resulting object has following attributes:
- `database`: this is the most interesting attribute. It contains the data of the conversation. In its current form, it is simply a list of four lists:
    - `_date_time`: denotes time of a record
    - `_sender`: denotes a sender, or a person that is involved in the creation of the record
    - `_event`: denotes an event, i.e. a record which is not a chat, e.g. when someone joins the group or unsent a message.
    - `_message`: denotes the chat.

- `n_entry`: how many records are listed.
- `start_date`: earliest record's time.
- `end_date`: most recent record's time.
- `participants`: set of all sender names in the group. If someone is in the group but does not have their name recorded on the export file at all, their name will not be here.

Information regarding metadata of the object can be obtained via

```
print(line)
```

which will display whatever is available out of these things (not all applications provide these info on their export file):

- What application exports the file
- When the file is exported
- What name is the personal/group/room chat
- How many records are available

# Applications

Currently this package is able to read these applications' exports:
- WhatsApp
- LINE
