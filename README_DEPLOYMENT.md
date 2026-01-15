# Study Buddy - Deployment Guide

## 📁 Estructura del Proyecto

```
Study_buddy/
├── frontend/              ← Deploy a Vercel
│   ├── index.html        (Landing page)
│   ├── student_interface.html
│   ├── professor_dashboard.html
│   ├── buddy_bot.html
│   ├── assets/
│   │   └── config.js     (API configuration)
│   └── vercel.json       (Vercel config)
│
├── backend/               ← Deploy a Railway/Render
│   ├── app.py            (Flask API)
│   ├── requirements.txt  (Python dependencies)
│   ├── Procfile          (For deployment)
│   ├── .env.example      (Environment variables template)
│   └── uploads/          (File storage)
│
└── README_DEPLOYMENT.md  (This file)
```

---

## 🚀 Deployment Instructions

### Part 1: Deploy Backend to Railway

#### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"

#### Step 2: Deploy Backend
```bash
# Navigate to backend folder
cd backend

# Initialize git (if not already)
git init
git add .
git commit -m "Initial backend commit"

# Push to Railway
railway login
railway init
railway up
```

#### Step 3: Get Backend URL
After deployment, Railway will give you a URL like:
```
https://study-buddy-api.railway.app
```

#### Step 4: Set Environment Variables on Railway
In Railway dashboard:
- Go to Variables
- Add:
  ```
  PORT=5000
  FLASK_ENV=production
  CORS_ORIGINS=https://study-buddy.vercel.app
  ```

---

### Part 2: Deploy Frontend to Vercel

#### Step 1: Update API URL
In `frontend/assets/config.js`, replace:
```javascript
: 'https://study-buddy-api.railway.app'; // ← Your Railway URL here
```

#### Step 2: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 3: Deploy Frontend
```bash
# Navigate to frontend folder
cd frontend

# Deploy to Vercel
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? study-buddy
# - Directory? ./
# - Override settings? No

# Deploy to production
vercel --prod
```

#### Step 4: Get Frontend URL
Vercel will give you a URL like:
```
https://study-buddy.vercel.app
```

#### Step 5: Update CORS on Backend
Go back to Railway → Variables → Update:
```
CORS_ORIGINS=https://study-buddy.vercel.app
```

---

## ✅ Verification

### Test Backend
```bash
# Health check
curl https://study-buddy-api.railway.app/health
```

### Test Frontend
Open in browser:
```
https://study-buddy.vercel.app
```

Test file upload:
1. Choose role (Student/Professor)
2. Go to Casillero
3. Drag & drop a file
4. Should upload successfully

---

## 🔧 Local Development

### Start Backend Locally
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Backend runs at: http://localhost:5000

### Start Frontend Locally
Simply open `frontend/index.html` in browser, or:
```bash
cd frontend
python -m http.server 3000
```
Frontend runs at: http://localhost:3000

---

## 📊 Database Setup (Future)

When ready to add PostgreSQL:

### On Railway:
1. Click "+ New" → Add PostgreSQL
2. Copy connection string
3. Add to backend environment:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

### Update backend/app.py:
```python
import psycopg2
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
```

---

## 🐛 Troubleshooting

### Issue: CORS Error
**Solution:** Make sure backend CORS_ORIGINS includes your Vercel URL

### Issue: 404 on file upload
**Solution:** Check API_URL in config.js points to correct backend

### Issue: Backend timeout
**Solution:** Railway free tier sleeps after inactivity. First request takes longer.

### Issue: File uploads fail
**Solution:** Check Railway logs:
```bash
railway logs
```

---

## 💰 Cost Breakdown

- **Vercel Frontend:** $0 (Free tier)
- **Railway Backend:** $0 (500 hrs/month free)
- **Total:** $0 for testing

### Free Tier Limits:
- Vercel: 100 GB bandwidth/month
- Railway: 500 hours execution/month
- Perfect for development & small-scale testing

---

## 🔐 Security Notes

For production:
1. Add authentication (JWT tokens)
2. Use environment secrets for API keys
3. Add rate limiting
4. Implement HTTPS only
5. Add input validation
6. Sanitize file uploads

---

## 📱 Custom Domain (Optional)

### Vercel:
1. Go to Settings → Domains
2. Add your domain: `studybuddy.com`
3. Follow DNS instructions

### Railway:
1. Settings → Domains
2. Add custom domain
3. Update DNS CNAME

---

## 🔄 Continuous Deployment

Both platforms support auto-deployment:

### Vercel:
- Connect to GitHub repo
- Auto-deploys on push to main branch

### Railway:
- Connect to GitHub repo
- Auto-deploys on push

---

## 📞 Support

Issues? Check:
- Railway logs: `railway logs`
- Vercel logs: Dashboard → Deployments → View logs
- Browser console (F12) for frontend errors

---

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Vercel
3. ⏳ Add PostgreSQL database
4. ⏳ Implement authentication
5. ⏳ Add professor dashboard functionality
6. ⏳ Integrate Buddy Bot AI

Good luck! 🚀
