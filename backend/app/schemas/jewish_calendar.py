from datetime import date, datetime
from pydantic import BaseModel


class Zmanim(BaseModel):
    sunrise: datetime | None
    sunset: datetime | None
    candle_lighting: datetime | None
    havdalah: datetime | None


class JewishDayInfo(BaseModel):
    gregorian_date: date
    jewish_date_str: str
    parsha: str | None
    holidays: list[str]
    omer_day: int | None
    day_type: str
    zmanim: Zmanim
