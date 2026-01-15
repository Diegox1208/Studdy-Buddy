// API Configuration
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : 'https://studdybuddy-production-5a70.up.railway.app';

console.log(`🔗 API URL: ${API_URL}`);
