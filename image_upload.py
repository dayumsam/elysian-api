import base64
import os
import sys
from pathlib import Path

from imagekitio import ImageKit

from dotenv import load_dotenv

load_dotenv()

imagekit = ImageKit(
    public_key=os.getenv('IMAGE_KIT_PUBLIC_KEY'),
    private_key=os.getenv('IMAGE_KIT_PRIVATE_KEY'),
    url_endpoint=os.getenv('IMAGE_KIT_URL')
)

baseFolder = 'styles/'

with os.scandir(baseFolder) as entries:
    for entry in entries:

        fileFolder = baseFolder + entry.name

        with os.scandir(fileFolder) as files:
            for file in files:
                if file.is_file():
                    imgPath = fileFolder + "/" + file.name

                    tag = entry.name.lower().replace(" ", "_")

                    upload = imagekit.upload(
                        file=open(imgPath, "rb"),
                        file_name=tag,
                        options={
                            "folder": "/elysian/",
                            'tags': [tag]
                        },
                    )

                    print("Upload binary", upload, end="\n\n")

print("done")
