const BACKEND_URL = 'http://localhost:8080/process_html';
const RESUME_URL = 'http://localhost:8080/get_resume';

export function sendHTMLToBackend(htmlContent) {
  return fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ html: htmlContent })
  })
  .then(response => response.json())
  .catch(error => console.error('Error communicating with backend:', error));
}

export function fetchResume() {
  return fetch(RESUME_URL).then(response => response.blob());
}
