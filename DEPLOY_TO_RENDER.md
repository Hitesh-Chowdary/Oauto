# How to Deploy to Render in 2 Minutes 🚀

The files inside `c:\Users\hites\PROJECTS\FINDdocsandpatches\render_deploy\` are completely prepared and tested for Render!

---

## ⚡ Method 1: Deploy as a "Static Site" (BEST for Mobile - Never Sleeps!)

Render's Static Sites are 100% free, have **zero cold starts**, and **never go to sleep**. Because the extraction engine is built directly into the client-side JavaScript, it runs instantly (0ms) on your phone.

### Step 1: Push this folder to GitHub
In PowerShell, run:
```powershell
cd c:\Users\hites\PROJECTS\FINDdocsandpatches\render_deploy
git init
git add .
git commit -m "Initial commit for Oracle Extractor"
git branch -M main
# Link to your new GitHub repository (create an empty repo on github.com first):
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to **[dashboard.render.com](https://dashboard.render.com/)**.
2. Click **New +** (top right) ➔ Select **Static Site**.
3. Connect your GitHub repository.
4. Configure settings:
   * **Name**: `oracle-extractor` (or whatever you prefer)
   * **Branch**: `main`
   * **Build Command**: *(leave empty)*
   * **Publish Directory**: `.`
5. Click **Create Static Site**.

🎉 Done! In 15 seconds, Render will give you a live URL like:
`https://oracle-extractor.onrender.com`

---

## 🐍 Method 2: Deploy as a Python "Web Service"

If you prefer running the Python Flask backend with the `/api/extract` REST API:

1. Push the `render_deploy` folder to GitHub (same as Step 1 above).
2. On **[dashboard.render.com](https://dashboard.render.com/)**, click **New +** ➔ **Web Service**.
3. Select your repo.
4. Render will auto-detect `render.yaml` or you can enter:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
   * **Instance Type**: `Free`
5. Click **Deploy Web Service**.

---

## 📱 Adding to your Mobile Phone Home Screen
Once your Render link is live:
1. Open the URL on your mobile phone in **Safari** (iOS) or **Chrome** (Android).
2. Tap the browser menu:
   * **iOS (Safari)**: Tap Share ➔ **"Add to Home Screen"**.
   * **Android (Chrome)**: Tap `...` ➔ **"Install App"** or **"Add to Home screen"**.
3. You now have an app icon on your phone that launches full-screen instantly anytime you need to extract!
