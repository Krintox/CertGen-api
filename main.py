from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import base64
import json
from excel import read_excel
from generate import generate_image
from qr_generator import create_qr

app = Flask(__name__)
CORS(app)

def infer(image, coordinates, excel_file):
    try:
        
        # Read the Excel file into a pandas DataFrame
        df, columns = read_excel(excel_file)

        # Process coordinates
        coordinate_list = []
        for coordinate_dict in coordinates:
            name = coordinate_dict['word']
            left = coordinate_dict['boundingBox']['left']
            top = coordinate_dict['boundingBox']['top']
            width = coordinate_dict['boundingBox']['width']
            height = coordinate_dict['boundingBox']['height']
            fontsize = coordinate_dict['fontSize']
            coordinate_list.append((name, left, top, width, height, fontsize))

        # Call generate_image function with image, coordinates, and data
        result_images, result_emails = generate_image(image, coordinate_list, df)
        
        return result_images, result_emails
    except Exception as e:
        # Log and handle errors
        return None, None

@app.route('/api', methods=['POST'])
def api():
    if 'image' not in request.files or 'excel' not in request.files:
        return jsonify({"message": "Missing image or Excel file"}), 400
    
    image_file = request.files['image']
    excel_file = request.files['excel']
    coordinates = json.loads(request.form['coordinates'])
    qr_coordinates = json.loads(request.form['qrCoordinates'])

    try:
        # Convert image file to PIL Image object
        image = Image.open(image_file)
        
        # Call inference function
        result_images, result_emails = infer(image, coordinates, excel_file)
        
        # Convert result_images to base64
        result_images_base64 = []
        for img in result_images:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            result_images_base64.append(base64.b64encode(buffered.getvalue()).decode())

        response = requests.post("http://localhost:3000/generated_images", 
                      json={"images": result_images_base64})
        
        links = response.json()['links']

        qr_images = create_qr(result_images_base64, qr_coordinates, links)

        return jsonify({"result_images": qr_images, "result_emails": result_emails})
    except Exception as e:
        # Log and handle errors
        return jsonify({"message": f"Error: {str(e)}"}), 500
    

@app.route('/')
def index():
    return "server is running"

if __name__ == "__main__":
    app.run(debug=False)
