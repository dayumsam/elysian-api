import os
import json

from dotenv import load_dotenv

from flask import Flask, jsonify, request, make_response

# Handle cors requests
from flask_cors import CORS, cross_origin

# Import DB models
from models import db, Styles, Suggestion, Images, Contact

# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.pool import NullPool

# For data hadling
import pandas as pd
import numpy as np

from imagekitio import ImageKit

# Google Sheets API Setup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

app.secret_key = '}>0q~A>cDk_fZ37kO"8BY9fA(zZ1>{5Wfq0Sdc-M?=a{3s@ew2ik/+F?U)9LnlI'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ENGINE_OPPTIONS'] = {
    'poolclass': NullPool,
}

# db = SQLAlchemy(app)
db.init_app(app)

cors = CORS(app)

@app.route('/get_image')
@cross_origin()
def images():
    images = Images.query.order_by(func.random()).all()
    db.session.close()
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

    result = model.iloc[0:3]
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

    # Get data from the request
    dataset = request.json['data'] # Selected styles
    contact = request.json['contact'] # Contact Info

    # Generate Result
    result = generateResult(dataset) # Generate preferred result

    # Create a new user
    newUser = Contact(fname=contact['fname'], lname=contact['lname'], email=contact['email'], style=result[0])

    # Add user to the database
    db.session.add(newUser)
    db.session.commit()
    db.session.close()

    # # Open the google sheet
    credential = ServiceAccountCredentials.from_json_keyfile_name("credentials.json")

    client = gspread.authorize(credential)
    gsheet = client.open("Find your style | Elysian").sheet1

    # # Insert data into the row
    row = [contact['fname'], contact['lname'], contact['email'], result[0]]
    gsheet.append_row(row) # Append a new row to the sheet

    # Generate output
    output = []

    for i in result:
        output.append(generatePageData(i)) # Generate style data

    data = {
        "result" : result, 
        "output": output
        }

    return make_response(data, 200)