import os
import json

import random

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

# Google Sheets API Setup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from imagekitio import ImageKit
from imagekitio.models.ListAndSearchFileRequestOptions import ListAndSearchFileRequestOptions

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ENGINE_OPPTIONS'] = {
    'poolclass': NullPool,
}

db.init_app(app)
cors = CORS(app)

# imagekit initialization
imagekit = ImageKit(
    public_key=os.getenv('IMAGE_KIT_PUBLIC_KEY'),
    private_key=os.getenv('IMAGE_KIT_PRIVATE_KEY'),
    url_endpoint=os.getenv('IMAGE_KIT_URL')
)

# Get the image URLs from the database


@app.route('/images')
@cross_origin()
def getImage():

    # Fetch file options
    options = ListAndSearchFileRequestOptions(
        path='/elysian',
    )

    # Get response from imagekit
    images = imagekit.list_files(options=options).response_metadata.raw
    random.shuffle(images)  # randomize the list

    return jsonify(images)  # returning JSON as the API response

# Generate preferred style


def generateResult(dataset):
    # dataset: ["style1", "style2", "style3", ...]
    # an array with selected styles

    sql = '''SELECT * FROM styles'''  # SQL Query
    conn = db.engine.connect().connection

    # importing data as a pandas dataframe
    model = pd.read_sql(sql, conn)

    dataPrams = []

    for i in dataset:
        # Query individual styles form the model
        obj = model.query('styles=="%s"' % i.lower())
        obj = obj.drop(obj.columns[[0, 1]], axis=1)  # TODO

        dataPrams.append(obj)

    store = pd.concat(dataPrams, ignore_index=True)
    store = store.mode().iloc[:1]

    store = model.drop(model.columns[[0, 1]],
                       axis=1) - store.values.tolist()[0]
    store = store.T.apply(pd.Series.value_counts)
    store = store.loc[[0]]

    model = pd.concat([model.T, store]).T.sort_values(by=0, ascending=False)

    result = model.iloc[0:3]
    result = result.styles.values.tolist()

    return result


def generatePageData(style):
    # Gets images and style recommendations
    result = Suggestion.query.filter_by(styles=style).first()
    searchQuery = "{}".format(style)

    # Fetch file options
    options = ListAndSearchFileRequestOptions(
        limit=3,
        tags=style,
    )

    # Get response from imagekit
    images = imagekit.list_files(options=options).response_metadata.raw

    data = {
        'content': result,
        'images': images
    }

    return data


@app.route('/results', methods=['POST'])
def index():

    # Get data from the request
    dataset = request.json['data']  # Selected styles
    contact = request.json['contact']  # Contact Info

    # Generate Result
    result = generateResult(dataset)  # Generate preferred result

    # Create a new user
    newUser = Contact(
        fname=contact['fname'], lname=contact['lname'], email=contact['email'], style=result[0])

    # Add user to the database
    db.session.add(newUser)
    db.session.commit()
    db.session.close()

    # # Open the google sheet
    credential = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json")

    client = gspread.authorize(credential)
    gsheet = client.open("Find your style | Elysian").sheet1

    # # Insert data into the row
    row = [contact['fname'], contact['lname'], contact['email'], result[0]]
    gsheet.append_row(row)  # Append a new row to the sheet

    # Generate output
    output = []

    for i in result:
        output.append(generatePageData(i))  # Generate style data

    data = {
        "result": result,
        "output": output
    }

    return make_response(data, 200)
