from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

# Cache for meetings and rate changes
_MEETINGS_CACHE = None
_RATE_CHANGES = {}
_MEETING_DECISIONS = {}  # Stores action type (Hold, Hike, Cut) for each meeting

# Base directory = same folder as app.py (works on Render and locally)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data():
    """Load and process all data from files"""
    try:
        # Load federal funds data (CSV)
        fed_funds = pd.read_csv(os.path.join(BASE_DIR, "fredgraph.csv"))
        fed_funds['observation_date'] = pd.to_datetime(fed_funds['observation_date'])
        fed_funds = fed_funds.sort_values('observation_date')
        
        # Load meeting premiums data (CSV or Excel)
        premium_file = None
        for f in os.listdir(BASE_DIR):
            if 'PREMIUM' in f.upper() and '2021' in f:
                premium_file = os.path.join(BASE_DIR, f)
                break
        
        if not premium_file:
            raise FileNotFoundError("Meeting premiums file not found")
        
        if premium_file.endswith('.xlsx') or premium_file.endswith('.xls'):
            premiums = pd.read_excel(premium_file)
        else:
            premiums = pd.read_csv(premium_file)

        premiums['Timestamp'] = pd.to_datetime(premiums['Timestamp'])
        premiums = premiums.sort_values('Timestamp')
        
        return fed_funds, premiums
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def load_economic_indicators():
    """Load all 10 economic indicators data with color coding"""
    try:
        # Define all 10 indicator types with their colors
        indicator_config = {
            'NFP.csv': {'name': 'NFP', 'color': '#4ade80', 'actual_col': 'Actual (K)', 'forecast_col': 'Forecast (K)', 'previous_col': 'Previous (K)'},
            'ADP.csv': {'name': 'ADP', 'color': '#facc15', 'actual_col': 'Actual (K)', 'forecast_col': 'Forecast (K)', 'previous_col': 'Previous (K)'},
            'CPI.csv': {'name': 'CPI', 'color': '#ef4444', 'actual_col': 'Actual (YoY %)', 'forecast_col': 'Forecast (YoY %)', 'previous_col': 'Previous (YoY %)'},
            'CORE PCE.csv': {'name': 'Core PCE', 'color': '#3b82f6', 'actual_col': 'Actual (YoY %)', 'forecast_col': 'Forecast (YoY %)', 'previous_col': 'Previous (YoY %)'},
            'RETAIL SALES.csv': {'name': 'Retail Sales', 'color': '#f97316', 'actual_col': 'Actual (MoM %)', 'forecast_col': 'Forecast (MoM %)', 'previous_col': 'Previous (MoM %)'},
            'GDP.csv': {'name': 'GDP', 'color': '#06b6d4', 'actual_col': 'Actual (QoQ %)', 'forecast_col': 'Forecast (QoQ %)', 'previous_col': 'Previous (QoQ %)'},
            'ECI.csv': {'name': 'ECI', 'color': '#ec4899', 'actual_col': 'Actual (QoQ %)', 'forecast_col': 'Forecast (QoQ %)', 'previous_col': 'Previous (QoQ %)'},
            'PPI.csv': {'name': 'PPI', 'color': '#a855f7', 'actual_col': 'Actual (MoM %)', 'forecast_col': 'Forecast (MoM %)', 'previous_col': 'Previous (MoM %)'},
            'JOLTS.csv': {'name': 'JOLTS', 'color': '#84cc16', 'actual_col': 'Actual (M)', 'forecast_col': 'Forecast (M)', 'previous_col': 'Previous (M)'},
            'JOBLESS CLAIMS.csv': {'name': 'Jobless Claims', 'color': '#6366f1', 'actual_col': 'Actual (K)', 'forecast_col': 'Forecast (K)', 'previous_col': 'Previous (K)'}
        }
        
        all_indicators = []
        
        for filename, config in indicator_config.items():
            try:
                filepath = os.path.join(BASE_DIR, filename)
                if not os.path.exists(filepath):
                    print(f"File not found: {filepath}")
                    continue
                
                df = pd.read_csv(filepath)
                
                # Parse Release Date
                df['Release_Date'] = pd.to_datetime(df['Release Date'], format='%d-%b-%Y')
                
                # Add indicator type and color
                df['Indicator_Type'] = config['name']
                df['Color'] = config['color']
                
                # Standardize column names for actual, forecast, previous
                df['Actual'] = pd.to_numeric(df[config['actual_col']], errors='coerce')
                df['Forecast'] = pd.to_numeric(df[config['forecast_col']], errors='coerce')
                df['Previous'] = pd.to_numeric(df[config['previous_col']], errors='coerce')
                
                all_indicators.append(df[['Release_Date', 'Reference Period', 'Actual', 'Forecast', 'Previous', 'Indicator_Type', 'Color']])
                print(f"Loaded {config['name']}: {len(df)} records")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue
        
        if not all_indicators:
            print("No economic indicators loaded")
            return None
        
        # Combine all indicators
        combined = pd.concat(all_indicators, ignore_index=True)
        combined = combined.sort_values('Release_Date')
        
        print(f"Total economic indicators loaded: {len(combined)}")
        return combined
    except Exception as e:
        print(f"Error loading economic indicators: {e}")
        return None

