"""
Flask Application - Main Entry Point

This is the main Flask web server that handles HTTP requests from the frontend.
It coordinates between the OCR service and verification service.

What is Flask?
--------------
Flask is a lightweight web framework for Python. It lets us:
- Define URL routes (e.g., /verify)
- Handle HTTP requests (GET, POST)
- Return JSON responses
- Serve static files (HTML, CSS, JS)

Think of Flask as a traffic controller:
1. Browser sends request to http://localhost:5000/verify
2. Flask receives it and calls the appropriate function
3. Function processes the request (OCR + verification)
4. Flask sends back the JSON response to browser

Request Flow:
-------------
Browser → POST /verify → Flask → OCR Service → Verification Service → JSON Response
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile

# Import our services
from ocr_service import ocr_service
from verification_service import verification_service


# Initialize Flask app
# __name__ tells Flask where to look for templates/static files
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our frontend (HTML page) to make requests to this backend
# even when they're running on different ports during development
#
# Example: Frontend on http://localhost:8000 can call backend on http://localhost:5000
# Without CORS, browser blocks this for security reasons
CORS(app)

# Configuration
# In production, you'd use environment variables, but for simplicity we hardcode these
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image formats


def allowed_file(filename):
    """
    Check if uploaded file has an allowed extension.

    Parameters:
    -----------
    filename : str
        Name of the uploaded file (e.g., "label.jpg")

    Returns:
    --------
    bool
        True if file extension is allowed, False otherwise

    Why Check Extensions?
    ---------------------
    Security: Prevents users from uploading executable files
    Correctness: OCR only works on image files
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """
    Serve the main HTML page.

    Route: GET /
    Returns: index.html from frontend folder

    This is called when user visits http://localhost:5000/
    """
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/verify', methods=['POST'])
def verify():
    """
    Main API endpoint for label verification.

    Route: POST /verify
    Content-Type: multipart/form-data

    Expected Request Data:
    ----------------------
    - brand_name: string (required)
    - product_type: string (required)
    - abv: string (required)
    - net_contents: string (optional)
    - image: file upload (required)

    Response:
    ---------
    JSON object:
    {
        "success": bool,
        "overall_match": bool,
        "details": {...},
        "ocr_text": string,
        "error": string (if failed)
    }

    Process Flow:
    -------------
    1. Validate request (check image present, form fields filled)
    2. Save uploaded image temporarily
    3. Extract text with OCR service
    4. Verify text with verification service
    5. Clean up temporary file
    6. Return results as JSON
    """

    # Step 1: Validate that an image was uploaded
    if 'image' not in request.files:
        return jsonify({
            "success": False,
            "error": "No image file provided. Please upload an image of the alcohol label."
        }), 400  # 400 = Bad Request status code

    file = request.files['image']

    # Check if user actually selected a file (not just submitted empty form)
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "No file selected. Please choose an image file."
        }), 400

    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    # Step 2: Get form data
    # request.form contains the text fields from the form
    form_data = {
        "brand_name": request.form.get('brand_name', '').strip(),
        "product_type": request.form.get('product_type', '').strip(),
        "abv": request.form.get('abv', '').strip(),
        "net_contents": request.form.get('net_contents', '').strip()
    }

    # Validate required fields
    required_fields = ['brand_name', 'product_type', 'abv']
    missing_fields = [field for field in required_fields if not form_data[field]]

    if missing_fields:
        return jsonify({
            "success": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    # Step 3: Save uploaded image temporarily
    # We need to save it to disk because pytesseract reads from file path
    #
    # secure_filename() cleans the filename to prevent security issues
    # Example: "../../etc/passwd" becomes "etc_passwd"
    filename = secure_filename(file.filename)

    # Use system temp directory (automatically cleaned up by OS)
    # This is better than creating our own uploads folder
    temp_dir = tempfile.gettempdir()
    temp_filepath = os.path.join(temp_dir, filename)

    try:
        # Save the uploaded file
        file.save(temp_filepath)

        # Step 4: Extract text with OCR
        ocr_result = ocr_service.extract_text_from_image(temp_filepath)

        # Check if OCR succeeded
        if not ocr_result["success"]:
            return jsonify({
                "success": False,
                "error": ocr_result["error"]
            }), 500  # 500 = Internal Server Error

        # Step 5: Verify the extracted text against form data
        verification_result = verification_service.verify_label(
            form_data,
            ocr_result["text"]
        )

        # Step 6: Clean up - delete temporary file
        # Always clean up, even if there was an error
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        # Step 7: Return success response
        return jsonify({
            "success": True,
            "overall_match": verification_result["overall_match"],
            "details": verification_result["details"],
            "ocr_text": verification_result["ocr_text"]
        }), 200  # 200 = Success status code

    except Exception as e:
        # Catch any unexpected errors
        # Always clean up temp file before returning error
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Route: GET /health
    Returns: {"status": "ok"}

    This is useful for:
    - Deployment platforms to check if app is running
    - Load balancers to verify server health
    - Quick testing that server is up

    Usage: curl http://localhost:5000/health
    """
    return jsonify({"status": "ok"}), 200


# Error handlers
@app.errorhandler(413)
def file_too_large(e):
    """
    Handle file size exceeded error.

    413 = Request Entity Too Large
    This is triggered when uploaded file exceeds MAX_CONTENT_LENGTH
    """
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 16 MB."
    }), 413


@app.errorhandler(404)
def not_found(e):
    """
    Handle 404 Not Found errors.

    This is triggered when user visits a non-existent route.
    """
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """
    Handle 500 Internal Server Error.

    This catches any unhandled exceptions that occur during request processing.
    """
    return jsonify({
        "success": False,
        "error": "Internal server error. Please check server logs."
    }), 500


# Run the app
if __name__ == '__main__':
    """
    Start the Flask development server.

    Settings:
    ---------
    - host='0.0.0.0': Accept connections from any IP (not just localhost)
                      This allows access from other devices on network
    - port=5000: Run on port 5000 (default Flask port)
    - debug=True: Enable debug mode:
                  * Auto-reloads when code changes
                  * Shows detailed error pages
                  * NOT for production!

    To run: python app.py
    Then visit: http://localhost:5000
    """
    app.run(host='0.0.0.0', port=5000, debug=True)
