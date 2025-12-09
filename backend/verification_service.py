"""
Verification Service - Compares form data with extracted OCR text

This module handles the "matching logic" of our application. It takes the user's
form inputs and the text extracted from the label image, then determines if they match.

Matching Strategy:
------------------
We use SUBSTRING MATCHING instead of exact matching because:
1. OCR isn't perfect - it may add/remove spaces or punctuation
2. Labels might have extra words (e.g., "Old Tom Distillery" vs "Tom")
3. Case differences shouldn't matter ("BOURBON" vs "bourbon")

Example:
--------
Form Input: "Old Tom Distillery"
OCR Text: "OLD TOM DISTILLERY\nKENTUCKY STRAIGHT BOURBON WHISKEY\n45% ALC/VOL"
Match? YES - "old tom distillery" is found in the lowercase version of OCR text

Trade-offs:
-----------
Pros:
+ More tolerant of OCR errors
+ Handles formatting differences
+ Reduces false negatives (saying "no match" when there actually is one)

Cons:
- Might allow some false positives (saying "match" when it shouldn't)
- Example: "Tom" would match "Tom's Distillery" (probably OK)
- Example: "45" would match "450" (we handle this with better patterns)

We document these trade-offs and keep matching simple per project requirements.
"""

import re


class VerificationService:
    """
    Service class for verifying label information against form data.

    Design Decision: Class vs Functions
    Similar to OCRService, we use a class for:
    - Grouping related verification methods
    - Easy to add configuration (strictness levels)
    - Can be extended with more sophisticated matching later
    """

    def __init__(self):
        """
        Initialize the verification service.

        We could add configuration here like:
        - Matching strictness level (strict, medium, loose)
        - Custom regex patterns
        - Required vs optional fields

        For now, we keep it simple with default behavior.
        """
        pass

    def verify_label(self, form_data, ocr_text):
        """
        Verify that form data matches the OCR extracted text.

        Parameters:
        -----------
        form_data : dict
            User's form inputs:
            {
                "brand_name": str,
                "product_type": str,
                "abv": str,
                "net_contents": str (optional)
            }

        ocr_text : str
            Raw text extracted from the label image by OCR

        Returns:
        --------
        dict
            {
                "overall_match": bool,        # True if ALL required fields match
                "details": {
                    "brand_name": {
                        "match": bool,
                        "expected": str,
                        "found": str or None
                    },
                    # ... similar for other fields
                },
                "ocr_text": str              # Include for debugging
            }

        Verification Process:
        ---------------------
        1. Normalize both form inputs and OCR text (lowercase, strip whitespace)
        2. Check each field:
           - Brand Name: substring match
           - Product Type: substring match
           - ABV: regex pattern match for percentage
           - Net Contents: regex pattern match for volume
           - Government Warning: check for "GOVERNMENT WARNING" (optional)
        3. Combine results into overall match status
        """

        # Normalize the OCR text once (we'll use this for all comparisons)
        # Normalization: convert to lowercase and remove extra whitespace
        # This makes matching case-insensitive and whitespace-tolerant
        normalized_ocr = self._normalize_text(ocr_text)

        # Initialize results structure
        results = {
            "overall_match": True,  # Assume success, set to False if any field fails
            "details": {},
            "ocr_text": ocr_text  # Include for debugging/transparency
        }

        # Check Brand Name (REQUIRED)
        results["details"]["brand_name"] = self._check_brand_name(
            form_data.get("brand_name", ""),
            normalized_ocr
        )

        # Check Product Type (REQUIRED)
        results["details"]["product_type"] = self._check_product_type(
            form_data.get("product_type", ""),
            normalized_ocr
        )

        # Check ABV (REQUIRED)
        results["details"]["abv"] = self._check_abv(
            form_data.get("abv", ""),
            normalized_ocr
        )

        # Check Net Contents (OPTIONAL - only if provided)
        if form_data.get("net_contents"):
            results["details"]["net_contents"] = self._check_net_contents(
                form_data.get("net_contents"),
                normalized_ocr
            )

        # Check Government Warning (OPTIONAL - simple check)
        results["details"]["government_warning"] = self._check_government_warning(
            normalized_ocr
        )

        # Determine overall match
        # Required fields: brand_name, product_type, abv
        # Optional fields don't affect overall match
        required_fields = ["brand_name", "product_type", "abv"]
        for field in required_fields:
            if not results["details"][field]["match"]:
                results["overall_match"] = False
                break

        return results

    def _normalize_text(self, text):
        """
        Normalize text for comparison.

        Parameters:
        -----------
        text : str
            Raw text to normalize

        Returns:
        --------
        str
            Normalized text (lowercase, stripped)

        Why Normalize?
        --------------
        - "BOURBON" and "bourbon" should match
        - "  Whiskey  " and "Whiskey" should match
        - Makes matching more reliable
        """
        return text.lower().strip()

    def _check_brand_name(self, brand_name, normalized_ocr):
        """
        Check if brand name appears in OCR text.

        Matching Method: Case-insensitive substring search

        Parameters:
        -----------
        brand_name : str
            User's input from form
        normalized_ocr : str
            Lowercase OCR text

        Returns:
        --------
        dict
            {"match": bool, "expected": str, "found": str or None}
        """
        if not brand_name:
            return {
                "match": False,
                "expected": "",
                "found": None,
                "error": "Brand name not provided in form"
            }

        normalized_brand = self._normalize_text(brand_name)

        # Simple substring check
        # Example: "tom" in "old tom distillery" → True
        if normalized_brand in normalized_ocr:
            return {
                "match": True,
                "expected": brand_name,
                "found": normalized_brand
            }
        else:
            return {
                "match": False,
                "expected": brand_name,
                "found": None,
                "error": f"Brand name '{brand_name}' not found in label"
            }

    def _check_product_type(self, product_type, normalized_ocr):
        """
        Check if product type appears in OCR text.

        Matching Method: Case-insensitive substring search

        Examples:
        ---------
        - Form: "Bourbon Whiskey"
          OCR: "KENTUCKY STRAIGHT BOURBON WHISKEY"
          Result: MATCH ✓

        - Form: "IPA"
          OCR: "INDIA PALE ALE"
          Result: NO MATCH ✗ (different words)

        Note: We use substring matching, not exact matching.
        The user could enter "Bourbon" and it would match "Bourbon Whiskey".
        """
        if not product_type:
            return {
                "match": False,
                "expected": "",
                "found": None,
                "error": "Product type not provided in form"
            }

        normalized_type = self._normalize_text(product_type)

        if normalized_type in normalized_ocr:
            return {
                "match": True,
                "expected": product_type,
                "found": normalized_type
            }
        else:
            return {
                "match": False,
                "expected": product_type,
                "found": None,
                "error": f"Product type '{product_type}' not found in label"
            }

    def _check_abv(self, abv, normalized_ocr):
        """
        Check if ABV (alcohol percentage) appears in OCR text.

        Matching Method: Regex pattern search for number + % symbol

        Why Regex Instead of Substring?
        --------------------------------
        ABV can appear in different formats on labels:
        - "45%"
        - "45.0%"
        - "45% ALC/VOL"
        - "45 %"
        - "Alc. 45% by Vol."

        Regex Pattern: r'\\b' + abv_number + r'(?:\\.0)?\\s*%'
        Breakdown:
        - \\b = word boundary (ensures we match whole number)
        - 45 = the actual number we're looking for
        - (?:\\.0)? = optionally match ".0" (e.g., "45.0")
        - \\s* = optional whitespace
        - % = the percent symbol

        Examples:
        ---------
        Form: "45"
        Pattern matches: "45%", "45.0%", "45 %"
        Doesn't match: "450%", "145%", "4.5%"
        """
        if not abv:
            return {
                "match": False,
                "expected": "",
                "found": None,
                "error": "ABV not provided in form"
            }

        # Clean the ABV input (remove % if user included it)
        abv_clean = abv.strip().replace('%', '').strip()

        # Build regex pattern
        # \\b ensures we match whole numbers (45 but not 145 or 450)
        # (?:\\.0)? optionally matches ".0" for "45.0%"
        # \\s* allows optional space before %
        pattern = r'\b' + re.escape(abv_clean) + r'(?:\.0)?\s*%'

        # Search for pattern in OCR text
        match = re.search(pattern, normalized_ocr)

        if match:
            return {
                "match": True,
                "expected": abv + "%",
                "found": match.group(0)  # The actual matched text
            }
        else:
            return {
                "match": False,
                "expected": abv + "%",
                "found": None,
                "error": f"ABV '{abv}%' not found in label"
            }

    def _check_net_contents(self, net_contents, normalized_ocr):
        """
        Check if net contents (volume) appears in OCR text.

        Matching Method: Flexible regex pattern for volume

        Volume can appear in many formats:
        - "750 mL"
        - "750mL"
        - "750 ML"
        - "750ml"
        - "12 fl oz"
        - "12 FL OZ"

        Regex Strategy:
        ---------------
        1. Extract the number (e.g., "750")
        2. Extract the unit (e.g., "ml", "oz")
        3. Build a flexible pattern that allows:
           - Optional space between number and unit
           - Case-insensitive unit matching
           - Optional periods in unit (e.g., "fl. oz")
        """
        if not net_contents:
            # This field is optional, so no error if not provided
            return {
                "match": True,
                "expected": "Not provided",
                "found": "Not checked"
            }

        normalized_contents = self._normalize_text(net_contents)

        # Extract number and unit using regex
        # Pattern: one or more digits, optional space, then letters/periods
        volume_match = re.search(r'(\d+(?:\.\d+)?)\s*([a-z.\s]+)', normalized_contents)

        if not volume_match:
            return {
                "match": False,
                "expected": net_contents,
                "found": None,
                "error": "Could not parse volume format from form input"
            }

        number = volume_match.group(1)  # e.g., "750"
        unit = volume_match.group(2).strip()  # e.g., "ml"

        # Build flexible pattern
        # Allow optional space and case-insensitive unit
        pattern = number + r'\s*' + re.escape(unit)

        # Search in OCR text
        match = re.search(pattern, normalized_ocr, re.IGNORECASE)

        if match:
            return {
                "match": True,
                "expected": net_contents,
                "found": match.group(0)
            }
        else:
            return {
                "match": False,
                "expected": net_contents,
                "found": None,
                "error": f"Net contents '{net_contents}' not found in label"
            }

    def _check_government_warning(self, normalized_ocr):
        """
        Check if government warning statement appears on label.

        Matching Method: Simple substring search for "government warning"

        Note from Requirements:
        -----------------------
        Per project specs, we do NOT check for exact warning text
        (that's a bonus feature we're skipping). We just check if
        "GOVERNMENT WARNING" appears somewhere on the label.

        This is sufficient for core requirements.
        """
        # Look for "government warning" in the normalized (lowercase) text
        if "government warning" in normalized_ocr:
            return {
                "match": True,
                "expected": "Government Warning Present",
                "found": "GOVERNMENT WARNING"
            }
        else:
            return {
                "match": False,
                "expected": "Government Warning Present",
                "found": None,
                "error": "Government warning statement not found on label"
            }


# Create singleton instance
verification_service = VerificationService()
