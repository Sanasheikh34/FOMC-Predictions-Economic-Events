# Market Premium Accuracy Dashboard

## Project Overview
This dashboard analyzes the accuracy of market expectations (meeting premiums) against actual Federal Reserve federal funds target rate changes from 2021-2025.

## Features
- **Dark Theme UI**: Modern, professional design with excellent contrast and readability
- **Interactive Date Range Selector**: Choose any date range to analyze
- **Real-time Chart Updates**: Dynamic line chart showing day-by-day percentage accuracy
- **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Data Files
Ensure these files are in `c:\Users\sana.sheikh\Downloads\`:
- `fredgraph.csv` - Federal funds target range data
- `US MEETING PREMIUMS GENERIC SINCE 2021.csv` - Market premiums data

### 3. Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## Project Structure
```
CODES/
├── app.py                 # Flask backend
├── templates/
│   └── index.html         # Frontend HTML/CSS/JavaScript
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Data Processing
- **Federal Funds Data**: Day-by-day federal funds target range upper/lower limits
- **Meeting Premiums**: Market-priced expectations for each FOMC meeting
- **Accuracy Calculation**: Percentage accuracy of market expectations vs actual changes

## Technical Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charting**: Chart.js
- **Data Processing**: Pandas, NumPy

## Usage
1. Open the dashboard at http://localhost:5000
2. Select a start date and end date
3. Click "Update Chart" to view accuracy data
4. The chart will display day-by-day percentage accuracy for your selected range
