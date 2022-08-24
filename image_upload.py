import base64
import os
import sys
from pathlib import Path

import sqlite3

from imagekitio import ImageKit
from dotenv import load_dotenv

load_dotenv()

imagekit = ImageKit(
    public_key = os.getenv('IMAGE_KIT_PUBLIC_KEY'),
    private_key = os.getenv('IMAGE_KIT_PRIVATE_KEY'),
    url_endpoint = os.getenv('IMAGE_KIT_URL')
)

connection = sqlite3.connect('database.db')
cur = connection.cursor()

# upload = imagekit.upload(
#     file=open("image.jpg", "rb"),
#     file_name='image.jpg',
# )

# print(upload, upload['response']['fileId'], upload['response']['url'])
# fileId = upload['response']['fileId']

# details = imagekit.get_file_details(fileId)
# print("File detail-", details, end="\n\n")

baseFolder = 'styles/'

with os.scandir(baseFolder) as entries:
    for entry in entries:
        # fileFolder = '%s%s/'% (baseFolder, entry.name)
        fileFolder = baseFolder + entry.name

        # print(fileFolder)

        with os.scandir(fileFolder) as files:
            for file in files:
                if file.is_file():
                    # print("--", file.name, "--", entry.name.lower())

                    # imgPath = '%s%s/%s'% (baseFolder, entry.name,file.name)
                    imgPath = fileFolder + "/" + file.name

                    upload = imagekit.upload(
                        file=open(imgPath, "rb"),
                        file_name=file.name,
                        options={
                            "folder" : "/elysian/",
                        },
                    )

                    print("Upload binary", upload, end="\n\n")

                    fileId = upload['response']['fileId']
                    url = upload['response']['url']
                    tags = entry.name.lower()

                    cur.execute("INSERT INTO images (file_id, url, tags) VALUES (?,?,?)",(fileId, url, tags))

connection.commit()
connection.close()


# details = imagekit.get_file_details(fileId)
# print("File detail-", details, end="\n\n")