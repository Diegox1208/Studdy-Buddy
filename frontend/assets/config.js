// API Configuration
// Local development talks to the Flask backend on port 5000.
// Production needs a hosted Flask API URL assigned to window.STUDY_BUDDY_API_URL.
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : (window.STUDY_BUDDY_API_URL || '');

const SUPABASE_URL = 'https://znbvjnvffknswcbqrznm.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_5E6jKC9HhJbuAm5K1O79Hw_K5-QrmLz';

if (!API_URL) {
    console.warn('Study Buddy backend API is not configured for this environment.');
}
