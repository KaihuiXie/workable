import { fetchResume } from './api.js';

export function autofillForm(fieldData) {
  fieldData.fields.forEach(field => {
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
      console.warn(`Unhandled element type: ${tagName}`);
    }
  });

  const resumeField = document.querySelector('input[type="file"]');
  if (resumeField) {
    uploadResume(resumeField);
  }
}

function uploadResume(fileInputElement) {
  fetchResume().then(fileBlob => {
    const dataTransfer = new DataTransfer();
    const file = new File([fileBlob], "resume.pdf", { type: 'application/pdf' });
    dataTransfer.items.add(file);
    fileInputElement.files = dataTransfer.files;
    fileInputElement.dispatchEvent(new Event('change', { bubbles: true }));
  }).catch(error => console.error('Error downloading resume:', error));
}
