# FOMC Dashboard - Display Issues Fixed & Indicator Selection Updated

## Changes Made

### 1. Fixed Event Lines Rendering Issue
**Problem:** Event lines were being defined inline within Chart.js options, causing closure/scoping issues and preventing proper rendering.

**Solution:** 
- Registered `eventLines` as a global Chart.js plugin using `Chart.register()`
- Plugin properly accesses chart data from `chart.data.eventData` and `chart.data.dates`
- Plugin correctly filters by selected indicators using `selectedIndicators` object

### 2. Replaced Simple Toggle with Multi-Indicator Selection
**Old Approach:** Single checkbox for "Show All Economic Events"

**New Approach:** Individual checkboxes for each of the 10 indicators:
- NFP (Green #4ade80)
- ADP (Yellow #facc15)
- CPI (Red #ef4444)
- Core PCE (Blue #3b82f6)
- Retail Sales (Orange #f97316)
- GDP (Cyan #06b6d4)
- ECI (Magenta #ec4899)
- PPI (Violet #a855f7)
- JOLTS (Lime #84cc16)
- Jobless Claims (Indigo #6366f1)

**Features:**
- ✅ All indicators selected by default
- ✅ Colored checkbox indicators showing each indicator's color
- ✅ Grid layout for easy selection
- ✅ Only appears AFTER meeting selection (dynamically injected)
- ✅ Real-time chart updates when toggling indicators

### 3. Improved Click Detection for Event Lines
**Previous Issue:** Click handlers were being added multiple times in event listeners, causing performance issues.

**New Approach:**
- Single click handler added to canvas after chart creation
- Properly detects clicks within 15px of vertical event lines
- Respects selected indicators (only shows panel for selected types)
- Uses chart scales to calculate exact line positions

### 4. JavaScript Architecture Improvements
**globalPlugin:**
```javascript
Chart.register({
    id: 'eventLines',
    afterDatasetsDraw(chart) {
        // Plugin now properly accesses:
        // - chart.data.eventData (array of events)
        // - chart.data.dates (array of dates for matching)
        // - selectedIndicators (object tracking selected types)
    }
});
```

**Data Structure:**
```javascript
let selectedIndicators = {
    'NFP': true,
    'ADP': true,
    'CPI': true,
    // ... all 10 indicators
};

const indicatorColors = {
    'NFP': '#4ade80',
    'ADP': '#facc15',
    // ... all 10 colors
};
```

**Dynamic Selection:**
- `injectIndicatorSelectors()` - Creates checkboxes from indicator configuration
- `updateSelectedIndicators()` - Updates selectedIndicators object on checkbox change
- Charts auto-redraw when selection changes

### 5. Event Panel Enhanced
- Title shows indicator type with matching color
- Panel border color matches indicator color
- Properly formatted data display based on indicator type

## How It Works Now

1. **User selects a meeting** from dropdown
2. **Click "Analyze Meeting"** button
3. **Indicator selection checkboxes appear** with all 10 indicators selected by default
4. **Charts render with event lines** in color-coded vertical lines
5. **User can toggle indicators** on/off to show/hide specific event types
6. **Click on an event line** to see detailed information in the right panel
7. **Event panel shows** indicator type, dates, actual/forecast values

## Technical Details

**Event Line Rendering:**
- Uses Chart.js custom plugin (afterDatasetsDraw hook)
- Draws dashed vertical lines using canvas context
- Colors match indicator type from `event.color`
- Lines only draw for selected indicators

**Click Detection:**
- Uses canvas bounding rect for accurate coordinate calculation
- Tolerance of ±15px for easier clicking
- Filters for selected indicators before showing panel

**CSS Considerations:**
- Grid layout for checkboxes: `repeat(auto-fit, minmax(150px, 1fr))`
- Color squares: 12px height/width with 2px border radius
- Responsive design maintains usability on all screen sizes

## Files Modified
- `templates/index.html` - Updated JavaScript plugin system, checkbox logic, and click handlers
- No changes needed to `app.py` (API already working correctly)

## Status: COMPLETE ✅

All 10 economic indicators are now:
- ✅ Loading and rendering event lines on charts
- ✅ Color-coded by indicator type
- ✅ Individually selectable via checkboxes
- ✅ Clickable to show detailed event information
- ✅ Real-time chart updates on selection change
