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
      //console.log("custom drop down", element, value);
      if (element.tagName === 'INPUT' && element.classList.contains('school-name')) {
        handleDynamicDropdown(element, value);
      }
      if (element.tagName === 'SELECT' && element.classList.contains('background-field')) {
        handleCustomDropdown(element, value);
      }
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
/*async function handleDynamicDropdown(hiddenInputElement, displayText) {
  console.log("Handling dynamic dropdown for:", hiddenInputElement, "with value:", displayText);

  if (!hiddenInputElement) {
    console.error("Hidden input element not found.");
    return;
  }

  // Derive the select2-container ID based on the hidden input's ID
  const containerId = 's2id_' + hiddenInputElement.id;
  const container = document.getElementById(containerId);

  if (!container) {
    console.error(`Select2 container with ID "${containerId}" not found.`);
    return;
  }

  // Locate the clickable trigger element inside the select2-container
  const clickableTrigger = container.querySelector('a.select2-choice');
  if (!clickableTrigger) {
    console.error("Clickable trigger ('a.select2-choice') not found inside the select2-container.");
    return;
  }

  // Simulate a click on the dropdown trigger to activate the dropdown
  clickableTrigger.click();
  console.log("Clicked the dropdown trigger to open the dropdown.");

  // Wait for the dropdown to open and the search input to become visible
  await new Promise(resolve => setTimeout(resolve, 500)); // Adjust delay as necessary

  // Locate the search input field within the active dropdown
  const searchInput = container.querySelector('.select2-input');
  if (!searchInput) {
    console.error("Search input (.select2-input) not found after activating the dropdown.");
    return;
  }

  // Focus the search input and set its value
  searchInput.focus();
  searchInput.value = displayText;
  searchInput.dispatchEvent(new Event('input', { bubbles: true }));
  console.log(`Typed "${displayText}" into the search input.`);

  // Wait for the dropdown options to load based on the input
  await new Promise(resolve => setTimeout(resolve, 1000)); // Adjust delay as necessary

  // Locate the dynamically loaded options
  const dropdownOptions = container.querySelectorAll('.select2-results li.select2-result-selectable');
  console.log("Dropdown options loaded:", dropdownOptions);

  if (!dropdownOptions || dropdownOptions.length === 0) {
    console.warn("No dropdown options found after typing.");
    return;
  }

  // Find the option that matches the desired display text
  let matchingOption = null;
  dropdownOptions.forEach(option => {
    const optionText = option.textContent.trim().toLowerCase();
    if (optionText === displayText.trim().toLowerCase()) {
      matchingOption = option;
    }
  });

  if (!matchingOption) {
    console.warn(`No matching option found for "${displayText}".`);
    return;
  }

  // Simulate a click on the matching option to select it
  matchingOption.click();
  console.log(`Clicked on the matching option: "${displayText}".`);

  // Optionally, verify that the hidden input field is updated
  const newValue = hiddenInputElement.value;
  console.log(`Hidden input field updated to value: "${newValue}".`);

  // Dispatch a change event on the hidden input to notify listeners
  hiddenInputElement.dispatchEvent(new Event('change', { bubbles: true }));
  console.log(`Dispatched a change event on the hidden input element.`);
}*/

