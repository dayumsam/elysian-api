from typing import Optional
from sqlmodel import SQLModel, Field


class Styles(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    styles: str
    timeperiod: int
    functionality: int
    traffic: int
    horizontal: int
    vertical: int
    dynamic: int
    shape: int
    details: int
    orientation: int
    lighting: int
    intensity: int
    fixtures: int
    vibrancy: int
    statement: int
    tone: int
    finish: int
    feel: int
    ambience: int
    prints: int
    style: int

    def __repr__(self):
        return f"<Styles {self.styles}>"


class Suggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    styles: str
    overview: str
    details: str
    tip_1: str
    tip_2: str
    tip_3: str
    tip_4: str
    tip_5: str
    tip_6: str


class Images(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fileId: str = Field(max_length=50)
    url: str = Field(max_length=500)
    tags: str = Field(max_length=50)


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fname: str
    lname: str
    email: str
    style: str
