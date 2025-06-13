# 🍎 Apple System Status RSS Feeds

> Real-time RSS feeds for all Apple services - automatically updated every 15 minutes

This project generates comprehensive RSS feeds for Apple's system status, covering both developer services and general consumer services. Get instant notifications about Apple service outages, maintenance, and status updates directly in your RSS reader.

**🌟 Live Demo**: [https://maatheusgois-dd.github.io/apple-developer-system-status-rss/](https://maatheusgois-dd.github.io/apple-developer-system-status-rss/)

## 📊 **What's Included**

- **130 Individual RSS Feeds** covering all Apple services
- **48 Developer Services** (App Store Connect, Xcode Cloud, CloudKit, etc.)
- **79 General Services** (iCloud, Apple Music, FaceTime, etc.)
- **3 Aggregate Feeds** (Developer, System, and Master combined)
- **Service-Specific URLs** linking directly to relevant documentation/consoles
- **Automatic Updates** every 15 minutes via GitHub Actions
- **Beautiful Web Interface** for browsing and searching feeds
- **Proper Timezone Handling** (PDT/PST → UTC conversion)

## 🚀 **Quick Start**

### 🔗 **Browse All Feeds**
Visit **[https://maatheusgois-dd.github.io/apple-developer-system-status-rss/](https://maatheusgois-dd.github.io/apple-developer-system-status-rss/)** for the complete web interface with search functionality.

### 📡 **Subscribe to RSS Feeds**

**Master Feeds (Recommended):**
- **All Apple Services**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/all-apple-services.rss`
- **All Developer Services**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/developer/all-developer-services.rss`
- **All System Services**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/general/all-system-services.rss`

**Popular Individual Services:**
- **App Attest**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/developer/app-attest.rss`
- **iCloud Mail**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/general/icloud-mail.rss`
- **Xcode Cloud**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/developer/xcode-cloud.rss`
- **App Store Connect**: `https://maatheusgois-dd.github.io/apple-developer-system-status-rss/rss/developer/app-store-connect.rss`

## ✨ **Key Features**

### 🎯 **Smart URL Routing**
Each RSS feed intelligently links to the most relevant page:
- **App Attest** → [DeviceCheck Documentation](https://developer.apple.com/documentation/devicecheck)
- **CloudKit Console** → [iCloud Developer Dashboard](https://icloud.developer.apple.com/dashboard)
- **Apple Pay** → [Apple Pay Developer Portal](https://developer.apple.com/apple-pay/)
- **Fallback** → Appropriate system status page when specific URLs unavailable

### 🕐 **Accurate Timestamps**
- **Pacific Time Conversion**: Properly converts Apple's PDT/PST to UTC
- **Real Event Times**: Actual incident timestamps from Apple's APIs
- **Operational Status**: Standardized timestamps for services without recent events

### 📊 **Comprehensive Coverage**
- **All Services Included**: Both operational and incident-affected services
- **Recent Events Priority**: Issues and outages appear first in aggregate feeds
- **Status Indicators**: 🟢 Operational, 🟠 Ongoing Issues, 🔴 Outages

## 📁 **File Structure**

```
rss/
├── index.html                         # Web interface with search
├── all-apple-services.rss            # Master feed (all 127 services)
├── developer/
│   ├── all-developer-services.rss    # All 48 developer services
│   ├── app-attest.rss                # App Attest status
│   ├── app-store-connect.rss          # App Store Connect status
│   ├── xcode-cloud.rss               # Xcode Cloud status
│   ├── cloudkit-database.rss         # CloudKit Database status
│   └── ... (44 more developer services)
└── general/
    ├── all-system-services.rss       # All 79 system services
    ├── icloud-mail.rss               # iCloud Mail status
    ├── apple-music.rss               # Apple Music status
    ├── facetime.rss                  # FaceTime status
    ├── imessage.rss                  # iMessage status
    └── ... (75 more system services)
```

## 🛠️ **Setup**

### Option 1: Fork This Repository (Recommended)

1. **Fork** this repository to your GitHub account
2. **Enable GitHub Pages** in repository settings (Source: GitHub Actions)
3. **Wait 5 minutes** for initial deployment
4. **Access your feeds** at `https://your-username.github.io/apple-developer-system-status-rss/`

The GitHub Actions workflow will automatically:
- ✅ Generate RSS feeds every 15 minutes
- ✅ Deploy to GitHub Pages
- ✅ Keep feeds updated with latest Apple status

### Option 2: Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/apple-developer-system-status-rss.git
cd apple-developer-system-status-rss
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install requests feedgen lxml python-dateutil
```

4. **Generate RSS feeds**:
```bash
python .github/scripts/generate_all_status_rss.py
```

## 📡 **Available Services**

### 👨‍💻 **Developer Services (48 feeds)**

**App Development:**
- App Store Connect (Analytics, TestFlight, Sales & Trends)
- Xcode Cloud, Xcode Automatic Configuration
- App Store APIs (Advanced Commerce, Server APIs, Receipt Verification)

**Cloud & Databases:**
- CloudKit Console, CloudKit Database
- Apple Maps API, MapKit JS Dashboard

**Authentication & Security:**
- App Attest, Developer ID Notary Service
- Certificates, Identifiers & Profiles

**Notifications & Payments:**
- APNS (Production & Sandbox)
- Apple Pay (Production, Sandbox, Developer Demo)

**Media & Content:**
- Apple Music API, Apple Music for Artists
- Apple News API, Apple Podcasts Connect, News Publisher

**And 28 more developer services...**

### 🖥️ **General Services (79 feeds)**

**iCloud Services:**
- Mail, Drive, Calendar, Contacts, Photos, Notes
- Backup, Keychain, Private Relay, Web Apps

**Communication:**
- FaceTime, iMessage, Phone, Walkie-Talkie

**Entertainment:**
- Apple Music (Classical, Radio, Subscriptions)
- Apple TV+, Apple TV Channels, Podcasts, News

**App Stores:**
- App Store, Mac App Store, visionOS App Store
- iTunes Store, Volume Purchase Program

**System Services:**
- Siri, Spotlight, Screen Time, Find My
- iOS Device Activation, macOS Software Update

**Financial Services:**
- Apple Pay, Apple Card, Apple Cash, Wallet

**And 50 more system services...**

## 📋 **RSS Feed Format**

Each feed includes:
- **🎯 Smart URLs**: Direct links to service documentation/consoles
- **🟢 Status Indicators**: Operational, Issues, Outage with emojis
- **📅 Accurate Timestamps**: Proper PDT/PST to UTC conversion
- **📝 Event Details**: Start/end times, affected users, descriptions
- **🔑 Unique IDs**: Prevents duplicate notifications in RSS readers

### Example RSS Entry

```xml
<item>
  <title>🟢 App Attest: Outage (resolved)</title>
  <link>https://developer.apple.com/documentation/devicecheck</link>
  <description>
    Started: 06/12/2025 11:30 PDT
    Ended: 06/12/2025 14:30 PDT
    
    This service was disrupted, but is now stable.
    
    Some users were affected
  </description>
  <pubDate>Fri, 13 Jun 2025 18:30:00 +0000</pubDate>
</item>
```

## ⚙️ **GitHub Actions Workflows**

### 🔄 **RSS Generation** (`generate.yml`)
- **Frequency**: Every 15 minutes (`*/15 * * * *`)
- **Action**: Fetches latest status from Apple APIs
- **Processing**: Converts timezones, generates 130 feeds
- **Output**: Auto-commits updated RSS files

### 🌐 **GitHub Pages Deployment** (`static.yml`)
- **Trigger**: On push to main branch
- **Action**: Deploys RSS feeds and web interface
- **Result**: Makes feeds publicly accessible via GitHub Pages

## 🔧 **Configuration**

### 📅 **Customize Update Frequency**

Edit `.github/workflows/generate.yml`:
```yaml
on:
  schedule:
    - cron: '*/30 * * * *'  # Change to 30 minutes
    - cron: '0 */6 * * *'   # Or every 6 hours
```

### 🎛️ **Modify Services**

Edit `.github/scripts/generate_all_status_rss.py` to:
- Filter specific services
- Customize RSS descriptions
- Adjust timezone handling
- Modify feed titles/formats

### 🔗 **Update URLs**

Replace `maatheusgois-dd.github.io` with your GitHub username in:
- `rss/index.html` (JavaScript RSS URLs)
- This README file
- Any documentation

## 📖 **Data Sources**

RSS feeds are generated from official Apple System Status APIs:
- **Developer Services**: [Apple Developer Status API](https://www.apple.com/support/systemstatus/data/developer/system_status_en_US.js)
- **General Services**: [Apple System Status API](https://www.apple.com/support/systemstatus/data/system_status_en_US.js)
- **Service URLs**: Extracted from `redirectUrl` fields in Apple's API responses

## 🚀 **Performance**

- **⚡ Feed Generation**: ~15 seconds for all 130 feeds
- **📦 File Sizes**: Individual feeds 1-5KB, aggregates 5-15KB
- **🔄 Update Frequency**: 15 minutes (configurable)
- **🌐 Hosting**: Free via GitHub Pages
- **📊 Bandwidth**: Minimal (~1MB total for all feeds)

## 💡 **Use Cases**

### 🛠️ **For Developers**
- Monitor App Store Connect outages before app releases
- Get instant notifications about Xcode Cloud issues
- Track CloudKit, APNS, and Apple Pay service status

### 🏢 **For DevOps Teams**
- Integration with monitoring dashboards
- Automated incident response workflows
- Service dependency tracking

### 📱 **For End Users**
- Monitor iCloud, FaceTime, Apple Music availability
- Get early warning about service disruptions
- Track Apple service reliability trends

## 🔧 **Integration Examples**

### 📊 **Slack Integration**
```yaml
# Recommended feeds for Slack channels:
#general-apple: all-apple-services.rss
#dev-ios: all-developer-services.rss
#ops-monitoring: all-system-services.rss
```

### 🔔 **RSS Reader Setup**
- **Feedly**: Add feed URLs for categorized monitoring
- **RSS Guard**: Set update intervals to 15-30 minutes
- **Thunderbird**: Create folders for Developer vs General feeds

## 🆘 **Troubleshooting**

### ❌ **GitHub Actions Permission Error**
Add to `.github/workflows/generate.yml`:
```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

### 🐍 **Python Dependencies**
```bash
pip install requests feedgen lxml python-dateutil
```

### 📡 **RSS Feeds Not Updating**
1. Check **Actions** tab for workflow errors
2. Verify **GitHub Pages** is enabled
3. Ensure repository has **write permissions**
4. Check if **GitHub API rate limits** exceeded

### 🌐 **Web Interface Issues**
- Clear browser cache
- Check if GitHub Pages deployment completed
- Verify `index.html` exists in `rss/` directory

## 🤝 **Contributing**

We welcome contributions! Please:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Test** your changes locally
4. **Commit** with clear messages: `git commit -m 'Add service filtering'`
5. **Push** to your branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request with detailed description

### 🎯 **Contribution Ideas**
- Additional status page integrations
- Enhanced filtering options
- Mobile-optimized web interface
- API rate limiting improvements
- Historical status tracking

## 📄 **License**

This project is open source and available under the [MIT License](LICENSE).

## 🔗 **Related Links**

- **[🍎 Apple System Status](https://www.apple.com/support/systemstatus/)** - Official consumer status page
- **[👨‍💻 Apple Developer Status](https://developer.apple.com/system-status/)** - Official developer status page
- **[📡 RSS 2.0 Specification](https://www.rssboard.org/rss-specification)** - RSS standard reference
- **[🌐 GitHub Pages](https://pages.github.com/)** - Free static site hosting

## 📈 **Project Stats**

- **📊 Total Feeds**: 130 individual RSS feeds
- **🔄 Update Frequency**: Every 15 minutes
- **⚡ Generation Time**: ~15 seconds for all feeds
- **🌍 Global Access**: Free via GitHub Pages CDN
- **📱 Mobile Friendly**: Responsive web interface
- **🔍 Searchable**: Real-time feed filtering

---

**🔄 Last Updated**: Automatically updated every 15 minutes by GitHub Actions  
**📊 Status**: ✅ All systems operational - monitoring 127 Apple services 24/7  
**🌟 Live Demo**: [https://maatheusgois-dd.github.io/apple-developer-system-status-rss/](https://maatheusgois-dd.github.io/apple-developer-system-status-rss/) 