import qrcode
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def base64_to_image(base64_str):
    img_data = base64.b64decode(base64_str)
    img = Image.open(BytesIO(img_data))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def image_to_base64(img):
    _, buffer = cv2.imencode('.png', img)
    img_bytes = buffer.tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')

def create_qr(images, coordinates, links):
    """
    Generates and adds QR codes to the images.

    Args:
        images (list): List of base64 encoded images.
        coordinates (tuple): A 4-dimensional array (x, y, width, height) to place the QR code on each image.
        links (list): List of links to be encoded in the QR codes.

    Returns:
        list: List of base64 encoded images with QR codes added.
    """

    output_images = []
    x, y, w, h = coordinates
    x=int(x)
    y=int(y)
    w=int(w)
    h=int(h)

    for img_base64, link in zip(images, links):
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
        qr_img = qr_img.convert('RGB')  # Ensure the QR image is in RGB mode
        qr_img = np.array(qr_img)

        # Resize the QR code to fit the given coordinates
        qr_img = cv2.resize(qr_img, (w, h))

        # Ensure the QR code and original image have the same number of color channels
        if qr_img.shape[2] == 3:  # QR code image has 3 color channels
            qr_img_rgb = qr_img
        else:  # QR code image has a single channel (grayscale)
            qr_img_rgb = cv2.cvtColor(qr_img, cv2.COLOR_GRAY2BGR)

        cv2.imwrite('qr.jpg', qr_img_rgb)
        # Place the QR code on the original image
        img[y:y+h, x:x+w] = qr_img_rgb

        cv2.imwrite('output.jpg', img)

        # Encode the final image back to base64
        output_img_base64 = image_to_base64(img)
        output_images.append(output_img_base64)

    return output_images
