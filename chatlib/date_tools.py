from typing import List, Optional
from dateutil.parser import ParserError, parser
from pydateinfer import infer
import random
from datetime import datetime

def check_complete_date(datetimestr: str) -> bool:
    res, _ = parser()._parse(datetimestr)           # type: ignore
    if res and all([res.year, res.month, res.day]):
        return True
    return False

def parse_or_none(datetimestr: str) -> Optional[str]:
    try:
        parser().parse(datetimestr)
        return datetimestr
    except ParserError:
        return None

def infer_date(datetimelst: List[datetime]) -> str:
    sample = random.sample(datetimelst, 500) if len(datetimelst) > 500 else datetimelst
    return infer(sample)