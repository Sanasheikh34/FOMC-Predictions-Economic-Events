import requests
import json

# Test API endpoints
try:
    # Test all meetings
    resp = requests.get('http://localhost:5000/api/all-meetings')
    print("Status:", resp.status_code)
    data = resp.json()
    print(f"Total Meetings loaded: {len(data.get('meetings', []))}")
    
    if data.get('meetings'):
        # Test each meeting to find one with charts
        for i, meeting in enumerate(data['meetings']):
            meeting_date = meeting['date']
            resp2 = requests.get(f'http://localhost:5000/api/meeting-analysis?date={meeting_date}')
            analysis = resp2.json()
            
            if analysis.get('charts') and len(analysis['charts']) > 0:
                print(f"\nFound meeting with data at index {i}: {meeting_date}")
                print(f"Decision: {analysis.get('decision')}")
                print(f"Change (bps): {analysis.get('change_bps')}")
                print(f"Charts: {len(analysis.get('charts', []))}")
                
                first_chart = analysis['charts'][0]
                print(f"\nFirst Chart FED Level: FED{first_chart.get('fed_level')}")
                print(f"Events in first chart: {len(first_chart.get('events', []))}")
                
                if first_chart.get('events'):
                    print(f"\nAll events in first chart:")
                    for j, event in enumerate(first_chart.get('events', [])):
                        print(f"  Event {j+1}:")
                        print(f"    Date: {event.get('date')}")
                        print(f"    Type: {event.get('indicator_type')}")
                        print(f"    Color: {event.get('color')}")
                        print(f"    Actual: {event.get('actual')}")
                        print(f"    Forecast: {event.get('forecast')}")
                
                break
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
