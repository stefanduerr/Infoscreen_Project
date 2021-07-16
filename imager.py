# Store Pdf with convert_from_path function
from typing import List, Any

from pdf2image import convert_from_path


def create_images(name):
    filepath = '/Users/lukas.schweighofer/PycharmProjects/flaskProject/static/uploads/' + name
    images: List[any] = convert_from_path(filepath)
    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save('/Users/lukas.schweighofer/PycharmProjects/flaskProject/static/uploads/imggg' + str(i) + '.jpg', 'JPEG')

create_images('presentation3.pdf')

