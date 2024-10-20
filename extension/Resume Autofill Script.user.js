// ==UserScript==
// @name         Resume Autofill Script
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Auto-fill resume information on job application pages.
// @match        *://*/*
// @author       Kaihui Xie
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';

    // Configuration
    const BACKEND_URL = 'http://localhost:5000/process_html';
    const RESUME_URL = 'http://localhost:5000/get_resume';

    // Function to check if we're on a recruiting-related page
    function isRecruitingSite() {
        const recruitingPatterns = [
            /greenhouse\.io/,
            /lever\.co/,
            /myworkdayjobs\.com/,
            /workday\.com/,
            /smartrecruiters\.com/
        ];
        return recruitingPatterns.some(pattern => pattern.test(window.location.hostname)) ||
               document.querySelector("iframe[src*='greenhouse.io'], iframe[src*='lever.co'], iframe[src*='myworkdayjobs.com'], iframe[src*='workday.com'], iframe[src*='smartrecruiters.com']");
    }

    // Create a button to trigger autofill, but only add it if the page is recognized as recruiting-related
    if (isRecruitingSite()) {
        const autofillButton = document.createElement('button');
        autofillButton.innerText = 'Auto-fill Resume';
        autofillButton.style.position = 'fixed';
        autofillButton.style.top = '10px';
        autofillButton.style.right = '10px';
        autofillButton.style.zIndex = '9999';
        autofillButton.style.padding = '10px';
        autofillButton.style.backgroundColor = '#28a745';
        autofillButton.style.color = '#fff';
        autofillButton.style.border = 'none';
        autofillButton.style.borderRadius = '5px';
        autofillButton.style.cursor = 'pointer';
        autofillButton.style.boxShadow = '0px 4px 6px rgba(0, 0, 0, 0.1)';
        document.body.appendChild(autofillButton);

        autofillButton.addEventListener('click', function() {
            const pageHTML = document.documentElement.outerHTML;
            sendHTMLToBackend(pageHTML);
        });
    }

    // Function to send HTML to backend
    function sendHTMLToBackend(htmlContent) {
        GM_xmlhttpRequest({
            method: "POST",
            url: BACKEND_URL,
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify({ html: htmlContent }),
            onload: function(response) {
                //console.log(response);
                if (response.status === 200) {
                    const data = JSON.parse(response.responseText);
                    if (data.fields) {
                        autofillForm(data);
                    } else {
                        console.error('Error in response:', data.error || 'Unknown error');
                    }
                } else {
                    console.error('Error communicating with backend:', response);
                }
            }
        });
    }

    // Function to auto-fill the form
    function autofillForm(fieldData) {
        //console.log(fieldData);
        fieldData.fields.forEach(field => {
            //console.log(field);
            const selector = field.selector;
            const value = field.value;
            let element = document.querySelector(selector);
            if (!element) {
                console.warn(`Element not found for selector: ${selector}`);
                return;
            }

            const tagName = element.tagName.toLowerCase();
            const type = element.getAttribute('type') ? element.getAttribute('type').toLowerCase() : '';

            if (tagName === 'input' && (type === 'text' || type === 'email' || type === 'tel' || type === 'number' || type === 'search')) {
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
            } else if (tagName === 'input' && (type === 'checkbox' || type === 'radio')) {
                element.checked = value;
                element.dispatchEvent(new Event('change', { bubbles: true }));
            } else if (tagName === 'select') {
                element.value = value;
                element.dispatchEvent(new Event('change', { bubbles: true }));
            } else if (tagName === 'textarea') {
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
            } else {
                // Handle other types if necessary
                console.warn(`Unhandled element type: ${tagName}`);
            }
        });

        // Handle file upload field
        const resumeField = document.querySelector('input[type="file"]');
        if (resumeField) {
            uploadResume(resumeField);
        }
    }

    function uploadResume(fileInputElement) {
        GM_xmlhttpRequest({
            method: 'GET',
            url: RESUME_URL,
            responseType: 'blob',
            onload: function(response) {
                if (response.status === 200) {
                    const fileBlob = new Blob([response.response], { type: 'application/pdf' });
                    const dataTransfer = new DataTransfer();
                    const file = new File([fileBlob], "resume.pdf", { type: 'application/pdf' });
                    dataTransfer.items.add(file);
                    fileInputElement.files = dataTransfer.files;

                    // Dispatch change event to simulate user interaction
                    fileInputElement.dispatchEvent(new Event('change', { bubbles: true }));

                    // Open the resume file in a new tab for testing purposes
                    //openResumeInNewTab(fileBlob);
                } else {
                    console.error('Error downloading resume:', response);
                }
            }
        });
    }

    // test purpose
    /*function openResumeInNewTab(fileBlob) {
        const fileURL = URL.createObjectURL(fileBlob);
        window.open(fileURL, '_blank');
    }*/

    // Capture the current page's HTML
    const pageHTML = document.documentElement.outerHTML;

    // Add an event listener to the button to trigger autofill when clicked
    //autofillButton.addEventListener('click', function() {
    //    sendHTMLToBackend(pageHTML);
    //});
})();
