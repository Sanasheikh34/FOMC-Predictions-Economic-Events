import requests

try:
    # Test with a recent meeting that has events
    meeting_date = '2021-03-17'
    resp = requests.get(f'http://localhost:5000/api/meeting-analysis?date={meeting_date}')
    
    if resp.status_code == 200:
        data = resp.json()
        print("OK: API Working")
        print(f"Meeting: {data['meeting_date']}")
        print(f"Decision: {data['decision']} ({data['change_bps']}bp)")
        print(f"Charts with events: {len([c for c in data['charts'] if c['events']])}")
        
        # Show first event details
        for chart in data['charts']:
            if chart['events']:
                event = chart['events'][0]
                print(f"\nSample Event:")
                print(f"  Date: {event['date']}")
                print(f"  Indicator: {event.get('indicator_type', 'Unknown')}")
                print(f"  Color: {event.get('color', 'Unknown')}")
                print(f"  Has all fields: date={bool(event.get('date'))}, type={bool(event.get('indicator_type'))}, color={bool(event.get('color'))}")
                break
    else:
        print(f"ERROR: API Error: {resp.status_code}")
        
except Exception as e:
    print(f"ERROR: {e}")
