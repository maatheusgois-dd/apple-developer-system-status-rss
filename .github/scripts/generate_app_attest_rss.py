#!/usr/bin/env python3
import re
import sys
import json
import datetime
import requests
from feedgen.feed import FeedGenerator

def main():
    # 1) Download the JS payload
    url = 'https://www.apple.com/support/systemstatus/data/developer/system_status_en_US.js'
    txt = requests.get(url).text

    # 2) Extract the JSON object with a regex
    match = re.search(r'var\s+systemStatus\s*=\s*(\{.*\})\s*;', txt, re.DOTALL)
    if not match:
        print("💥 ERROR: couldn't find the systemStatus JSON in the downloaded JS.", file=sys.stderr)
        sys.exit(1)
    data = json.loads(match.group(1))

    # 3) Locate the App Attest component
    components = data.get('components', [])
    app_attest = next((c for c in components if 'App Attest' in c.get('name','')), None)

    # 4) Build the RSS feed
    fg = FeedGenerator()
    fg.title('Apple Developer System Status – App Attest')
    fg.link(href='https://www.apple.com/support/systemstatus/', rel='alternate')
    fg.description('Latest updates for Apple App Attest')
    fg.language('en')

    if app_attest:
        for u in app_attest.get('updates', []):
            e = fg.add_entry()
            e.id((u.get('number','') or '') + (u.get('date','') or ''))
            e.title(f"{app_attest['name']}: {u.get('message','')}")
            e.link(href='https://www.apple.com/support/systemstatus/')
            try:
                dt = datetime.datetime.fromisoformat(u.get('date','').replace('Z','+00:00'))
            except Exception:
                dt = datetime.datetime.utcnow()
            e.pubDate(dt)
            e.description(u.get('message',''))
    else:
        now = datetime.datetime.utcnow()
        e = fg.add_entry()
        e.id(now.isoformat())
        e.title('App Attest status not found')
        e.link(href='https://www.apple.com/support/systemstatus/')
        e.pubDate(now)
        e.description('No App Attest entry found in the system status feed.')

    # 5) Write out the RSS
    with open('app-attest-status.rss', 'wb') as f:
        f.write(fg.rss_str(pretty=True))

if __name__ == '__main__':
    main()
