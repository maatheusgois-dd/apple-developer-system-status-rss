#!/usr/bin/env python3
import re
import sys
import json
import datetime
from datetime import timezone
import requests
import os
from feedgen.feed import FeedGenerator

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
                    # Parse format like "06/13/2025 01:00 PDT"
                    if ' PDT' in date_str:
                        clean_date = date_str.replace(' PDT', '')
                        dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M')
                        # PDT is UTC-7
                        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
                        dt = dt.astimezone(timezone.utc)
                    elif ' PST' in date_str:
                        clean_date = date_str.replace(' PST', '')
                        dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M')
                        # PST is UTC-8
                        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-8)))
                        dt = dt.astimezone(timezone.utc)
                    else:
                        # Assume UTC if no timezone specified
                        dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %H:%M').replace(tzinfo=timezone.utc)
                else:
                    # Fall back to epoch timestamp
                    epoch_start = event.get('epochStartDate', 0)
                    dt = datetime.datetime.fromtimestamp(epoch_start / 1000.0, tz=timezone.utc) if epoch_start else datetime.datetime.now(timezone.utc)
            except Exception:
                dt = datetime.datetime.now(timezone.utc)
            
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
        # No events - add a placeholder entry
        now = datetime.datetime.now(timezone.utc)
        e = fg.add_entry()
        e.id(f"{service_name}-no-events-{now.isoformat()}")
        e.title(f"🟢 {service_name}: All systems operational")
        e.link(href=service_url)
        e.pubDate(now)
        e.description(f"No current issues reported for {service_name}")
    
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
    
    # Add operational status for services without events
    # Use a fixed "status check" time that's more meaningful than "now"
    status_check_time = datetime.datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    
    for service in services:
        service_name = service.get('serviceName', 'Unknown Service')
        if service_name not in services_with_events:
            # Create a status entry for operational services
            operational_event = {
                '_serviceName': service_name,
                '_serviceUrl': service.get('redirectUrl') or base_url,
                'messageId': 'operational',
                'epochStartDate': int(status_check_time.timestamp() * 1000),
                'eventStatus': 'operational',
                'statusType': 'Operational',
                'datePosted': status_check_time.strftime('%m/%d/%Y %H:%M UTC'),
                'message': f'Service is operating normally',
                'usersAffected': None,
                'affectedServices': None
            }
            all_events.append(operational_event)
    
    # Sort all events by date (newest first), but prioritize non-operational events
    def sort_key(event):
        # Non-operational events get priority (lower sort value)
        priority = 0 if event.get('eventStatus') != 'operational' else 1
        epoch = event.get('epochStartDate', 0)
        return (priority, -epoch)
    
    all_events.sort(key=sort_key)
    
    # Limit to reasonable number of entries (recent events + all operational services)
    # Keep all recent events (non-operational) and up to 50 operational services
    recent_events = [e for e in all_events if e.get('eventStatus') != 'operational']
    operational_events = [e for e in all_events if e.get('eventStatus') == 'operational'][:50]
    all_events = recent_events + operational_events
    
    for event in all_events:
        e = fg.add_entry()
        service_name = event.get('_serviceName', 'Unknown Service')
        
        # Create status emoji based on event status
        if event.get('eventStatus') == 'operational':
            status_emoji = "🟢"
            status_text = "Operational"
        elif event.get('eventStatus') == 'resolved':
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
                if ' PDT' in date_str:
                    clean_date = date_str.replace(' PDT', '')
                    dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M')
                    # PDT is UTC-7
                    dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-7)))
                    dt = dt.astimezone(timezone.utc)
                elif ' PST' in date_str:
                    clean_date = date_str.replace(' PST', '')
                    dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M')
                    # PST is UTC-8
                    dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-8)))
                    dt = dt.astimezone(timezone.utc)
                elif ' UTC' in date_str:
                    clean_date = date_str.replace(' UTC', '')
                    dt = datetime.datetime.strptime(clean_date, '%m/%d/%Y %H:%M').replace(tzinfo=timezone.utc)
                else:
                    # Assume UTC if no timezone specified
                    dt = datetime.datetime.strptime(date_str, '%m/%d/%Y %H:%M').replace(tzinfo=timezone.utc)
            else:
                epoch_start = event.get('epochStartDate', 0)
                dt = datetime.datetime.fromtimestamp(epoch_start / 1000.0, tz=timezone.utc) if epoch_start else status_check_time
        except Exception:
            dt = status_check_time
        
        e.pubDate(dt)
        
        # Build description
        description_parts = []
        
        if event.get('eventStatus') == 'operational':
            description_parts.append(f"✅ {service_name} is operating normally")
            description_parts.append("No current issues reported")
        else:
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
        
        # Generate individual feeds for each developer service
        for service in developer_services:
            service_name = service.get('serviceName', 'Unknown Service')
            print(f"  📄 Generating RSS for {service_name}")
            
            fg = create_service_feed(service, 'Developer')
            filename = f"rss/developer/{sanitize_filename(service_name)}.rss"
            
            with open(filename, 'wb') as f:
                f.write(fg.rss_str(pretty=True))
            
            generated_feeds.append(filename)
        
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
        
        # Generate individual feeds for each general service
        for service in general_services:
            service_name = service.get('serviceName', 'Unknown Service')
            print(f"  📄 Generating RSS for {service_name}")
            
            fg = create_service_feed(service, 'System')
            filename = f"rss/general/{sanitize_filename(service_name)}.rss"
            
            with open(filename, 'wb') as f:
                f.write(fg.rss_str(pretty=True))
            
            generated_feeds.append(filename)
        
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