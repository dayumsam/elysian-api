import os

from imagekitio import ImageKit

from dotenv import load_dotenv

load_dotenv()

# Imagekit config
imagekit = ImageKit(
    public_key=os.getenv('IMAGE_KIT_PUBLIC_KEY'),
    private_key=os.getenv('IMAGE_KIT_PRIVATE_KEY'),
    url_endpoint=os.getenv('IMAGE_KIT_URL')
)

# Folder with images
# Images should be in a folder with the name of the style
baseFolder = 'styles/'

# Loop through each folder
with os.scandir(baseFolder) as entries:
    for entry in entries:

        fileFolder = baseFolder + entry.name  # generate folder names

        # Loop through each file inside the folder
        with os.scandir(fileFolder) as files:
            for file in files:
                if file.is_file():
                    imgPath = fileFolder + "/" + file.name  # generate file names

                    # generate a tag from the folder name
                    # converting the name to lowercase and replacing spaces with an underscore
                    tag = entry.name.lower().replace(" ", "_")

                    # uploading to imagekit
                    upload = imagekit.upload(
                        file=open(imgPath, "rb"),
                        file_name=tag,
                        options={
                            "folder": "/elysian/",
                            'tags': [tag]
                        },
                    )

                    # print status of each upload
                    print("Upload binary", upload, end="\n\n")

print("done")  # end program
