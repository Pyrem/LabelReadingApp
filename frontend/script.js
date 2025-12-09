/**
 * Alcohol Label Verification - Frontend JavaScript
 *
 * This file handles all frontend interactivity:
 * - Form submission
 * - Image preview
 * - API communication
 * - Results display
 *
 * JavaScript Concepts Used:
 * - Event listeners (responding to user actions)
 * - Fetch API (making HTTP requests)
 * - FormData (sending files to server)
 * - DOM manipulation (updating HTML dynamically)
 * - Async/await (handling asynchronous operations)
 */

// ===== WAIT FOR DOM TO LOAD =====

/*
    DOMContentLoaded event fires when HTML is fully loaded
    We wait for this before accessing HTML elements

    Why? If we try to access elements before they exist, we get errors
*/
document.addEventListener('DOMContentLoaded', function() {
    // Now all HTML elements are available

    // Get references to HTML elements
    const form = document.getElementById('verificationForm');
    const imageInput = document.getElementById('labelImage');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const loading = document.getElementById('loading');
    const submitBtn = document.getElementById('submitBtn');
    const resultsSection = document.getElementById('resultsSection');
    const tryAgainBtn = document.getElementById('tryAgainBtn');
    const errorDisplay = document.getElementById('errorDisplay');
    const dismissErrorBtn = document.getElementById('dismissErrorBtn');

    // ===== IMAGE PREVIEW FUNCTIONALITY =====

    /**
     * Show preview of selected image
     *
     * Event: 'change' fires when user selects a file
     * FileReader API reads the file and converts it to a data URL
     */
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];  // Get the selected file

        // Check if a file was actually selected
        if (file) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
            if (!validTypes.includes(file.type)) {
                showError('Please select a valid image file (JPEG, PNG, or GIF)');
                imageInput.value = '';  // Clear the input
                return;
            }

            // Validate file size (max 16MB to match backend)
            const maxSize = 16 * 1024 * 1024;  // 16MB in bytes
            if (file.size > maxSize) {
                showError('File too large. Maximum size is 16 MB.');
                imageInput.value = '';
                return;
            }

            // Use FileReader to read the file
            const reader = new FileReader();

            /**
             * FileReader is an async API that reads files
             * onload fires when file is successfully read
             */
            reader.onload = function(e) {
                // e.target.result contains the file data as a data URL
                // data URL format: data:image/jpeg;base64,/9j/4AAQ...
                previewImg.src = e.target.result;
                imagePreview.style.display = 'block';
            };

            // Start reading the file as a data URL
            reader.readAsDataURL(file);
        } else {
            // No file selected, hide preview
            imagePreview.style.display = 'none';
        }
    });

    // ===== FORM SUBMISSION =====

    /**
     * Handle form submission
     *
     * e.preventDefault() stops the default form submission behavior
     * (which would cause a page reload)
     */
    form.addEventListener('submit', async function(e) {
        e.preventDefault();  // Stop page reload

        // Hide any previous results or errors
        resultsSection.style.display = 'none';
        errorDisplay.style.display = 'none';

        // Show loading indicator
        loading.style.display = 'block';
        submitBtn.disabled = true;

        try {
            /**
             * Create FormData object from the form
             *
             * FormData automatically collects all form inputs
             * including files, and formats them as multipart/form-data
             * which is required for file uploads
             */
            const formData = new FormData(form);

            /**
             * Send POST request to backend
             *
             * fetch() is the modern way to make HTTP requests
             * It returns a Promise that resolves with the response
             */
            const response = await fetch('/verify', {
                method: 'POST',
                body: formData
                // Note: Don't set Content-Type header manually for FormData
                // Browser sets it automatically with correct boundary
            });

            /**
             * Parse JSON response
             *
             * response.json() returns another Promise
             * We await it to get the actual data
             */
            const data = await response.json();

            // Hide loading indicator
            loading.style.display = 'none';
            submitBtn.disabled = false;

            /**
             * Handle response based on HTTP status code
             */
            if (response.ok) {
                // Success (status 200)
                if (data.success) {
                    displayResults(data);
                } else {
                    showError(data.error || 'Verification failed');
                }
            } else {
                // Error (status 400, 500, etc.)
                showError(data.error || 'Server error occurred');
            }

        } catch (error) {
            /**
             * Catch network errors or other exceptions
             *
             * This includes:
             * - Network connection failed
             * - Server not running
             * - Invalid JSON response
             */
            loading.style.display = 'none';
            submitBtn.disabled = false;
            showError('Network error: ' + error.message);
        }
    });

    // ===== RESULTS DISPLAY =====

    /**
     * Display verification results
     *
     * @param {Object} data - Response data from backend
     *   {
     *     success: true,
     *     overall_match: true/false,
     *     details: {...},
     *     ocr_text: "..."
     *   }
     */
    function displayResults(data) {
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Display overall status
        const overallStatus = document.getElementById('overallStatus');
        if (data.overall_match) {
            overallStatus.className = 'status-banner success';
            overallStatus.innerHTML = `
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✓</div>
                <div>Label Verification Successful</div>
                <div style="font-size: 0.9rem; font-weight: normal; margin-top: 0.5rem;">
                    All required information matches between the form and the label.
                </div>
            `;
        } else {
            overallStatus.className = 'status-banner failure';
            overallStatus.innerHTML = `
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">✗</div>
                <div>Label Verification Failed</div>
                <div style="font-size: 0.9rem; font-weight: normal; margin-top: 0.5rem;">
                    Some information does not match. See details below.
                </div>
            `;
        }

        // Display detailed field results
        const detailedResults = document.getElementById('detailedResults');
        detailedResults.innerHTML = '';  // Clear previous results

        /**
         * Iterate through each field in the details object
         *
         * Object.entries() converts object to array of [key, value] pairs
         * Example: { brand_name: {...}, abv: {...} }
         *       → [['brand_name', {...}], ['abv', {...}]]
         */
        for (const [field, result] of Object.entries(data.details)) {
            const resultItem = createResultItem(field, result);
            detailedResults.appendChild(resultItem);
        }

        // Display OCR text
        const ocrText = document.getElementById('ocrText');
        ocrText.textContent = data.ocr_text || 'No text extracted';
    }

    /**
     * Create a result item element for a field
     *
     * @param {string} field - Field name (e.g., 'brand_name')
     * @param {Object} result - Field result data
     * @returns {HTMLElement} - Div element with result display
     */
    function createResultItem(field, result) {
        const div = document.createElement('div');
        div.className = 'result-item';

        // Determine CSS class and icon based on match status
        let cssClass, icon;
        if (result.match) {
            cssClass = 'match';
            icon = '✓';
        } else if (field === 'government_warning' || field === 'net_contents') {
            // Optional fields - show in blue
            cssClass = 'optional';
            icon = 'ℹ';
        } else {
            cssClass = 'no-match';
            icon = '✗';
        }

        div.classList.add(cssClass);

        // Format field name for display
        const fieldName = formatFieldName(field);

        // Build HTML content
        let html = `
            <h4>
                <span class="icon">${icon}</span>
                ${fieldName}
            </h4>
        `;

        // Add field details
        html += '<div class="field-details">';

        if (result.match) {
            html += `<strong>Status:</strong> Match found<br>`;
            html += `<strong>Expected:</strong> ${result.expected}<br>`;
            if (result.found) {
                html += `<strong>Found in label:</strong> "${result.found}"`;
            }
        } else {
            html += `<strong>Status:</strong> No match<br>`;
            html += `<strong>Expected:</strong> ${result.expected}<br>`;
            if (result.error) {
                html += `<strong>Issue:</strong> ${result.error}`;
            }
        }

        html += '</div>';
        div.innerHTML = html;

        return div;
    }

    /**
     * Format field name for display
     *
     * Converts: "brand_name" → "Brand Name"
     *           "abv" → "ABV"
     */
    function formatFieldName(field) {
        const nameMap = {
            'brand_name': 'Brand Name',
            'product_type': 'Product Class/Type',
            'abv': 'Alcohol Content (ABV)',
            'net_contents': 'Net Contents',
            'government_warning': 'Government Warning'
        };

        return nameMap[field] || field;
    }

    // ===== ERROR DISPLAY =====

    /**
     * Show error message to user
     *
     * @param {string} message - Error message to display
     */
    function showError(message) {
        errorDisplay.style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
        errorDisplay.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Hide error message
     */
    function hideError() {
        errorDisplay.style.display = 'none';
    }

    // ===== BUTTON EVENT LISTENERS =====

    /**
     * "Try Again" button - resets form and shows input section
     */
    tryAgainBtn.addEventListener('click', function() {
        // Reset form inputs
        form.reset();

        // Hide preview and results
        imagePreview.style.display = 'none';
        resultsSection.style.display = 'none';

        // Scroll back to form
        form.scrollIntoView({ behavior: 'smooth' });
    });

    /**
     * Dismiss error button
     */
    dismissErrorBtn.addEventListener('click', hideError);

    // ===== HELPER FUNCTIONS =====

    /**
     * Scroll element into view smoothly
     *
     * This improves UX by guiding user's attention
     */
    HTMLElement.prototype.scrollIntoView = function(options) {
        this.scrollIntoView(options || { behavior: 'smooth', block: 'start' });
    };
});

/**
 * ===== KEY JAVASCRIPT CONCEPTS EXPLAINED =====
 *
 * 1. EVENT LISTENERS
 *    element.addEventListener('event', function)
 *    Responds to user actions (click, submit, change, etc.)
 *
 * 2. ASYNC/AWAIT
 *    async function() { ... }
 *    await promise
 *    Makes asynchronous code look synchronous
 *
 * 3. FETCH API
 *    fetch(url, options)
 *    Modern way to make HTTP requests (replaces XMLHttpRequest)
 *
 * 4. FORMDATA
 *    new FormData(form)
 *    Collects form data including files for submission
 *
 * 5. DOM MANIPULATION
 *    document.getElementById()
 *    element.innerHTML
 *    element.style.display
 *    Dynamically update HTML content
 *
 * 6. PROMISES
 *    A promise represents a value that may not be available yet
 *    fetch() returns a promise
 *    await waits for promise to resolve
 */
