import os
import logging
import random

from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from dotenv import load_dotenv

from imagekitio import ImageKit
from imagekitio.models.ListAndSearchFileRequestOptions import ListAndSearchFileRequestOptions

from pydantic import BaseModel
from sqlmodel import Session, select, create_engine

from fastapi.middleware.cors import CORSMiddleware

import polars as pl

# Google Sheets API Setup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Import DB models
from models import Suggestion, Contact as ContactModel

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Load environment variables
load_dotenv()

# Initialize ImageKit
public_key = os.getenv('IMAGE_KIT_PUBLIC_KEY')
private_key = os.getenv('IMAGE_KIT_PRIVATE_KEY')
url_endpoint = os.getenv('IMAGE_KIT_URL')

if not public_key or not private_key or not url_endpoint:
    logging.error('ImageKit environment variables are not set properly.')
    raise ValueError('ImageKit environment variables are missing.')

imagekit = ImageKit(
    public_key=public_key,
    private_key=private_key,
    url_endpoint=url_endpoint
)

# Database configuration
DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

if not DATABASE_URI:
    logging.error(
        "The SQLALCHEMY_DATABASE_URI environment variable is not set.")
    raise ValueError(
        "The SQLALCHEMY_DATABASE_URI environment variable is not set.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URI)

origins = os.getenv('ORIGIN', "[*]")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    with Session(engine) as session:
        yield session


@app.get('/images')
def get_images():
    """
    Endpoint to retrieve images from ImageKit.
    """
    logging.info('Received request for images.')

    # Fetch file options from ImageKit
    options = ListAndSearchFileRequestOptions(
        path='/elysian',
    )

    try:
        # Get response from ImageKit
        images = imagekit.list_files(options=options).response_metadata.raw
        random.shuffle(images)  # Randomize the list

        logging.info('Successfully retrieved images from ImageKit.')
    except Exception as e:
        # Raise error
        logging.error(f'Error retrieving images from ImageKit: {e}')
        raise HTTPException(status_code=500, detail='Error retrieving images.')

    # Return the images as JSON response
    json_compatible_item_data = jsonable_encoder(images)
    return JSONResponse(content=json_compatible_item_data)


def compute_distance(df, mode_vector, distance_metric='manhattan'):
    """
    Compute the distance between each style in the DataFrame and the mode vector.

    Parameters:
    - df: Polars DataFrame containing the styles data.
    - mode_vector: Dictionary with the mode values for each feature.
    - distance_metric: 'manhattan' or 'euclidean'.

    Returns:
    - df_with_distance: DataFrame with an additional 'distance' column.
    """
    logging.info(f'Computing {distance_metric} distance.')

    # Select the feature columns
    feature_cols = list(mode_vector.keys())

    # Create expressions to compute the difference between each feature and the mode
    if distance_metric == 'manhattan':
        # Sum of absolute differences
        distance_expr = pl.fold(
            acc=pl.lit(0),
            function=lambda acc, x: acc + x,
            exprs=[
                (pl.col(col).cast(pl.Int64) - pl.lit(mode_vector[col])).abs() for col in feature_cols
            ]
        ).alias('distance')
    elif distance_metric == 'euclidean':
        # Square root of sum of squared differences
        distance_expr = pl.fold(
            acc=pl.lit(0),
            function=lambda acc, x: acc + x,
            exprs=[
                ((pl.col(col).cast(pl.Int64) - pl.lit(mode_vector[col])).pow(2)) for col in feature_cols
            ]
        ).sqrt().alias('distance')
    else:
        logging.error(f'Unsupported distance metric: {distance_metric}')
        raise ValueError(
            "Unsupported distance metric. Use 'manhattan' or 'euclidean'.")

    # Compute the distance and add it as a new column
    df_with_distance = df.with_columns(distance_expr)

    logging.info('Distance computation completed.')

    return df_with_distance


def find_closest_styles(df, mode_vector, top_n=5, distance_metric='manhattan'):
    """
    Find the top N closest styles to the mode vector.

    Parameters:
    - df: Polars DataFrame containing all styles.
    - mode_vector: Dictionary with the mode values for each feature.
    - top_n: Number of top styles to return.
    - distance_metric: 'manhattan' or 'euclidean'.

    Returns:
    - top_styles: DataFrame with the top N closest styles.
    """
    logging.info(f'Finding top {top_n} closest styles using {
                 distance_metric} distance.')

    # Compute the distances
    df_with_distances = compute_distance(df, mode_vector, distance_metric)

    # Sort the DataFrame by distance
    df_sorted = df_with_distances.sort('distance')

    # Get the top N styles
    top_styles = df_sorted.head(top_n)

    logging.info('Found closest styles.')

    return top_styles


def generateResult(dataset):
    """
    Generate the top styles based on the user's selected styles.

    Parameters:
    - dataset: List of styles selected by the user.

    Returns:
    - result: List of the top styles.
    """
    logging.info('Generating result based on user preferences.')

    sql = '''SELECT * FROM styles'''  # SQL Query

    try:
        with engine.connect() as conn:
            # Read data from the database using Polars
            model = pl.read_database(sql, conn)
        logging.info('Successfully read styles data from the database.')
    except Exception as e:
        logging.error(f'Error reading styles data from the database: {e}')
        raise HTTPException(
            status_code=500, detail='Error reading styles data.')

    dataPrams = []

    for style_name in dataset:
        # Filter the DataFrame for the selected styles
        obj = model.filter(pl.col('styles') == style_name.lower())
        # Drop unnecessary columns
        obj = obj.drop(["id", "styles"])
        dataPrams.append(obj)

    if not dataPrams:
        logging.error('No matching styles found in the dataset.')
        raise HTTPException(
            status_code=400, detail='No matching styles found.')

    # Concatenate all filtered DataFrames
    store = pl.concat(dataPrams)

    # Compute the mode for each column
    store_mode = store.select([
        pl.col(column).mode().first().alias(column) for column in store.columns
    ])

    # Extract mode values as a dictionary
    mode_values = store_mode.row(0, named=True)

    logging.info('Mode values computed.')

    # Find the top styles closest to the mode vector
    top_styles = find_closest_styles(
        model, mode_values, top_n=5, distance_metric='manhattan')

    # Get the list of style names
    result = top_styles.get_column("styles").to_list()

    logging.info(f'Generated result: {result}')

    return result


def generatePageData(style: str):
    """
    Generate page data for a given style, including content and images.

    Parameters:
    - style: The style name.

    Returns:
    - data: Dictionary containing 'content' and 'images'.
    """
    logging.info(f'Generating page data for style: {style}')

    with Session(engine) as session:
        # Query the Suggestion model for the given style
        statement = select(Suggestion).where(Suggestion.styles == style)
        result = session.exec(statement).first()

    if not result:
        logging.error(f'Style not found in the database: {style}')
        raise HTTPException(status_code=404, detail="Style not found")

    # Fetch file options from ImageKit
    options = ListAndSearchFileRequestOptions(
        limit=3,
        tags=[style],
    )

    try:
        # Get response from ImageKit
        images_response = imagekit.list_files(options=options)
        images = images_response.response_metadata.raw
        logging.info(f'Successfully retrieved images for style: {style}')
    except Exception as e:
        logging.error(f'Error retrieving images for style {style}: {e}')
        images = []

    data = {
        'content': result,
        'images': images
    }

    return data


class ContactInfo(BaseModel):
    """
    Pydantic model for contact information provided by the user.
    """
    fname: str | None = None
    lname: str | None = None
    email: str | None = None
    style: str | None = None


class Preferences(BaseModel):
    """
    Pydantic model for user preferences.
    """
    data: list
    contact: ContactInfo | None = None


@app.post('/results')
def index(preferences: Preferences):
    """
    Endpoint to process user preferences and return the recommended styles.

    Parameters:
    - preferences: User preferences and contact information.

    Returns:
    - JSON response containing the recommended styles and their data.
    """
    logging.info('Received /results POST request.')

    # Get data from the request
    result = generateResult(preferences.data)  # Generate preferred result
    contactInfo = preferences.contact

    if not hasattr(contactInfo, 'testing'):
        with Session(engine) as session:
            if contactInfo:
                # Create a new contact entry
                newUser = ContactModel(
                    fname=contactInfo.fname,
                    lname=contactInfo.lname,
                    email=contactInfo.email,
                    style=result[0]
                )

                # Commit the contact into the database
                session.add(newUser)
                session.commit()
                logging.info(f'New contact added to the database: {
                    contactInfo.email}')

                # Append contact information to Google Sheet
                try:
                    # Authenticate with Google Sheets API
                    credential = ServiceAccountCredentials.from_json_keyfile_name(
                        "credentials.json")
                    client = gspread.authorize(credential)
                    gsheet = client.open("Find your style | Elysian").sheet1

                    # Insert data into the sheet
                    row = [contactInfo.fname, contactInfo.lname,
                           contactInfo.email, result[0]]
                    gsheet.append_row(row)  # Append a new row to the sheet
                    logging.info(
                        'Contact information appended to Google Sheet.')
                except Exception as e:
                    logging.error(f'Error appending to Google Sheet: {e}')
            else:
                logging.warning('No contact information provided.')

    # Generate output data for each recommended style
    output = []

    for style_name in result:
        style_data = generatePageData(style_name)  # Generate style data
        output.append(style_data)

    data = {
        "result": result,
        "output": output
    }

    logging.info('Response data generated for /results endpoint.')

    # Return the data as JSON response
    return data
