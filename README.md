# RAYR OPTIONS - Automated Options Trading

**Fully automated weekly options premium selling system running in the cloud.**

## 🎯 Strategy

- Sells weekly cash-secured puts on SPY, QQQ, IWM
- Target: 0.30 delta (30% OTM)
- Expected return: 24-36% annual
- Runs automatically Monday-Friday at market open

## 📊 Live Dashboard

**View on mobile:** https://rayr-06.github.io/rayr-options

- Real-time performance metrics
- Recent trade history
- Portfolio value tracking
- Auto-refreshes every 60 seconds

## 🚀 How It Works

1. GitHub Actions runs bot every weekday at 9:30 AM EST
2. Bot scans SPY, QQQ, IWM for best opportunities
3. Calculates optimal strike prices (0.30 delta)
4. Executes trade via Alpaca API
5. Updates dashboard with results
6. Commits trade data to repo

## 📈 Performance Tracking

All trades are logged in `data/results/history.json`

Analytics calculated automatically:
- Total return %
- Number of trades
- Days running
- Portfolio value

## ⚙️ Setup (One-Time)

### 1. Fork This Repo

Click "Fork" button on GitHub

### 2. Add Alpaca API Keys

Go to Settings → Secrets and variables → Actions

Add two secrets:
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`

Get keys from: https://alpaca.markets

### 3. Enable GitHub Actions

Go to Actions tab → Click "I understand, enable"

### 4. Enable GitHub Pages

Settings → Pages → Source: main branch → folder: /dashboard

## 🔄 Manual Run

You can manually trigger a trade:

1. Go to Actions tab
2. Click "Automated Options Trading"
3. Click "Run workflow"
4. Click green "Run workflow" button

## 📱 Mobile Access

Once GitHub Pages is enabled:
- Dashboard URL: https://YOUR-USERNAME.github.io/rayr-options
- Bookmark on phone home screen
- Check anytime, anywhere

## 💰 Expected Returns

**Conservative (based on 0.3% weekly):**
- Weekly: 0.3%
- Monthly: 1.2%
- Annual: 15.6%

**Realistic (based on 0.5% weekly):**
- Weekly: 0.5%
- Monthly: 2.0%
- Annual: 26.0%

**Aggressive (based on 0.7% weekly):**
- Weekly: 0.7%
- Monthly: 2.8%
- Annual: 36.4%

## ⚠️ Disclaimer

- Start with paper trading (Alpaca paper account)
- Options involve risk
- Past performance doesn't guarantee future results
- Only invest what you can afford to lose

## 📞 Support

Questions? Open an issue on GitHub.

---

**Made with 🚀 by RAYR**
