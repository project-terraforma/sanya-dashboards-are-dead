# Backend (Modal)

Serverless proxy for the GitHub Pages frontend. The OpenAI key lives as
a Modal secret and never reaches the browser.

## One-time setup

1. Install Modal and authenticate:
   ```bash
   pip install modal
   modal token new
   ```
2. Create the OpenAI secret (Modal stores it server-side):
   ```bash
   modal secret create overture-openai OPENAI_API_KEY=sk-...
   ```
3. Deploy the app:
   ```bash
   modal deploy backend/modal_app.py
   ```
   Modal prints a URL like `https://<user>--overture-chat-chat.modal.run`.
   Copy it.

## Wiring up GitHub Pages

1. In the GitHub repo: **Settings → Secrets and variables → Actions →
   New repository secret**.
2. Add `VITE_API_URL` with the URL from the Modal deploy above.
3. In **Settings → Pages**, set **Source** to **GitHub Actions**.
4. Push to `main`. The `Deploy frontend to GitHub Pages` workflow builds
   the Vite app with the Modal URL baked in and publishes to Pages.

## Local development

```bash
modal serve backend/modal_app.py
```
This gives you a temporary URL. Run the frontend with `VITE_API_URL`
pointing at it:
```bash
cd frontend
VITE_API_URL=https://...modal.run npm run dev
```

## Cost

`gpt-4o-mini` at temperature 0, ~600 max tokens, with the
~6KB context+artifact prompt is under $0.001 per request. Modal's free
tier ($30/month credits) covers a demo many times over; the function
scales to zero when idle.
