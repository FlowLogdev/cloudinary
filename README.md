# Cloudinary Video ID Console

A small web app for setting or changing a Cloudinary video's `videoId` (public_id)
right from your browser. Deployed on Vercel at `cloudinary.lustmia.com`.

## How it works

- `index.html` — static frontend (password-gated, dark "tally light" theme).
  Video uploads go **directly from the browser to Cloudinary** using a signed,
  time-limited upload signature — the video file never passes through our own
  server, avoiding Vercel's serverless request-size limits.
- `api/index.py` — Flask app deployed as a Vercel serverless function. Handles:
  - `POST /api/sign-upload` — generates a signed upload signature (secret never leaves the server)
  - `POST /api/rename` — renames an existing video's public_id
  - `POST /api/check-password` — validates the site password
- `vercel.json` — routes all `/api/*` requests to the Flask app.

## Environment variables (set in Vercel → Project Settings → Environment Variables)

```
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
SITE_PASSWORD       # the password required to use the upload/rename forms
```

None of these are stored in this repo — they're injected at runtime by Vercel.

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export CLOUDINARY_CLOUD_NAME=...
export CLOUDINARY_API_KEY=...
export CLOUDINARY_API_SECRET=...
export SITE_PASSWORD=...
python3 -c "from api.index import app; app.run(port=5001, debug=True)"
```

Then open http://127.0.0.1:5001.

## Deployment

Connected to Vercel. Pushing to `main` triggers a production deployment.
Custom domain: `cloudinary.lustmia.com`.