/*async function handleDynamicDropdown(hiddenInputElement, displayText) {
  console.log("Handling dynamic dropdown for:", hiddenInputElement, "with value:", displayText);

  if (!hiddenInputElement) {
    console.error("Hidden input element not found.");
    return;
  }

  // Derive the Select2 container ID based on the hidden input's ID
  const containerId = 's2id_' + hiddenInputElement.id;
  const container = document.getElementById(containerId);

  if (!container) {
    console.error(`Select2 container with ID "${containerId}" not found.`);
    return;
  }

  // Locate the clickable trigger element inside the Select2 container
  const clickableTrigger = container.querySelector('a.select2-choice');
  if (!clickableTrigger) {
    console.error("Clickable trigger ('a.select2-choice') not found inside the Select2 container.");
    return;
  }

  // Simulate a click on the dropdown trigger to open the dropdown
  clickableTrigger.click();
  console.log("Clicked the dropdown trigger to open the dropdown.");

  // Wait for the dropdown to open and the search input to become visible
  await waitForElement('.select2-drop-active .select2-input', 3000);
  const searchInput = container.querySelector('.select2-drop-active .select2-input');

  if (!searchInput) {
    console.error("Search input (.select2-input) not found after activating the dropdown.");
    return;
  }

  // Focus the search input and set its value
  searchInput.focus();
  searchInput.value = displayText;
  searchInput.dispatchEvent(new Event('input', { bubbles: true }));
  console.log(`Typed "${displayText}" into the search input.`);

  // Wait for the dropdown options to load based on the input
  await waitForElement('.select2-results li.select2-result-selectable', 3000);
  const dropdownOptions = container.querySelectorAll('.select2-results li.select2-result-selectable');
  console.log("Dropdown options loaded:", dropdownOptions);

  if (!dropdownOptions || dropdownOptions.length === 0) {
    console.warn("No dropdown options found after typing.");
    return;
  }

  // Find the option that matches the desired display text
  let matchingOption = null;
  dropdownOptions.forEach(option => {
    const optionText = option.textContent.trim().toLowerCase();
    if (optionText === displayText.trim().toLowerCase()) {
      matchingOption = option;
    }
  });

  if (!matchingOption) {
    console.warn(`No matching option found for "${displayText}".`);
    return;
  }

  // Simulate a click on the matching option to select it
  matchingOption.click();
  console.log(`Clicked on the matching option: "${displayText}".`);

  // Optionally, verify that the hidden input field is updated
  const newValue = hiddenInputElement.value;
  console.log(`Hidden input field updated to value: "${newValue}".`);

  // Dispatch a change event on the hidden input to notify listeners
  hiddenInputElement.dispatchEvent(new Event('change', { bubbles: true }));
  console.log(`Dispatched a change event on the hidden input element.`);
}
*/
async function fetchAllData(url) {
  const allData = [];
  let currentPage = 1;
  const perPage = 100; // Based on the meta data in your response
  let totalCount = null;

  try {
    while (totalCount === null || allData.length < totalCount) {
      const response = await fetch(`${url}?page=${currentPage}&per_page=${perPage}`);
      const data = await response.json();

      if (data.items) {
        allData.push(...data.items); // Add current page's data to the array
      }

      if (totalCount === null) {
        totalCount = data.meta.total_count; // Set total count from the first response
      }

      currentPage++; // Move to the next page
      console.log(`Fetching page ${currentPage}...`);
    }

    console.log(`Fetched ${allData.length} items in total.`);
    return allData;
  } catch (error) {
    console.error('Error fetching data:', error);
    return allData; // Return the data fetched so far, if any
  }
}

// Function to handle dynamic dropdown (Select2)
async function handleDynamicDropdown(hiddenInputElement, displayText) {
  console.log("Handling dynamic dropdown for:", hiddenInputElement, "with value:", displayText);

  // Fetch data from the API
  const url = hiddenInputElement.getAttribute('data-url');
  const allData = await fetchAllData(url);
  console.log('Fetched all data:', allData);
  /*
  // Populate the <select> element with all fetched options
  allData.forEach(item => {
    // Avoid adding duplicate options
    if (!hiddenInputElement.querySelector(`option[value="${item.id}"]`)) {
      const option = document.createElement('option');
      option.value = item.id;
      option.text = item.text;
      hiddenInputElement.appendChild(option);
    }
  });*/

  // Reinitialize Select2 to recognize new options (if necessary)
  // If Select2 is already initialized, you might not need to do this
  // Uncomment the following lines if Select2 doesn't recognize new options automatically
  /*
  $(hiddenInputElement).select2('destroy').select2({
    width: '60%',
    placeholder: "Select a School",
    allowClear: true
  });
  */

  // Find the matching option
  const matchingOption = allData.find(item => item.text.toLowerCase() === displayText.toLowerCase());
  if (!matchingOption) {
    console.warn(`No matching option found for "${displayText}"`);
    return;
  }

  // Set the value of the <select> element
  //hiddenInputElement.value = matchingOption.id;

  // Trigger Select2 to update the UI
  $(hiddenInputElement).val(matchingOption.id).trigger('change');

  console.log(`Set value "${matchingOption.id}" for the dropdown.`);
  console.log(`Selected School: "${matchingOption.text}"`);
}

// Helper function to wait for an element to appear in the DOM
function waitForElement(selector, timeout = 3000) {
  return new Promise((resolve, reject) => {
    const intervalTime = 100;
    let elapsedTime = 0;

    const interval = setInterval(() => {
      const element = document.querySelector(selector);
      if (element) {
        clearInterval(interval);
        resolve(element);
      } else {
        elapsedTime += intervalTime;
        if (elapsedTime >= timeout) {
          clearInterval(interval);
          reject(new Error(`Timeout waiting for element: ${selector}`));
        }
      }
    }, intervalTime);
  });
}

function handleCustomDropdown(element, displayText) {
  // Check if the dropdown element exists
  if (!element) {
    console.error("Dropdown element is not provided.");
    return;
  }

  // Get all options in the dropdown
  const options = Array.from(element.options);

  // Find the option with matching display text
  const matchingOption = options.find(option => option.text.trim() === displayText.trim());

  if (matchingOption) {
    // Set the dropdown value to the corresponding option's value
    element.value = matchingOption.value;

    // Trigger a change event to notify listeners
    element.dispatchEvent(new Event("change", { bubbles: true }));

    console.log(`Selected "${displayText}" in the dropdown.`);
  } else {
    // Log a warning if no matching text is found
    console.warn(`No option found with display text "${displayText}".`);
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
