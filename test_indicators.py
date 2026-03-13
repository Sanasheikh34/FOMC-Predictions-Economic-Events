import requests

# Test API to find meetings with all different indicator types
try:
    resp = requests.get('http://localhost:5000/api/all-meetings')
    data = resp.json()
    
    all_types = set()
    
    # Check multiple meetings to see all indicator types
    for i, meeting in enumerate(data['meetings']):
        if i > 15:  # Check first 15 meetings
            break
        
        meeting_date = meeting['date']
        resp2 = requests.get(f'http://localhost:5000/api/meeting-analysis?date={meeting_date}')
        analysis = resp2.json()
        
        if analysis.get('charts'):
            for chart in analysis['charts']:
                for event in chart.get('events', []):
                    all_types.add((event.get('indicator_type'), event.get('color')))
    
    print("\n=== All Indicator Types Found ===")
    for indicator_type, color in sorted(all_types):
        print(f"{indicator_type:20} Color: {color}")
    
    print(f"\nTotal indicator types found: {len(all_types)}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
