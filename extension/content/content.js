import { sendHTMLToBackend } from '../scripts/api.js';
import { autofillForm } from '../scripts/autofill.js';

function isRecruitingSite() {
  const recruitingPatterns = [
    /greenhouse\.io/,
    /lever\.co/,
    /myworkdayjobs\.com/,
    /workday\.com/,
    /smartrecruiters\.com/,
    /icims\.com/,
    /breezy\.hr/
  ];
  return recruitingPatterns.some(pattern => pattern.test(window.location.hostname)) ||
         document.querySelector("iframe[src*='greenhouse.io'], iframe[src*='lever.co'], iframe[src*='myworkdayjobs.com'], iframe[src*='workday.com'], iframe[src*='smartrecruiters.com']");
}

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
  document.body.appendChild(autofillButton);

  autofillButton.addEventListener('click', () => {
    const pageHTML = document.documentElement.outerHTML;
    sendHTMLToBackend(pageHTML).then(data => {
      if (data.fields) {
        autofillForm(data);
      }else {
        console.error('Error in response:', data.error || 'Unknown error');
      }
    });
  });
}
