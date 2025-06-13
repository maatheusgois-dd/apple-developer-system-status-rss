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

    # 2) Extract the JSON object from JSONP callback
    match = re.search(r'jsonCallback\s*\(\s*(\{.*\})\s*\)\s*;?', txt, re.DOTALL)
    if not match:
        print("💥 ERROR: couldn't find the jsonCallback JSON in the downloaded JS.", file=sys.stderr)
        sys.exit(1)
    data = json.loads(match.group(1))

    # 3) Locate the App Attest service
    services = data.get('services', [])
    app_attest = next((s for s in services if 'App Attest' in s.get('serviceName','')), None)

    # 4) Build the RSS feed
    fg = FeedGenerator()
    fg.title('Apple Developer System Status – App Attest')
    fg.link(href='https://www.apple.com/support/systemstatus/', rel='alternate')
    fg.description('Latest updates for Apple App Attest')
    fg.language('en')

    if app_attest:
        for event in app_attest.get('events', []):
            e = fg.add_entry()
            e.id(str(event.get('messageId', '')) + str(event.get('epochStartDate', '')))
            status_emoji = "🟢" if event.get('eventStatus') == 'resolved' else "🟠"
            e.title(f"{status_emoji} {app_attest['serviceName']}: {event.get('statusType', 'Issue')} ({event.get('eventStatus', 'unknown')})")
            e.link(href='https://www.apple.com/support/systemstatus/')
            try:
                # Try to parse datePosted first, then fall back to epochStartDate
                date_str = event.get('datePosted', '')
                if date_str:
                    # Parse format like "06/13/2025 01:00 PDT"
                    dt = datetime.datetime.strptime(date_str.replace(' PDT', '').replace(' PST', ''), '%m/%d/%Y %H:%M')
                else:
                    # Fall back to epoch timestamp
                    epoch_start = event.get('epochStartDate', 0)
                    dt = datetime.datetime.fromtimestamp(epoch_start / 1000.0)
            except Exception:
                dt = datetime.datetime.utcnow()
            e.pubDate(dt)
            
            # Build description with event details
            description = []
            if event.get('startDate') and event.get('endDate'):
                description.append(f"Started: {event.get('startDate')}")
                description.append(f"Ended: {event.get('endDate')}")
            elif event.get('startDate'):
                description.append(f"Started: {event.get('startDate')}")
            
            if event.get('message'):
                description.append(event.get('message'))
            
            if event.get('usersAffected'):
                description.append(event.get('usersAffected'))
                
            e.description('\n\n'.join(description))
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
