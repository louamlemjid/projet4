import pandas as pd
import os
from pathlib import Path

# Get the directory of the current script
current_dir = Path(__file__).parent

# Load all CSV files from the Aqustat folder
csv_files = list(current_dir.glob("*.csv"))

# Combine all CSV files into one DataFrame
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# Concatenate all dataframes
df_all = pd.concat(dfs, ignore_index=True)

print(f"Total rows loaded: {len(df_all)}")
print(f"Years available: {sorted(df_all['Year'].unique())}")
print("\nAvailable variables:")
for var in df_all['Variable'].unique():
    print(f"  - {var}")

# Calculate AWE (Agricultural Water Efficiency)
# Formula: Awe = (GVA_a × (1 - Cr)) / Va
# 
# Where:
# - GVA_a: Gross Value Added from agriculture (from water use efficiency metric)
# - Cr: Crop requirement coefficient (derived from withdrawal as % of renewable resources)
# - Va: Volume of water used in agriculture (withdrawal volumes)

# Extract relevant metrics
df_pivot = df_all.pivot_table(
    index=['Year', 'Area'],
    columns='Variable',
    values='Value',
    aggfunc='first'
).reset_index()

print("\n" + "="*80)
print("Data structure:")
print(df_pivot.head())

# Calculate AWE using available data
# Using SDG 6.4.1. Irrigated Agriculture Water Use Efficiency as a proxy
if 'SDG 6.4.1. Irrigated Agriculture Water Use Efficiency' in df_pivot.columns:
    df_pivot['AWE_base'] = df_pivot['SDG 6.4.1. Irrigated Agriculture Water Use Efficiency']

# If we have withdrawal percentages, use them as Cr coefficient
if 'Agricultural water withdrawal as % of total renewable water resources' in df_pivot.columns:
    # Normalize the percentage to a coefficient (0-1 range)
    df_pivot['Cr'] = df_pivot['Agricultural water withdrawal as % of total renewable water resources'] / 100
    
    # Calculate adjusted AWE: Awe = GVA_a × (1 - Cr) / Va
    # Here we use the water use efficiency as proxy for GVA_a/Va ratio
    if 'AWE_base' in df_pivot.columns:
        df_pivot['Awe'] = df_pivot['AWE_base'] * (1 - df_pivot['Cr'])
        
        print("\n" + "="*80)
        print("Agricultural Water Efficiency (Awe) calculated using formula:")
        print("Awe = (GVA_a × (1 - Cr)) / Va")
        print("\nWhere:")
        print("  - GVA_a/Va ratio approximated by Irrigated Agriculture Water Use Efficiency")
        print("  - Cr = Agricultural water withdrawal as % of total renewable resources")
        print("\nResults:")
        print(df_pivot[['Year', 'Area', 'Cr', 'AWE_base', 'Awe']].to_string(index=False))
        
        # Save results
        output_file = current_dir / 'awe_results.csv'
        df_pivot[['Year', 'Area', 'Cr', 'AWE_base', 'Awe']].to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")

print("\n" + "="*80)
print("Note: To calculate precise Awe, please provide:")
print("  - GVA_a: Gross Value Added from agriculture (in currency units)")
print("  - Cr: Crop water requirement coefficient or efficiency factor")
print("  - Va: Volume of agricultural water use (in m³)")
