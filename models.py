from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

db = SQLAlchemy()

class Styles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    styles = db.Column(db.String())
    timeperiod = db.Column(db.Integer)
    functionality = db.Column(db.Integer)
    traffic = db.Column(db.Integer)
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    dynamic = db.Column(db.Integer)
    shape = db.Column(db.Integer)
    details = db.Column(db.Integer)
    orientation = db.Column(db.Integer)
    lighting = db.Column(db.Integer)
    intensity = db.Column(db.Integer)
    fixtures = db.Column(db.Integer)
    vibrancy = db.Column(db.Integer)
    statement = db.Column(db.Integer)
    tone = db.Column(db.Integer)
    finish = db.Column(db.Integer)
    feel = db.Column(db.Integer)
    ambience = db.Column(db.Integer)
    prints = db.Column(db.Integer)
    style = db.Column(db.Integer)

    def __repr__(self):
        return '<Styles %r>' % self.styles

@dataclass
class Suggestion(db.Model):
    id: int
    styles: str
    overview: str
    details: str
    tip_1: str
    tip_2: str
    tip_3: str
    tip_4: str
    tip_5: str
    tip_6: str

    id = db.Column(db.Integer, primary_key=True)
    styles = db.Column(db.String())
    overview = db.Column(db.String())
    details = db.Column(db.String())
    tip_1 = db.Column(db.String())
    tip_2 = db.Column(db.String())
    tip_3 = db.Column(db.String())
    tip_4 = db.Column(db.String())
    tip_5 = db.Column(db.String())
    tip_6 = db.Column(db.String())

@dataclass
class Images(db.Model):
    id: int
    fileId: str
    url: str
    tags: str

    id = db.Column(db.Integer, primary_key=True)
    fileId = db.Column(db.String(50))
    url = db.Column(db.String(500))
    tags = db.Column(db.String(50))


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String())
    lname = db.Column(db.String())
    email = db.Column(db.String())
    style = db.Column(db.String())