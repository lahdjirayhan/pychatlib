from typing import List, Optional
from dateutil.parser import ParserError, parser
from pydateinfer import infer
import random
from datetime import datetime

def check_complete_date(datetimestr: str) -> bool:
    """Check if a string becomes datetime that contains year, month, and date when parsed

    This function helps disambiguate whether a possible parseable string is actually a datetime-
    like timestamp or a false positive. This is because dateutil's parse utility accepts an
    incomplete date string (e.g. a single integer 1 that can be interpreted as "1st of today's
    month and year").

    Args:
        datetimestr (str): A string that represents a datetime

    Returns:
        bool: True if string contains year, month, and date; False otherwise
    """    
    res, _ = parser()._parse(datetimestr)           # type: ignore
    if res and all([res.year, res.month, res.day]):
        return True
    return False

def parse_or_none(datetimestr: str) -> Optional[str]:
    """Check if a string is parseable to datetime

    If a string can be parsed to datetime using dateutil's parser,
    return back the string. Otherwise, return None.

    Args:
        datetimestr (str): A string to be checked

    Returns:
    Optional[str]: ...
        - str: Return back datetimestr if it is parseable to datetime
        - None: Return None if datetimestr is not parseable to datetime
    """
    try:
        parser().parse(datetimestr)
        return datetimestr
    except ParserError:
        return None

def infer_date(datetimelst: List[datetime]) -> str:
    """Infer date(time) pattern from a large list of datetime objects using sampling

    Sample at most 500 elements randomly from the list. Using this sample, infer the most likely
    pattern. Inferring the pattern is an expensive operation, and random sampling is used
    as a resort to reduce the runtime.

    Args:
        datetimelst (List[datetime]): List of datetime objects

    Returns:
        str: String that represents the most likely pattern, in a format compatible with strptime
    """
    sample = random.sample(datetimelst, 500) if len(datetimelst) > 500 else datetimelst
    return infer(sample)