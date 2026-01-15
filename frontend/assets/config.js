// API Configuration
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : 'https://study-buddy-api.railway.app'; // Change this to your deployed backend URL

console.log(`🔗 API URL: ${API_URL}`);
