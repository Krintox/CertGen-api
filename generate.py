from PIL import ImageDraw, ImageFont
import math

def generate_image(image, required_predictions, data, email_column_name="email"):
    """
    Writes details onto a certificate image for each row in the DataFrame.

    Args:
        image (PIL.Image): The base certificate image.
        required_predictions (list): List of tuples containing (text, left, top, width, height, font size) information.
        data (pd.DataFrame): DataFrame containing the data to be written onto the images.
        email_column_name (str, optional): The column name in the DataFrame containing email addresses. Defaults to "email".

    Returns:
        tuple: A tuple containing two lists:
            - list of PIL.Image: List of modified certificate images for each row.
            - list of str: List of email addresses extracted from the DataFrame.
    """

    all_row_images = []
    email_list = []
    data_columns = data.columns.tolist()
    columns = [word.lower() for word in data_columns]
    print(columns)

    for index, row in data.iterrows():
        row_data = {}
        # Extract data corresponding to required text labels (case-insensitive)
        for text, _, _, _, _, _ in required_predictions:
            if text.lower() in columns:
                column_name = text.lower() if text.lower() in row.index else text.capitalize()
                row_data[text.lower()] = str(row[column_name])
        
        print(required_predictions)
        # Create a copy of the base image for each row
        certificate_image = image.copy()
        draw = ImageDraw.Draw(certificate_image)

        # Extract email address (if available)
        email = row.get(email_column_name, "")
        email_list.append(email)

        # Write data onto the image at specified locations
        for text, left, top, width, height, font_size in required_predictions:
            if text.lower() in row_data:
                data_value = row_data[text.lower()]
                
                #Round off values to lowest integer
                left = math.floor(left)
                top = math.floor(top)
                width = math.floor(width)
                height = math.floor(height)
                font_size = math.floor(font_size)

                # Load and adjust font size
                text_font = ImageFont.truetype('Montesart.ttf', size=font_size)

                text_bbox = draw.textbbox([0, 0, 0, 0], text=data_value, font=text_font)
                text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

                # Calculate text position for centered placement
                text_x = left + (width - text_width) / 2
                text_y = top + (height - text_height) / 2

                # Write the text onto the image at calculated coordinates
                draw.text((text_x, text_y), data_value, fill='black', font=text_font)

        # Append the modified image to the list
        all_row_images.append(certificate_image)

    print("Successfully generated images.")
    return all_row_images, email_list
