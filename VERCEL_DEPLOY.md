# Vercel Python Visualizer

## Setup for Vercel Deployment

### Option 1: Deploy from GitHub (Recommended)

1. Go to [Vercel.com](https://vercel.com)
2. Import your GitHub repo: `Susandhungana1/Python-code-visualiser`
3. Add environment variable:
   - Name: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key
4. Deploy!

### Option 2: Manual Upload (Not Recommended)

The GitHub option is better because:
- Automatic builds
- Environment variables stay secure
- Easy updates

---

## Environment Variables

Add these in Vercel dashboard:

| Name | Value |
|------|-------|
| `OPENROUTER_API_KEY` | Your API key from https://openrouter.ai/ |

---

## Project Structure for Vercel

```
├── backend/
│   ├── main.py          # API endpoint (Vercel function)
│   └── requirements.txt
├── frontend/
│   └── index.html
├── vercel.json
├── requirements.txt
└── README.md
```

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend - open directly
open frontend/index.html
# Or serve it
cd frontend && python -m http.server 8080
```