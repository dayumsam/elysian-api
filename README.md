# Elysian Style Recommendation API

Welcome to the Elysian Style Recommendation API! This application is designed to recommend interior design styles to users based on their preferences. It integrates with external services like ImageKit and Google Sheets to fetch images and store user contact information.

This README provides a comprehensive guide for developers to understand, set up, and run the application.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Appendix](#appendix)
- [Authors](#authors)

## Overview

The Elysian Style Recommendation API is built using FastAPI, leveraging SQLModel for ORM capabilities. The application performs the following key functions:

- Accepts user preferences and contact information via RESTful API endpoints.
- Processes the preferences to generate style recommendations using data analysis with Polars.
- Retrieves content and images related to the recommended styles from a database and ImageKit.
- Stores user contact information in a database and Google Sheets (unless in testing mode).

## Features

- **User Preference Analysis**: Processes user-selected styles to generate personalized recommendations.
- **Data Retrieval**: Fetches detailed content and images for each recommended style.
- **Database Integration**: Utilizes SQLModel for seamless database interactions.
- **ImageKit Integration**: Retrieves images based on style tags.
- **Google Sheets Integration**: Stores user contact information for marketing and follow-up (can be disabled during testing).
- **Logging**: Provides detailed logging for debugging and monitoring.
- **Testing Mode**: Allows developers to skip database and Google Sheets operations during testing.

## Architecture

### Main Components

- **API Endpoints**: Defined using FastAPI to handle HTTP requests.
- **Models**:
  - SQLModel models for database tables (`Styles`, `Suggestion`, `Images`, `Contact`).
  - Pydantic models for request validation (`Preferences`, `ContactInfo`).
- **Data Processing Functions**:
  - `compute_distance`: Calculates distances between user preferences and available styles.
  - `find_closest_styles`: Identifies the top matching styles.
  - `generateResult`: Integrates the above functions to produce recommendations.
  - `generatePageData`: Retrieves content and images for a given style.
- **External Services**:
  - ImageKit: For image retrieval.
  - Google Sheets: For storing user contact information.

### Data Flow

- **User Input**: User submits preferences and contact info via the `/results` endpoint.
- **Data Processing**:
  - Preferences are analyzed to compute the mode vector.
  - Styles in the database are compared using the Manhattan distance metric.
- **Recommendation Generation**: Top styles are selected based on proximity to the mode vector.
- **Data Retrieval**: Content and images for the recommended styles are fetched.
- **Response**: Compiled data is returned to the user.
- **Data Storage**: Contact info is saved to the database and Google Sheets (unless in testing mode).

## Prerequisites

Ensure you have the following installed:

- **Python 3.9 or higher**
- **Virtual Environment** tool (optional but recommended)
- **Database Server**: PostgreSQL, MySQL, or SQLite for development
- **ImageKit Account**: For image retrieval
- **Google Cloud Service Account**: For accessing Google Sheets API
- **Git**: For version control

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/dayumsam/elysian-api.git
cd elysian-style-recommendation
```

### Step 2: Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.

``python -m venv venv``

Activate the virtual environment:

- Windows:

  ```venv\Scripts\activate```

- Unix or macOS:
  ```source venv/bin/activate```

### Step 3: Install Dependencies
```pip install -r requirements.txt```

## Configuration
### Environment Variables
Create a `.env` file in the root directory and add the following environment variables:


```json
  # Database Configuration
  SQLALCHEMY_DATABASE_URI=your_database_uri_here

  # ImageKit Configuration
  IMAGE_KIT_PUBLIC_KEY=your_imagekit_public_key
  IMAGE_KIT_PRIVATE_KEY=your_imagekit_private_key
  IMAGE_KIT_URL=your_imagekit_url_endpoint
```

- `SQLALCHEMY_DATABASE_URI`: The URI for your database.

Examples: 
- **Database:** postgresql://user:password@localhost:5432/yourdatabase 
  > we are using ***elephantSQL***
- **ImageKit Credentials:** Obtain these from your ImageKit account dashboard.

### Google Sheets Credentials
Place your credentials.json file (downloaded from Google Cloud Console) in the root directory. This file is used to authenticate with the Google Sheets API.

## Database Setup
### Models
Ensure all models are defined in models.py:

- Styles: Contains style attributes and scores.
- Suggestion: Contains content and tips for each style.
- Images: Stores image metadata.
- Contact: Stores user contact information.

[!CAUTION] Only do this if you are making a new db
### Creating Tables
Run the script named `create_tables.py`

### Populating Data
Insert necessary data into the database tables using SQLModel sessions or direct SQL scripts.

## Running the Application
### Step 1: Start the FastAPI Server
Use Uvicorn to run the application:

```bash
uvicorn main:app --reload
```

The `--reload` flag enables auto-reload when code changes.
Access the application at `http://127.0.0.1:8000`.
### Step 2: Interactive API Docs
FastAPI provides interactive API documentation at:

Swagger UI: `http://127.0.0.1:8000/docs`
Redocly: `http://127.0.0.1:8000/redoc`

## API Endpoints
### 1. Retrieve Images
Endpoint: `GET /images`

Description: Retrieves images from ImageKit.

Sample Request:
```bash
curl -X GET http://127.0.0.1:8000/images
Response: JSON array of images.
```
### 2. Get Style Recommendations
Endpoint: POST /results

Description: Processes user preferences and returns recommended styles along with their data.

**Request Body:**
```json
{
  "data": ["style1", "style2", "style3"],
  "contact": {
    "fname": "John",
    "lname": "Doe",
    "email": "john.doe@example.com",
    "testing": true  // Optional: Include 'testing' to skip saving contact info
  }
}
```
- data: List of styles selected by the user.
- contact: User's contact information.

**Sample Request:**
```bash
curl -X POST http://127.0.0.1:8000/results \
-H "Content-Type: application/json" \
-d '{
      "data": ["abstract", "modern", "contemporary"],
      "contact": {
        "fname": "Jane",
        "lname": "Doe",
        "email": "jane.doe@example.com"
      }
    }'
```

**Response:**

```json
{
  "result": ["style_recommendation_1", "style_recommendation_2", "style_recommendation_3"],
  "output": [
    {
      "content": { /* Content from the Suggestion model */ },
      "images": [ /* Images from ImageKit */ ]
    }
    // ... more styles
  ]
}
```

## Testing
### Testing Mode
To prevent saving contact information during testing, include "testing": true in the contact field of your request.

**Example:**

```json
{
  "data": ["style1", "style2", "style3"],
  "contact": {
    "fname": "Test",
    "lname": "User",
    "email": "test.user@example.com",
    "testing": true
  }
}
```

### Running Tests
To run the test run the following command
```bash
pytest
```

## Troubleshooting
### Common Issues
- Environment Variables Not Set: Ensure all required environment variables are set in the .env file.
- Database Connection Errors: Verify the database URI and that the database server is running.
- Missing Credentials: Ensure credentials.json for Google Sheets API is in the root directory.
- Dependency Errors: Install all dependencies using pip install -r requirements.txt.

### Logging for Debugging
Check logs for detailed error messages and stack traces to diagnose issues.

## Appendix
### Full Code Structure
- main.py: The main application file containing the FastAPI app and endpoints.
- models.py: Contains SQLModel and Pydantic models.
- requirements.txt: Lists all Python dependencies.
- credentials.json: Google Sheets API credentials (do not commit this file to version control).
- .env: Environment variables configuration file.
- create_tables.py: Script to initialize the database tables.
### Dependencies
- FastAPI
- SQLModel
- Uvicorn
- Polars
- ImageKitIO
- gspread
- oauth2client
- Pydantic
- SQLAlchemy
- psycopg2-binary (or appropriate database driver)
- python-dotenv

Install all dependencies:

```bash
pip install -r requirements.txt
````

### Setting Up ImageKit
1. Create an Account: Sign up at [ImageKit.io](https://imagekit.io/).
2. Get API Keys: Obtain your public and private keys, and URL endpoint.
3. Set Environment Variables: Add the keys to your .env file.
### Setting Up Google Sheets API
1. Create a Project: Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable Google Sheets API: Enable the API for your project.
3. Create Service Account Credentials:
    - Navigate to APIs & Services > Credentials.
    - Click Create Credentials > Service Account.
    - Download the credentials.json file.

4. Share the Sheet with the Service Account: Share your Google Sheet with the service account email address.



## Authors
🧑🏽‍🦱 [**Sam Mathew**](https://github.com/dayumsam) 🧑🏽‍🦱 [**Vidit Teotia**](https://github.com/vidit0610)