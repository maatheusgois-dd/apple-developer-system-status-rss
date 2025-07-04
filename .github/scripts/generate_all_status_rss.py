#!/usr/bin/env python3
import re
import sys
import json
import datetime
from datetime import timezone
import requests
import os
from feedgen.feed import FeedGenerator
import zoneinfo

# Get PDT timezone
PDT = zoneinfo.ZoneInfo("America/Los_Angeles")

def fetch_and_parse_status(url, callback_name='jsonCallback'):
    """Fetch and parse system status data from Apple"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        txt = response.text
        
        # Handle both JSONP callback and plain JSON
        if callback_name in txt:
            match = re.search(rf'{callback_name}\s*\(\s*(\{{.*\}})\s*\)\s*;?', txt, re.DOTALL)
        else:
            # Try to find plain JSON object
            match = re.search(r'(\{.*\})', txt, re.DOTALL)
            
        if not match:
            print(f"💥 ERROR: couldn't find JSON data in {url}", file=sys.stderr)
            return None
            
        return json.loads(match.group(1))
    except Exception as e:
        print(f"💥 ERROR fetching {url}: {e}", file=sys.stderr)
        return None

def create_service_feed(service, service_type, base_url=None):
    """Create RSS feed for a single service"""
    # Set correct base URL based on service type
    if base_url is None:
        if service_type == 'Developer':
            base_url = 'https://developer.apple.com/system-status/'
        else:
            base_url = 'https://www.apple.com/support/systemstatus/'
    
    fg = FeedGenerator()
    service_name = service.get('serviceName', 'Unknown Service')
    
    # Use service-specific redirectUrl if available, otherwise fall back to base_url
    service_url = service.get('redirectUrl') or base_url
    
    fg.title(f'Apple {service_type} Status – {service_name}')
    fg.link(href=service_url, rel='alternate')
    fg.description(f'Latest updates for {service_name}')
    fg.language('en')
    
    events = service.get('events', [])
    
    if events:
        # Sort events by date (newest first)
        events.sort(key=lambda x: x.get('epochStartDate', 0), reverse=True)
        
        for event in events:
            e = fg.add_entry()
            e.id(f"{service_name}-{event.get('messageId', '')}-{event.get('epochStartDate', '')}")
            
            # Create status emoji based on event status
            status_emoji = "🟢" if event.get('eventStatus') == 'resolved' else "🟠" if event.get('eventStatus') == 'ongoing' else "🔴"
            status_type = event.get('statusType', 'Issue')
            event_status = event.get('eventStatus', 'unknown')
            
            e.title(f"{status_emoji} {service_name}: {status_type} ({event_status})")
            e.link(href=service_url)
            
            # Parse date
            try:
                date_str = event.get('datePosted', '')
                if date_str:
                    # Keep original timezone (PDT/PST)
                    if ' PDT' in date_str:
                        clean_date = date_str.replace(' PDT', '')
                        dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M').replace(tzinfo=PDT)
                    elif ' PST' in date_str:
                        clean_date = date_str.replace(' PST', '')
                        dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M').replace(tzinfo=PDT)
                    else:
                        # Assume PDT if no timezone specified
                        dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %H:%M').replace(tzinfo=PDT)
                else:
                    # Fall back to epoch timestamp
                    epoch_start = event.get('epochStartDate', 0)
                    dt = datetime.datetime.fromtimestamp(epoch_start / 1000.0, tz=PDT) if epoch_start else datetime.datetime.now(tz=PDT)
            except Exception:
                dt = datetime.datetime.now(tz=PDT)
            
            e.pubDate(dt)
            
            # Build description
            description_parts = []
            
            if event.get('startDate') and event.get('endDate') and event.get('eventStatus') == 'resolved':
                description_parts.append(f"Started: {event.get('startDate')}")
                description_parts.append(f"Ended: {event.get('endDate')}")
            elif event.get('startDate'):
                description_parts.append(f"Started: {event.get('startDate')}")
            
            if event.get('message'):
                description_parts.append(event.get('message'))
            
            if event.get('usersAffected'):
                description_parts.append(event.get('usersAffected'))
                
            if event.get('affectedServices'):
                affected = ', '.join(event.get('affectedServices'))
                description_parts.append(f"Affected Services: {affected}")
            
            e.description('\n\n'.join(description_parts))
    else:
        # No events - don't create RSS entries for operational services
        # This prevents spam notifications for services with no issues
        pass
    
    return fg

def create_aggregate_feed(services, title_suffix, service_type):
    """Create aggregated RSS feed for multiple services"""
    # Set correct base URL based on service type
    if service_type == 'Developer':
        base_url = 'https://developer.apple.com/system-status/'
    elif service_type == 'All':
        base_url = 'https://www.apple.com/support/systemstatus/'
    else:
        base_url = 'https://www.apple.com/support/systemstatus/'
    
    fg = FeedGenerator()
    fg.title(f'Apple {service_type} System Status – {title_suffix}')
    fg.link(href=base_url, rel='alternate')
    fg.description(f'Latest updates for all Apple {service_type} services')
    fg.language('en')
    
    all_events = []
    services_with_events = set()
    
    # Collect all events from all services
    for service in services:
        service_name = service.get('serviceName', 'Unknown Service')
        events = service.get('events', [])
        
        if events:
            services_with_events.add(service_name)
            for event in events:
                event_copy = event.copy()
                event_copy['_serviceName'] = service_name
                event_copy['_serviceUrl'] = service.get('redirectUrl') or base_url
                all_events.append(event_copy)
    
    # Don't add operational status entries to aggregate feeds
    # This prevents spam from services with no issues
    # Only real events (outages, issues) will appear in the feed
    
    # Sort all events by date (newest first)
    all_events.sort(key=lambda x: x.get('epochStartDate', 0), reverse=True)
    
    # Limit to reasonable number of recent events (max 100)
    all_events = all_events[:100]
    
    for event in all_events:
        e = fg.add_entry()
        service_name = event.get('_serviceName', 'Unknown Service')
        
        # Create status emoji based on event status
        if event.get('eventStatus') == 'resolved':
            status_emoji = "🟢"
            status_text = f"{event.get('statusType', 'Issue')} (resolved)"
        elif event.get('eventStatus') == 'ongoing':
            status_emoji = "🟠"
            status_text = f"{event.get('statusType', 'Issue')} (ongoing)"
        else:
            status_emoji = "🔴"
            status_text = f"{event.get('statusType', 'Issue')} ({event.get('eventStatus', 'unknown')})"
        
        service_specific_url = event.get('_serviceUrl', base_url)
        
        e.title(f"{status_emoji} {service_name}: {status_text}")
        e.link(href=service_specific_url)
        e.id(f"{service_name}-{event.get('messageId', '')}-{event.get('epochStartDate', '')}")
        
        # Parse date
        try:
            date_str = event.get('datePosted', '')
            if date_str:
                # Keep original timezone (PDT/PST)
                if ' PDT' in date_str:
                    clean_date = date_str.replace(' PDT', '')
                    dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M').replace(tzinfo=PDT)
                elif ' PST' in date_str:
                    clean_date = date_str.replace(' PST', '')
                    dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M').replace(tzinfo=PDT)
                else:
                    # Assume PDT if no timezone specified
                    dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %H:%M').replace(tzinfo=PDT)
            else:
                epoch_start = event.get('epochStartDate', 0)
                dt = datetime.datetime.fromtimestamp(epoch_start / 1000.0, tz=PDT) if epoch_start else now
        except Exception:
            dt = now
        
        e.pubDate(dt)
        
        # Build description
        description_parts = []
        
        if event.get('startDate') and event.get('endDate') and event.get('eventStatus') == 'resolved':
            description_parts.append(f"Started: {event.get('startDate')}")
            description_parts.append(f"Ended: {event.get('endDate')}")
        elif event.get('startDate'):
            description_parts.append(f"Started: {event.get('startDate')}")
        
        if event.get('message'):
            description_parts.append(event.get('message'))
        
        if event.get('usersAffected'):
            description_parts.append(event.get('usersAffected'))
            
        if event.get('affectedServices'):
            affected = ', '.join(event.get('affectedServices'))
            description_parts.append(f"Affected Services: {affected}")
        
        e.description('\n\n'.join(description_parts))
    
    return fg

def sanitize_filename(name):
    """Sanitize service name for use as filename"""
    # Replace problematic characters
    name = name.replace('/', '-')
    name = name.replace('\\', '-')
    name = name.replace(' ', '-')
    name = name.replace('&', 'and')
    name = name.replace('|', '-')
    name = name.replace(':', '-')
    name = name.replace('?', '')
    name = name.replace('*', '')
    name = name.replace('<', '')
    name = name.replace('>', '')
    name = name.replace('"', '')
    return name.lower()


def main():
    # URLs for both developer and general system status
    developer_url = 'https://www.apple.com/support/systemstatus/data/developer/system_status_en_US.js'
    general_url = 'https://www.apple.com/support/systemstatus/data/system_status_en_US.js'
    
    print("🔄 Fetching developer system status...")
    developer_data = fetch_and_parse_status(developer_url, 'jsonCallback')
    
    print("🔄 Fetching general system status...")
    general_data = fetch_and_parse_status(general_url)
    
    if not developer_data and not general_data:
        print("💥 ERROR: Could not fetch any system status data", file=sys.stderr)
        sys.exit(1)
    
    # Create output directories
    os.makedirs('rss/developer', exist_ok=True)
    os.makedirs('rss/general', exist_ok=True)
    
    generated_feeds = []
    
    # Process developer services
    if developer_data:
        developer_services = developer_data.get('services', [])
        print(f"📋 Found {len(developer_services)} developer services")
        
        # Generate individual feeds for each developer service (only if they have events)
        for service in developer_services:
            service_name = service.get('serviceName', 'Unknown Service')
            events = service.get('events', [])
            
            if events:  # Only generate RSS if there are actual events
                print(f"  📄 Generating RSS for {service_name} ({len(events)} events)")
                
                fg = create_service_feed(service, 'Developer')
                filename = f"rss/developer/{sanitize_filename(service_name)}.rss"
                
                with open(filename, 'wb') as f:
                    f.write(fg.rss_str(pretty=True))
                
                generated_feeds.append(filename)
            else:
                print(f"  ⏭️  Skipping {service_name} (no events)")
        
        # Generate aggregate developer feed
        print("📄 Generating aggregate developer RSS feed...")
        dev_aggregate = create_aggregate_feed(developer_services, 'All Developer Services', 'Developer')
        dev_aggregate_file = 'rss/developer/all-developer-services.rss'
        
        with open(dev_aggregate_file, 'wb') as f:
            f.write(dev_aggregate.rss_str(pretty=True))
        
        generated_feeds.append(dev_aggregate_file)
    
    # Process general services
    if general_data:
        general_services = general_data.get('services', [])
        print(f"📋 Found {len(general_services)} general services")
        
        # Generate individual feeds for each general service (only if they have events)
        for service in general_services:
            service_name = service.get('serviceName', 'Unknown Service')
            events = service.get('events', [])
            
            if events:  # Only generate RSS if there are actual events
                print(f"  📄 Generating RSS for {service_name} ({len(events)} events)")
                
                fg = create_service_feed(service, 'System')
                filename = f"rss/general/{sanitize_filename(service_name)}.rss"
                
                with open(filename, 'wb') as f:
                    f.write(fg.rss_str(pretty=True))
                
                generated_feeds.append(filename)
            else:
                print(f"  ⏭️  Skipping {service_name} (no events)")
        
        # Generate aggregate general feed
        print("📄 Generating aggregate general RSS feed...")
        gen_aggregate = create_aggregate_feed(general_services, 'All System Services', 'System')
        gen_aggregate_file = 'rss/general/all-system-services.rss'
        
        with open(gen_aggregate_file, 'wb') as f:
            f.write(gen_aggregate.rss_str(pretty=True))
        
        generated_feeds.append(gen_aggregate_file)
    
    # Generate master aggregate feed (both developer and general)
    if developer_data and general_data:
        print("📄 Generating master aggregate RSS feed...")
        all_services = developer_data.get('services', []) + general_data.get('services', [])
        master_aggregate = create_aggregate_feed(all_services, 'All Apple Services', 'All')
        master_aggregate_file = 'rss/all-apple-services.rss'
        
        with open(master_aggregate_file, 'wb') as f:
            f.write(master_aggregate.rss_str(pretty=True))
        
        generated_feeds.append(master_aggregate_file)
    
    print(f"\n✅ Generated {len(generated_feeds)} RSS feeds:")
    for feed in generated_feeds:
        print(f"  📄 {feed}")

if __name__ == '__main__':
    main() 