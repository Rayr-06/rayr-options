# RAYR OPTIONS - DASHBOARD SETUP GUIDE

## 🚀 Quick Setup (5 Minutes)

### Step 1: Add Your GitHub Token

1. **Open `config.js`** in your project root
2. **Replace `'YOUR_GITHUB_TOKEN_HERE'`** with your actual GitHub Personal Access Token
3. **Save the file**

Example:
```javascript
window.GITHUB_CONFIG = {
    token: 'ghp_abcdefghijklmnopqrstuvwxyz1234567890',  // ← Your token here
    owner: 'Rayr-06',
    repo: 'rayr-options'
};
```

### Step 2: Update .gitignore

Add this line to `.gitignore`:
```
config.js
```

This prevents your token from being committed to GitHub.

### Step 3: Deploy to GitHub

```powershell
cd E:\claude\Projects\rayr-options

# Replace index.html with upgraded version
# (Use the index_upgraded.html I sent you)

# Add and commit
git add index.html .gitignore
git commit -m "Deploy upgraded dashboard with working controls"
git push
```

### Step 4: Test It!

1. Open: `https://rayr-06.github.io/rayr-options/`
2. Click **"SCAN NOW"** button
3. Should see notification: "Scan Started"
4. Check GitHub Actions tab - workflow should be running!

---

## ✅ What Works Now

### Dashboard Features:
- ✅ **Real bot controls** (START/STOP/SCAN)
- ✅ **Help tooltips** (? icons everywhere)
- ✅ **Live status updates** (RUNNING/STOPPED/ANALYZING)
- ✅ **Push notifications** (on new trades, events)
- ✅ **Beautiful UI** with loading states
- ✅ **Mobile responsive** (works perfectly on phone)

### Bot Controls:
- **START TRADING** → Triggers GitHub Actions workflow immediately
- **STOP TRADING** → Sets pause flag (bot won't trade)
- **SCAN NOW** → Runs market analysis on-demand
- **REFRESH** → Updates dashboard data

---

## 📱 Mobile Setup

1. Open dashboard on phone: `https://rayr-06.github.io/rayr-options/`
2. Tap **Share** button
3. Select **"Add to Home Screen"**
4. ✅ Now it's an app!

Push notifications will work when:
- Dashboard is added to home screen
- You allow notifications when prompted

---

## 🔧 Troubleshooting

### "Setup Required" notification keeps showing
**Solution:** Make sure `config.js` exists and has your token

### Buttons do nothing
**Solution:** 
1. Check browser console (F12) for errors
2. Verify token has `repo` and `workflow` permissions
3. Make sure token isn't expired

### Workflow doesn't trigger
**Solution:**
1. Go to GitHub repo → Actions tab
2. Check if workflows are enabled
3. Verify token permissions

### Dashboard shows old data
**Solution:** 
1. Click **REFRESH** button
2. Clear browser cache
3. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

---

## 🎯 How It Works

### Data Flow:
```
1. Dashboard loads from GitHub Pages
2. Fetches analytics.json every 30 seconds
3. Updates all metrics and signals
4. Shows live bot status
```

### Button Flow:
```
1. You click START/STOP/SCAN
2. Dashboard calls GitHub Actions API
3. Triggers workflow on GitHub servers
4. Bot executes in cloud
5. Updates analytics.json
6. Dashboard auto-refreshes and shows results
```

### No PC Required:
- ✅ Bot runs on GitHub (cloud)
- ✅ Dashboard hosted on GitHub Pages
- ✅ Everything works from phone
- ✅ Your PC can be off!

---

## 🔐 Security Notes

### Keep Your Token Safe:
- ❌ Never commit `config.js` to GitHub
- ❌ Never share token publicly
- ❌ Never paste in Discord/Slack/etc
- ✅ Keep it LOCAL only
- ✅ Regenerate if compromised

### Token Permissions (Minimum Required):
- ✅ `repo` - Control your repository
- ✅ `workflow` - Trigger GitHub Actions
- ❌ Nothing else needed!

---

## 📊 Next Steps

### Week 1-4: Monitor & Collect Data
- Check dashboard 1x daily
- Let bot run on schedule
- Watch for 20-30 trades

### Week 4: First Review
- Win rate >50%? ✅ Continue
- Win rate <50%? ⚠️ Tune parameters

### Week 8: Final Decision
- 30+ trades collected
- Edge validated (or not)
- Go/No-go on live money

---

## 🆘 Need Help?

If something isn't working:
1. Check this README first
2. Look at browser console (F12)
3. Check GitHub Actions logs
4. Ask in chat with screenshot

---

**You're all set! Open the dashboard and start monitoring!** 🚀
