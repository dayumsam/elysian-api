import os
import sqlite3
import json
from flask import Flask, render_template, jsonify, request, make_response, session
from flask_session import Session

from flask_cors import CORS, cross_origin

from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import close_all_sessions

import pandas as pd
import numpy as np

from imagekitio import ImageKit
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = '}>0q~A>cDk_fZ37kO"8BY9fA(zZ1>{5Wfq0Sdc-M?=a{3s@ew2ik/+F?U)9LnlI'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
cors = CORS(app)

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


@app.route('/get_image')
@cross_origin()
def images():
    images = Images.query.order_by(func.random()).all()
    return jsonify(images)

def generateResult(dataset):
    sql = '''SELECT * FROM styles'''
    conn = db.engine.connect().connection

    model = pd.read_sql(sql, conn)

    dataPrams = []

    for i in dataset:

        obj = model.query('styles=="%s"' % i.lower())
        obj = obj.drop(obj.columns[[0,1]], axis=1)
        
        dataPrams.append(obj)

    store = pd.concat(dataPrams, ignore_index=True)
    store = store.mode().iloc[:1]

    store = model.drop(model.columns[[0,1]], axis=1) - store.values.tolist()[0]
    store = store.T.apply(pd.Series.value_counts)
    store = store.loc[[0]]

    model =  pd.concat([model.T , store]).T.sort_values(by=0, ascending=False)

    result = model.iloc[0: 3]
    result = result.styles.values.tolist()

    return result

def generatePageData(style):
    result = Suggestion.query.filter_by(styles=style).first()
    photo =  Images.query.filter_by(tags=style).limit(3).all()

    data = {
        'content': result,
        'photo': photo
    }

    return data

@app.route('/generate_result', methods = ['POST'])
def index():
    dataset = request.json['data']
    contact = request.json['contact']

    print(contact)

    result = generateResult(dataset)

    newUser = Contact(fname=contact['fname'], lname=contact['lname'], email=contact['email'], style=result[0] )
    db.session.add(newUser)
    db.session.commit()

    output = []

    for i in result:
        output.append(generatePageData(i))

    data = {
        "result" : result, 
        "output": output
        }
    
    close_all_sessions()

    return make_response(data, 200)