def extract_meetings_from_excel():
    """Extract meeting dates and rate changes from FOMC decisions CSV"""
    global _MEETINGS_CACHE, _RATE_CHANGES, _MEETING_DECISIONS
    
    if _MEETINGS_CACHE is not None:
        return _MEETINGS_CACHE
    
    try:
        # Load FOMC decisions CSV from same directory as app.py
        fomc_csv = None
        for f in os.listdir(BASE_DIR):
            if 'fomc' in f.lower() and 'decision' in f.lower() and f.endswith('.csv'):
                fomc_csv = os.path.join(BASE_DIR, f)
                print(f"Loaded FOMC CSV: {fomc_csv}")
                break
        
        meeting_dates = []
        
        if fomc_csv:
            fomc_df = pd.read_csv(fomc_csv)
            for idx, row in fomc_df.iterrows():
                meeting_name = str(row['Meeting_Date']).strip().lower()
                if 'start' in meeting_name:
                    continue
                
                try:
                    date_str = str(row['Decision_Date']).strip()
                    if date_str and date_str != 'nan' and len(date_str) >= 10:
                        meeting_date = pd.to_datetime(date_str)
                        
                        if meeting_date.year >= 2021 and meeting_date.year <= 2025:
                            meeting_dates.append(meeting_date)
                            
                            try:
                                change_str = str(row['Change_bps']).strip()
                                if change_str and change_str != 'nan':
                                    rate_change = float(change_str.replace('+', ''))
                                    _RATE_CHANGES[meeting_date.strftime('%Y-%m-%d')] = rate_change
                            except Exception as e:
                                print(f"Error parsing rate change: {e}")
                                pass
                            
                            try:
                                action = str(row['Action']).strip()
                                if action and action != 'nan' and action != 'Initial Rate':
                                    if 'hold' in action.lower():
                                        decision = 'Hold'
                                    elif 'hike' in action.lower():
                                        decision = 'Hike'
                                    elif 'cut' in action.lower():
                                        decision = 'Cut'
                                    else:
                                        decision = action
                                    
                                    change_str = str(row['Change_bps']).strip()
                                    if change_str and change_str != 'nan' and change_str != '0':
                                        bps = float(change_str.replace('+', ''))
                                        _MEETING_DECISIONS[meeting_date.strftime('%Y-%m-%d')] = {
                                            'action': decision,
                                            'bps': bps
                                        }
                                    else:
                                        _MEETING_DECISIONS[meeting_date.strftime('%Y-%m-%d')] = {
                                            'action': 'Hold',
                                            'bps': 0
                                        }
                            except Exception as e:
                                print(f"Error parsing action: {e}")
                                pass
                except Exception as e:
                    print(f"Error parsing date: {e}")
                    pass
        
        if not meeting_dates:
            print("No meetings found in CSV, using hardcoded dates")
            MEETINGS = {
                2021: ['2021-01-27', '2021-03-17', '2021-04-28', '2021-06-16',
                       '2021-07-28', '2021-09-22', '2021-11-03', '2021-12-15'],
                2022: ['2022-01-26', '2022-03-16', '2022-05-04', '2022-06-15',
                       '2022-07-27', '2022-09-21', '2022-11-02', '2022-12-14'],
                2023: ['2023-02-01', '2023-03-22', '2023-05-03', '2023-06-14',
                       '2023-07-26', '2023-09-20', '2023-11-01', '2023-12-13'],
                2024: ['2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12',
                       '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18'],
                2025: ['2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
                       '2025-07-30', '2025-09-17', '2025-10-29', '2025-12-10']
            }
            
            for year in MEETINGS:
                for date_str in MEETINGS[year]:
                    meeting_dates.append(pd.to_datetime(date_str))
        
        meeting_dates = sorted(list(set(meeting_dates)))
        _MEETINGS_CACHE = meeting_dates
        
        print(f"Loaded {len(meeting_dates)} meetings")
        print(f"Loaded {len(_RATE_CHANGES)} rate changes")
        return meeting_dates
    
    except Exception as e:
        print(f"Error extracting meetings: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_meeting_analysis(meeting_date_str):
    """Get analysis data for a specific meeting"""
    try:
        fed_funds, premiums = load_data()
        meeting_date = pd.to_datetime(meeting_date_str)
        
        if fed_funds is None or premiums is None:
            return None
        
        all_meetings = extract_meetings_from_excel()
        
        if not all_meetings:
            return None
        
        meeting_idx = None
        for i, m in enumerate(all_meetings):
            if m.date() == meeting_date.date():
                meeting_idx = i
                break
        
        if meeting_idx is None:
            return None
        
        meeting_date_key = meeting_date.strftime('%Y-%m-%d')
        rate_change_bp = _RATE_CHANGES.get(meeting_date_key, 0)
        
        fed_data_before = fed_funds[fed_funds['observation_date'] < meeting_date].sort_values('observation_date')
        if len(fed_data_before) > 0:
            prev_upper = float(fed_data_before.iloc[-1]['DFEDTARU'])
            prev_lower = float(fed_data_before.iloc[-1]['DFEDTARL'])
        else:
            prev_upper = 0
            prev_lower = 0
        
        next_day = meeting_date + timedelta(days=1)
        fed_data_after = fed_funds[fed_funds['observation_date'] >= next_day].sort_values('observation_date')
        if len(fed_data_after) > 0:
            post_upper = float(fed_data_after.iloc[0]['DFEDTARU'])
            post_lower = float(fed_data_after.iloc[0]['DFEDTARL'])
        else:
            post_upper = 0
            post_lower = 0
        
        charts_data = []
        
        for fed_level in range(1, 7):
            fed_col = f'FED{fed_level}'
            
            if fed_col not in premiums.columns:
                continue
            
            start_meeting_idx = meeting_idx - fed_level
            end_meeting_idx = meeting_idx - (fed_level - 1)
            
            if start_meeting_idx < 0:
                continue
            
            start_date = all_meetings[start_meeting_idx]
            end_date = all_meetings[end_meeting_idx]
            
            mask = (premiums['Timestamp'] >= start_date) & (premiums['Timestamp'] <= end_date)
            date_range_data = premiums[mask].copy()
            
            if len(date_range_data) == 0:
                continue
            
            chart_points = []
            
            for idx, row in date_range_data.iterrows():
                forecast_rate = row[fed_col]
                
                if pd.isna(forecast_rate):
                    continue
                
                predicted_change_bp = float(forecast_rate)
                accuracy = max(0, 100 - abs(predicted_change_bp - rate_change_bp))
                
                chart_points.append({
                    'date': row['Timestamp'].strftime('%Y-%m-%d'),
                    'predicted': round(predicted_change_bp, 2),
                    'actual': float(rate_change_bp),
                    'accuracy': round(float(accuracy), 2),
                    'upper': post_upper,
                    'lower': post_lower,
                    'prev_upper': prev_upper,
                    'prev_lower': prev_lower
                })
            
            if chart_points:
                indicators = load_economic_indicators()
                chart_events = []
                
                if indicators is not None:
                    mask = (indicators['Release_Date'] >= start_date) & (indicators['Release_Date'] <= end_date)
                    range_indicators = indicators[mask]
                    
                    for idx, row in range_indicators.iterrows():
                        chart_events.append({
                            'date': row['Release_Date'].strftime('%Y-%m-%d'),
                            'actual': float(row['Actual']) if pd.notna(row['Actual']) else 0,
                            'forecast': float(row['Forecast']) if pd.notna(row['Forecast']) else 0,
                            'previous': float(row['Previous']) if pd.notna(row['Previous']) else 0,
                            'reference_period': str(row['Reference Period']) if pd.notna(row['Reference Period']) else '',
                            'indicator_type': str(row['Indicator_Type']) if pd.notna(row['Indicator_Type']) else 'Unknown',
                            'color': str(row['Color']) if pd.notna(row['Color']) else '#ffffff'
                        })
                
                charts_data.append({
                    'fed_level': fed_level,
                    'fed_column': fed_col,
                    'date_range': {
                        'from': start_date.strftime('%Y-%m-%d'),
                        'to': end_date.strftime('%Y-%m-%d')
                    },
                    'data': chart_points,
                    'events': chart_events
                })
        
        decision_info = _MEETING_DECISIONS.get(meeting_date_key, {'action': 'N/A', 'bps': 0})
        
        return {
            'meeting_date': meeting_date_str,
            'decision': decision_info['action'],
            'change_bps': decision_info['bps'],
            'charts': charts_data
        }
    
    except Exception as e:
        print(f"Error in get_meeting_analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_daily_accuracy(start_date, end_date):
    """Calculate daily accuracy between market premiums and actual federal funds"""
    try:
        fed_funds, premiums = load_data()
        
        if fed_funds is None or premiums is None:
            return []
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        mask = (fed_funds['observation_date'] >= start) & (fed_funds['observation_date'] <= end)
        filtered_fed = fed_funds[mask].copy()
        
        mask_prem = (premiums['Timestamp'] >= start) & (premiums['Timestamp'] <= end)
        filtered_prem = premiums[mask_prem].copy()
        
        filtered_fed['MidPoint'] = (filtered_fed['DFEDTARU'] + filtered_fed['DFEDTARL']) / 2
        
        result_data = []
        for idx, row in filtered_fed.iterrows():
            date = row['observation_date'].strftime('%Y-%m-%d')
            actual_rate = row['MidPoint']
            upper = row['DFEDTARU']
            lower = row['DFEDTARL']
            
            prem_before = filtered_prem[filtered_prem['Timestamp'] <= row['observation_date']]
            if len(prem_before) > 0:
                latest_prem = prem_before.iloc[-1]
                market_expectation = latest_prem['FED1'] if not pd.isna(latest_prem['FED1']) else 0
                
                if actual_rate != 0:
                    accuracy = max(0, 100 - abs(market_expectation - actual_rate))
                else:
                    accuracy = 100 if market_expectation == 0 else 0
            else:
                accuracy = 50
                market_expectation = 0
            
            result_data.append({
                'DATE': date,
                'Forecast': float(market_expectation),
                'Actual': float(actual_rate),
                'Upper': float(upper),
                'Lower': float(lower),
                'Accuracy': round(accuracy, 2)
            })
        
        return result_data
    except Exception as e:
        print(f"Error calculating accuracy: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/all-meetings', methods=['GET'])
def get_all_meetings():
    """Get all available meeting dates"""
    try:
        meetings = extract_meetings_from_excel()
        
        meeting_list = []
        for m in meetings:
            meeting_list.append({
                'date': m.strftime('%Y-%m-%d'),
                'display': m.strftime('%d/%m/%Y')
            })
        
        return jsonify({'meetings': meeting_list})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/meeting-analysis', methods=['GET'])
def meeting_analysis():
    """Get meeting-specific analysis with forecast comparisons"""
    try:
        meeting_date = request.args.get('date')
        
        if not meeting_date:
            return jsonify({'error': 'Missing meeting date'}), 400
        
        analysis = get_meeting_analysis(meeting_date)
        
        if analysis is None:
            return jsonify({'error': 'No analysis data available for this meeting'}), 404
        
        return jsonify(analysis)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
