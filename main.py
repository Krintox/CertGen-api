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
            if (name == 'qrCode'):
                continue
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

        return jsonify({"result_images": result_images_base64, "result_emails": result_emails})
    except Exception as e:
        # Log and handle errors
        return jsonify({"message": f"Error: {str(e)}"}), 500
    

@app.route('/post-data', methods=['POST'])
def post_data():
    data = request.json
    emails =  data['emails']
    images = data['images']
    links = data['s3ImageUrls']
    coordinates =data['coordinates']
    qr_coordinates = None
    for coordinate in coordinates:
        if coordinate['word'] == 'qrCode':
            qr_coordinates = coordinate['boundingBox']
            qr_coordinates_final = [qr_coordinates['left'],qr_coordinates['top'],qr_coordinates['width'],qr_coordinates['height']]
            break

    print(qr_coordinates_final)
    print(type(coordinates))
    ## qr_coordinates = coordinates['qr']
    qr_images = create_qr(images,qr_coordinates_final,links)
    return jsonify({"qr_images":qr_images,"final_emails":emails})
        

@app.route('/')
def index():
    return "server is running"

if __name__ == "__main__":
    app.run(debug=True)
