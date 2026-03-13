import pandas as pd
import os

# Debug script to inspect CSV files
print("=" * 60)
print("INSPECTING FEDERAL FUNDS DATA")
print("=" * 60)
try:
    fed_funds = pd.read_csv(r"c:\Users\sana.sheikh\Downloads\fredgraph.csv")
    print(f"Shape: {fed_funds.shape}")
    print(f"\nColumns: {fed_funds.columns.tolist()}")
    print(f"\nFirst 5 rows:")
    print(fed_funds.head())
    print(f"\nData types:\n{fed_funds.dtypes}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("INSPECTING MEETING PREMIUMS DATA")
print("=" * 60)
try:
    downloads = r"c:\Users\sana.sheikh\Downloads"
    files = os.listdir(downloads)
    
    # Find the premium file (could be .xlsx or .csv)
    premium_file = None
    for f in files:
        if 'PREMIUM' in f.upper() and '2021' in f:
            premium_file = os.path.join(downloads, f)
            break
    
    if premium_file:
        print(f"Found file: {premium_file}")
        
        # Read Excel or CSV based on extension
        if premium_file.endswith('.xlsx'):
            premiums = pd.read_excel(premium_file)
        else:
            premiums = pd.read_csv(premium_file)
            
        print(f"Shape: {premiums.shape}")
        print(f"\nColumns: {premiums.columns.tolist()}")
        print(f"\nFirst 5 rows:")
        print(premiums.head())
        print(f"\nData types:\n{premiums.dtypes}")
    else:
        print("Premium file not found!")
except Exception as e:
    print(f"Error: {e}")
    print(f"Shape: {premiums.shape}")
    print(f"\nColumns: {premiums.columns.tolist()}")
    print(f"\nFirst 5 rows:")
    print(premiums.head())
    print(f"\nData types:\n{premiums.dtypes}")
except Exception as e:
    print(f"Error: {e}")
