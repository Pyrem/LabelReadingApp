"""
OCR Service - Extracts text from images using Tesseract OCR

This module handles the "AI" part of our application. It takes an image file
and uses Optical Character Recognition (OCR) to extract any text found in the image.

What is OCR?
-----------
OCR (Optical Character Recognition) is technology that converts images of text
into actual text strings that computers can process. Think of it like this:
- Image: A picture with pixels showing "WHISKEY"
- OCR Output: The string "WHISKEY" that we can search/compare

How Tesseract Works (Simplified):
---------------------------------
1. Load the image as a grid of pixels
2. Detect regions that look like text (dark shapes on light background)
3. Use a machine learning model trained on millions of text examples
4. Recognize each character by comparing patterns
5. Return the extracted text as a string

Why We Preprocess Images:
-------------------------
Raw images from cameras/phones often have:
- Color (unnecessary - text recognition only needs brightness)
- Low contrast (hard to distinguish text from background)
- Noise (random pixels that confuse the OCR)

Preprocessing improves accuracy by 10-20% on average.
"""

import pytesseract
from PIL import Image, ImageEnhance
import os


class OCRService:
    """
    Service class for handling OCR operations.

    Design Decision: Why a class instead of simple functions?
    - Encapsulation: All OCR logic in one place
    - Extensibility: Easy to add config options later (e.g., language settings)
    - Testability: Can mock this class in tests
    """

    def __init__(self):
        """
        Initialize the OCR service.

        Note: We could add configuration here like:
        - OCR language (default: English)
        - Tesseract path (if custom installation)
        - OCR confidence threshold

        For now, we use defaults to keep it simple.
        """
        pass

    def extract_text_from_image(self, image_path):
        """
        Extract all text from an image file.

        Parameters:
        -----------
        image_path : str
            Full path to the image file (e.g., "/tmp/label.jpg")

        Returns:
        --------
        dict
            {
                "success": bool,           # True if OCR worked
                "text": str,               # Extracted text (empty if failed)
                "error": str or None       # Error message if failed
            }

        Process Flow:
        -------------
        1. Validate image exists
        2. Load image with Pillow
        3. Preprocess (grayscale + contrast)
        4. Run Tesseract OCR
        5. Return extracted text
        """

        # Step 1: Validate the image file exists
        if not os.path.exists(image_path):
            return {
                "success": False,
                "text": "",
                "error": f"Image file not found: {image_path}"
            }

        try:
            # Step 2: Load the image using Pillow
            # Pillow (PIL) reads the image file and converts it to a Python object
            # that we can manipulate (resize, change colors, etc.)
            image = Image.open(image_path)

            # Step 3: Preprocess the image
            # This improves OCR accuracy significantly
            processed_image = self._preprocess_image(image)

            # Step 4: Run Tesseract OCR
            # pytesseract.image_to_string() is the main OCR function
            # It sends the image to Tesseract and returns extracted text
            #
            # The 'lang' parameter specifies language (default: 'eng' for English)
            # For alcohol labels, English is sufficient
            extracted_text = pytesseract.image_to_string(
                processed_image,
                lang='eng'
            )

            # Step 5: Clean up the extracted text
            # OCR often includes extra whitespace and newlines
            extracted_text = extracted_text.strip()

            # Check if we actually got any text
            if not extracted_text:
                return {
                    "success": False,
                    "text": "",
                    "error": "No text could be extracted from the image. The image may be too blurry, too dark, or contain no text."
                }

            # Success! Return the extracted text
            return {
                "success": True,
                "text": extracted_text,
                "error": None
            }

        except pytesseract.TesseractNotFoundError:
            # This happens if Tesseract OCR engine is not installed on the system
            return {
                "success": False,
                "text": "",
                "error": "Tesseract OCR is not installed. Please install it: sudo apt-get install tesseract-ocr"
            }

        except Exception as e:
            # Catch any other errors (corrupt image, permission issues, etc.)
            return {
                "success": False,
                "text": "",
                "error": f"Error processing image: {str(e)}"
            }

    def _preprocess_image(self, image):
        """
        Preprocess image to improve OCR accuracy.

        Parameters:
        -----------
        image : PIL.Image
            The image object loaded by Pillow

        Returns:
        --------
        PIL.Image
            Processed image optimized for OCR

        Preprocessing Steps:
        -------------------
        1. Convert to grayscale (remove color)
        2. Enhance contrast (make text stand out)

        Why These Steps?
        ----------------
        Grayscale: OCR doesn't need color information. Text recognition only
                   depends on brightness differences. Removing color reduces
                   noise and speeds up processing.

        Contrast: Increases the difference between text (usually dark) and
                  background (usually light). This makes edges sharper and
                  easier for OCR to detect.
        """

        # Convert to grayscale
        # 'L' mode = Luminosity (grayscale)
        # Each pixel becomes a single brightness value (0=black, 255=white)
        # Color images have 3 values per pixel (Red, Green, Blue)
        grayscale_image = image.convert('L')

        # Enhance contrast
        # Contrast enhancement makes dark pixels darker and light pixels lighter
        # Factor of 2.0 means we double the contrast
        #
        # Why 2.0? Through experimentation, this value works well for most labels
        # - Too low (1.0-1.5): Not much improvement
        # - Too high (3.0+): Can create artifacts and noise
        # - 2.0: Sweet spot for labels with printed text
        enhancer = ImageEnhance.Contrast(grayscale_image)
        enhanced_image = enhancer.enhance(2.0)

        return enhanced_image


# Create a singleton instance
# This means we create one OCRService object that the whole app uses
# instead of creating a new one for each request
ocr_service = OCRService()
