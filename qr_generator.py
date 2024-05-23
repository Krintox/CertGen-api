import qrcode
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def create_qr(images, coordinates, links):
    """
    Generates and adds QR codes to the images.

    Args:
        images (list): List of base64 encoded images.
        coordinates (list): List of 4-dimensional arrays (x, y, width, height) to place the QR code on the image.
        links (list): List of links to be encoded in the QR codes.

    Returns:
        list: List of base64 encoded images with QR codes added.
    """

    def base64_to_image(base64_str):
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def image_to_base64(img):
        _, buffer = cv2.imencode('.png', img)
        img_bytes = buffer.tobytes()
        return base64.b64encode(img_bytes).decode('utf-8')

    output_images = []

    for img_base64, coord, link in zip(images, coordinates, links):
        # Decode the base64 image
        img = base64_to_image(img_base64)

        # Create the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)

        # Convert the QR code to an image
        qr_img = qr.make_image(fill='black', back_color='white')
        qr_img = qr_img.resize((coord[2], coord[3]))  # Resize to fit the given coordinates
        qr_img = cv2.cvtColor(np.array(qr_img), cv2.COLOR_RGB2BGR)

        # Place the QR code on the original image
        x, y, w, h = coord
        img[y:y+h, x:x+w] = qr_img

        # Encode the final image back to base64
        output_img_base64 = image_to_base64(img)
        output_images.append(output_img_base64)

    return output_images

    
    
