// API Configuration
// Local development talks to the Flask backend on port 5000.
// Production talks to the Flask backend hosted on Render.
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://studdy-buddy-backend-ayww.onrender.com';

const SUPABASE_URL = 'https://znbvjnvffknswcbqrznm.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_5E6jKC9HhJbuAm5K1O79Hw_K5-QrmLz';

