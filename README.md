# 🍎 Apple System Status RSS Feeds

> Real-time RSS feeds for all Apple services - automatically updated every 15 minutes

This project generates comprehensive RSS feeds for Apple's system status, covering both developer services and general consumer services. Get instant notifications about Apple service outages, maintenance, and status updates directly in your RSS reader.

## 📊 **What's Included**

- **130 Individual RSS Feeds** covering all Apple services
- **48 Developer Services** (App Store Connect, Xcode Cloud, CloudKit, etc.)
- **79 General Services** (iCloud, Apple Music, FaceTime, etc.)
- **3 Aggregate Feeds** (Developer, System, and Master combined)
- **Automatic Updates** every 15 minutes via GitHub Actions
- **Beautiful Web Interface** for browsing feeds

## 🚀 **Quick Start**

### Subscribe to RSS Feeds

**Individual Services:**
- App Attest: `https://your-username.github.io/rss/developer/app-attest.rss`
- iCloud Mail: `https://your-username.github.io/rss/general/icloud-mail.rss`
- Xcode Cloud: `https://your-username.github.io/rss/developer/xcode-cloud.rss`

**Aggregate Feeds:**
- All Apple Services: `https://your-username.github.io/rss/all-apple-services.rss`
- All Developer Services: `https://your-username.github.io/rss/developer/all-developer-services.rss`
- All System Services: `https://your-username.github.io/rss/general/all-system-services.rss`

**Browse All Feeds:**
Visit `https://your-username.github.io/rss/` for a complete web interface.

## 📁 **File Structure**

```
rss/
├── index.html                         # Web interface for browsing feeds
├── all-apple-services.rss            # Master feed (all services)
├── developer/
│   ├── all-developer-services.rss    # Aggregate developer feed
│   ├── app-attest.rss                # App Attest status
│   ├── app-store-connect.rss          # App Store Connect status
│   ├── xcode-cloud.rss               # Xcode Cloud status
│   ├── cloudkit-database.rss         # CloudKit Database status
│   └── ... (44 more developer services)
└── general/
    ├── all-system-services.rss       # Aggregate system feed
    ├── icloud-mail.rss               # iCloud Mail status
    ├── apple-music.rss               # Apple Music status
    ├── facetime.rss                  # FaceTime status
    ├── imessage.rss                  # iMessage status
    └── ... (75 more system services)
```

## 🛠️ **Setup**

### Option 1: Fork This Repository (Recommended)

1. Fork this repository
2. Enable GitHub Pages in repository settings
3. The GitHub Actions workflow will automatically:
   - Generate RSS feeds every 15 minutes
   - Deploy to GitHub Pages
   - Keep feeds updated with latest status

### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/rss.git
cd rss
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install requests feedgen
```

4. Generate RSS feeds:
```bash
python .github/scripts/generate_all_status_rss.py
```

## 📡 **Available Services**

### 👨‍💻 Developer Services (48 feeds)

- **App Development**: App Store Connect, TestFlight, Xcode Cloud
- **APIs**: App Store Connect API, Apple Music API, Apple Maps API
- **Authentication**: App Attest, Sign in with Apple
- **Cloud Services**: CloudKit Console, CloudKit Database
- **Notifications**: APNS, APNS Sandbox
- **Payments**: Apple Pay Production/Sandbox
- **And 36 more...**

### 🖥️ General Services (79 feeds)

- **iCloud Services**: Mail, Drive, Calendar, Contacts, Photos
- **Communication**: FaceTime, iMessage, Phone
- **Entertainment**: Apple Music, Apple TV+, Podcasts, News
- **Apps**: App Store, Mac App Store, iTunes Store
- **System**: Siri, Spotlight, Screen Time, Find My
- **And 65 more...**

## 📋 **RSS Feed Format**

Each feed includes:
- **Status Indicators**: 🟢 Operational, 🟠 Issues, 🔴 Outage
- **Event Details**: Start/end times, affected users, service descriptions
- **Timestamps**: Proper RFC-compliant dates for RSS readers
- **Unique IDs**: Prevents duplicate notifications

### Example RSS Entry

```xml
<item>
  <title>🟢 Xcode Cloud: Outage (resolved)</title>
  <link>https://www.apple.com/support/systemstatus/</link>
  <description>
    Started: 06/12/2025 11:30 PDT
    Ended: 06/12/2025 14:30 PDT
    
    This service was disrupted, but is now stable.
    
    Some users were affected
  </description>
  <pubDate>Fri, 13 Jun 2025 01:00:00 +0000</pubDate>
</item>
```

## ⚙️ **GitHub Actions Workflow**

The repository includes automated workflows:

### RSS Generation (`generate.yml`)
- **Frequency**: Every 15 minutes
- **Action**: Fetches latest status from Apple APIs
- **Output**: Updates all 130 RSS feeds
- **Deployment**: Auto-commits and pushes changes

### GitHub Pages (`static.yml`)
- **Trigger**: On push to main branch
- **Action**: Deploys RSS feeds and web interface
- **Result**: Makes feeds publicly accessible

## 🔧 **Configuration**

### Customize Update Frequency

Edit `.github/workflows/generate.yml`:
```yaml
on:
  schedule:
    - cron: '*/30 * * * *'  # Change to 30 minutes
```

### Add Custom Services

Edit `.github/scripts/generate_all_status_rss.py` to filter or add specific services.

## 📖 **Data Sources**

RSS feeds are generated from official Apple System Status APIs:
- **Developer Services**: `https://www.apple.com/support/systemstatus/data/developer/system_status_en_US.js`
- **General Services**: `https://www.apple.com/support/systemstatus/data/system_status_en_US.js`

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 **License**

This project is open source and available under the [MIT License](LICENSE).

## 🔗 **Related Links**

- [Apple System Status](https://www.apple.com/support/systemstatus/) - Official Apple status page
- [RSS Specification](https://www.rssboard.org/rss-specification) - RSS 2.0 standard
- [GitHub Pages](https://pages.github.com/) - Free hosting for static sites

## ⚡ **Performance**

- **Feed Generation**: ~10 seconds for all 130 feeds
- **File Size**: Individual feeds ~1-5KB, aggregates ~5-10KB
- **Update Frequency**: 15 minutes (configurable)
- **Hosting**: Free via GitHub Pages

## 🆘 **Troubleshooting**

### GitHub Actions Permission Error
Add repository permissions in `.github/workflows/generate.yml`:
```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

### Python Dependencies
Install required packages:
```bash
pip install requests feedgen lxml python-dateutil
```

### RSS Feed Not Updating
1. Check GitHub Actions tab for errors
2. Verify repository permissions
3. Ensure GitHub Pages is enabled

---

**🔄 Last Updated**: Automatically updated every 15 minutes by GitHub Actions  
**📊 Total Feeds**: 130 individual RSS feeds covering all Apple services  
**🌟 Status**: All systems operational and monitoring Apple services 24/7 