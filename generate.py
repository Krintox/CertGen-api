from PIL import ImageDraw, ImageFont
import math
import numpy as np

def preprocess_dataframe(data):
    """
    Preprocesses the DataFrame to create a dictionary mapping column names to their corresponding indices.

    Args:
        data (pd.DataFrame): DataFrame containing the data to be written onto the images.

    Returns:
        dict: A dictionary mapping column names to their corresponding indices.
    """
    return {column.lower(): index for index, column in enumerate(data.columns)}

def round_to_nearest_common_font_size(font_size):
    """
    Rounds the font size to the nearest common point size.

    Args:
        font_size (float): The font size to be rounded.

    Returns:
        int: The rounded font size.
    """
    common_font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64]
    return min(common_font_sizes, key=lambda x: abs(x - font_size))

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
    column_indices = preprocess_dataframe(data)

    for index, row in data.iterrows():
        row_data = {}
        
        # Extract data corresponding to required text labels using preprocessed column indices
        for text, _, _, _, _, _ in required_predictions:
            if text.lower() in column_indices:
                row_data[text.lower()] = str(row.iloc[column_indices[text.lower()]])
        
        # Create a copy of the base image for each row
        certificate_image = image.copy()
        draw = ImageDraw.Draw(certificate_image)

        # Extract email address (if available) outside the loop
        email = row.get(email_column_name, "")
        if isinstance(email, str) and email.strip():
            email_list.append(email)
        else:
            email_list.append('')  # Append empty string if email is not available or not a valid string

        # Write data onto the image at specified locations
        for text, left, top, width, height, font_size in required_predictions:
            if text.lower() in row_data:
                data_value = row_data[text.lower()]
                
                # Round off values to lowest integer
                left = math.floor(left)
                top = math.floor(top)
                width = math.floor(width)
                height = math.floor(height)
                font_size = round_to_nearest_common_font_size(font_size)

                # Load font with dynamically calculated font size
                text_font = ImageFont.truetype('George-SemiBold.ttf', size=font_size)

                # Calculate maximum font size that fits within the bounding box
                max_font_size = int(min(width, height) * 0.8)  # Adjust this factor as needed

                # Calculate text dimensions for the maximum font size
                text_width, text_height = draw.textbbox((0, 0), data_value, font=text_font)[2:]

                # Reduce font size if the text doesn't fit within the bounding box
                while text_width > width or text_height > height:
                    max_font_size -= 1
                    text_font = ImageFont.truetype('George-SemiBold.ttf', size=max_font_size)
                    text_width, text_height = draw.textbbox((0, 0), data_value, font=text_font)[2:]

                # Choose the final font size based on comparison with the input font size
                final_font_size = min(font_size, max_font_size)

                # Load font with the final font size
                text_font = ImageFont.truetype('George-SemiBold.ttf', size=final_font_size)

                # Calculate text position for centered placement
                text_x = left + (width - text_width) / 2
                text_y = top + (height - text_height) / 2

                # Write the text onto the image at calculated coordinates
                draw.text((text_x, text_y), data_value, fill='black', font=text_font)

        # Append the modified image to the list
        all_row_images.append(certificate_image)

    return all_row_images, email_list