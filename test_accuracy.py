import sys
sys.path.insert(0, r'c:\Users\sana.sheikh\CODES')

from app import calculate_daily_accuracy

# Test with a date range
result = calculate_daily_accuracy('2021-01-01', '2021-12-31')

print(f"Number of records: {len(result)}")
print(f"\nFirst 5 records:")
for i, item in enumerate(result[:5]):
    print(f"  {item}")

print(f"\nLast 5 records:")
for item in result[-5:]:
    print(f"  {item}")

print(f"\nAccuracy range: {min([r['Accuracy'] for r in result])} to {max([r['Accuracy'] for r in result])}")
