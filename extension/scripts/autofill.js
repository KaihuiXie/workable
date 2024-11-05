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
    const isCustomDropdown = element.classList.contains('background-field');

    if (isCustomDropdown) {
      //handleCustomDropdown(element, value);
      console.log("custom drop down", element, value)
    } else if (tagName === 'input' && (type === 'text' || type === 'email' || type === 'tel' || type === 'number' || type === 'search')) {
      element.value = value;
      element.dispatchEvent(new Event('input', { bubbles: true }));
    } else if (tagName === 'input' && (type === 'checkbox' || type === 'radio')) {
      element.checked = value;
      element.dispatchEvent(new Event('change', { bubbles: true }));
    } else if (tagName === 'select') {
      //console.log("selection box", element, value)
      if (element.multiple) {
        // For multi-select, handle multiple values
        const values = value.split(',').map(v => v.trim());
        Array.from(element.options).forEach(option => {
          option.selected = values.includes(option.value) || values.includes(option.text);
        });
      } else {
        // For single select, match based on the option value or text
        let matched = false;
        Array.from(element.options).forEach(option => {
          if (option.value === value || option.text === value) {
            element.value = option.value;
            matched = true;
          }
        });
        if (!matched) console.warn(`Option not found in select for value: ${value}`);
      }
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

function handleCustomDropdown(element, value) {
  const dropdownOptions = Array.from(element.options);
  const matchingOption = dropdownOptions.find(option => option.text === value || option.value === value);

  if (matchingOption) {
    element.value = matchingOption.value;
    element.dispatchEvent(new Event('change', { bubbles: true }));

    if (element.classList.contains('select2-hidden-accessible')) {
      // If using Select2 or similar, refresh the display.
      $(element).trigger('change');
    }
  } else {
    console.warn(`No matching option found for value: ${value}`);
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
