// background.js
import { sendHTMLToBackend, fetchResume } from '../scripts/api.js';
import { autofillForm } from '../scripts/autofill.js';

// You can now use these functions as needed in the background service worker
chrome.runtime.onInstalled.addListener(() => {
  console.log("Resume Autofill Extension installed.");
});
