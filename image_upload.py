import os
from pathlib import Path
from imagekitio import ImageKit
from dotenv import load_dotenv
import logging
import sys

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Retrieve environment variables
public_key = os.getenv('IMAGE_KIT_PUBLIC_KEY')
private_key = os.getenv('IMAGE_KIT_PRIVATE_KEY')
url_endpoint = os.getenv('IMAGE_KIT_URL')

# Check if any of the environment variables are missing
missing_vars = []
if not public_key:
    missing_vars.append('IMAGE_KIT_PUBLIC_KEY')
if not private_key:
    missing_vars.append('IMAGE_KIT_PRIVATE_KEY')
if not url_endpoint:
    missing_vars.append('IMAGE_KIT_URL')

if missing_vars:
    logging.error(f'Missing environment variables: {", ".join(missing_vars)}')
    sys.exit(1)  # Exit the program with an error code

# ImageKit configuration
imagekit = ImageKit(
    public_key=public_key,
    private_key=private_key,
    url_endpoint=url_endpoint
)

# Base folder with images
base_folder = Path('styles')

# Loop through each subdirectory in the base folder
for style_folder in base_folder.iterdir():
    if style_folder.is_dir():
        # Generate a tag from the folder name
        tag = style_folder.name.lower().replace(" ", "_")
        logging.info(f'Processing folder: {style_folder.name}')

        # Loop through each file in the style folder
        for img_file in style_folder.iterdir():
            if img_file.is_file():
                try:
                    with img_file.open('rb') as file_stream:
                        # Upload to ImageKit
                        upload = imagekit.upload(
                            file=file_stream,
                            file_name=img_file.name,
                            options={
                                "folder": f"/elysian/{tag}/",
                                'tags': [tag]
                            },
                        )
                    logging.info(f'Uploaded {img_file.name} with tag "{tag}"')
                except Exception as e:
                    logging.error(f'Failed to upload {img_file.name}: {e}')

logging.info("Done")
