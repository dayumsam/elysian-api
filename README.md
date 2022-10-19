# Elysian API

## Description
> An API to generate interior design style preferences based on the user's inputs.

## Requirements
- python virtual environment

This API uses a propietary dataset to calculate preferred a users preferred interior design style based on the inputs given

It works in a few steps
1. The user chooses a group of images based on their style preferrence
   - The input is taken from a front end see [Elysian Frontend](https://github.com/dayumsam/elysian-frontend)
2. It is then sent to the the backend and fed into the preferred style generator
3. And from the list of styles it was provided the API can generate a ranked list based on similarites

## Install
  `pip install -r requirements.txt`

## Usage
Create and activate a virtual env
```python
python -m venv ./venv
Source venv/Scripts/activate
```

Install the dependencies
```python
pip install -r requirements.txt
```

Create a .env file with the required keys

Run the app using 
```Flask --app app run```

## Authors
🧑🏽‍🦱 [**Sam Mathew**](https://github.com/dayumsam)<br>
🧑🏽‍🦱 [**Vidit Teotia**](https://github.com/vidit0610)