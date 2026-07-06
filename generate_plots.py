import pandas as pd
import matplotlib.pyplot as plt

print("Loading telemetry data and preparing visualizations...")

# Load the generated telemetry dataset
try:
    df = pd.read_csv("mine_fleet_telemetry.csv")
except FileNotFoundError:
    print("Error: 'mine_fleet_telemetry.csv' not found. Please run haul_cycle_simulator.py first.")
    exit()

# Convert timestamps and extract months for chronological aggregation
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Month'] = df['Timestamp'].dt.strftime('%b')
months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

monthly_summary = df.groupby('Month').agg({
    'Total_Diesel_Consumed_L': 'sum',
    'Ramp_Diesel_Displaced_L': 'sum'
}).reindex(months_order)

# Calculate remaining diesel burned outside the ramp lines
monthly_summary['Remaining_Diesel_L'] = monthly_summary['Total_Diesel_Consumed_L'] - monthly_summary['Ramp_Diesel_Displaced_L']

# Set clean style parameters
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# --- CHART 1: MONTHLY FUEL DISPLACEMENT PROFILE ---
fig, ax = plt.subplots(figsize=(10, 6))

# Construct professional stacked bars (values converted to thousands for readability)
bars1 = ax.bar(monthly_summary.index, monthly_summary['Ramp_Diesel_Displaced_L'] / 1e3, 
               label='Displaced Diesel (Trolley Assist On-Ramp)', color='#3b82f6', 
               bottom=monthly_summary['Remaining_Diesel_L'] / 1e3, width=0.6)
bars2 = ax.bar(monthly_summary.index, monthly_summary['Remaining_Diesel_L'] / 1e3, 
               label='Remaining Diesel (Pit Floor & Surface)', color='#64748b', width=0.6)

ax.set_title('Monthly Fleet Diesel Consumption & Displacement Profile (2026)', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
ax.set_xlabel('Operational Month', fontsize=11, labelpad=10, color='#334155')
ax.set_ylabel('Fuel Volume (Thousand Liters)', fontsize=11, labelpad=10, color='#334155')
ax.grid(axis='y', linestyle='--', alpha=0.5, color='#e2e8f0')
ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0')

plt.tight_layout()
plt.savefig('monthly_diesel_displacement.png', dpi=300)
plt.close()
print("Success: 'monthly_diesel_displacement.png' exported.")

# --- CHART 2: BEFORE vs AFTER CO2 EMISSIONS ---
DIESEL_EMISSIONS_FACTOR = 2.68  # kg CO2 per Liter
total_diesel = df["Total_Diesel_Consumed_L"].sum()
total_saved = df["Ramp_Diesel_Displaced_L"].sum()

co2_baseline = (total_diesel * DIESEL_EMISSIONS_FACTOR) / 1000
co2_abated = (total_saved * DIESEL_EMISSIONS_FACTOR) / 1000
co2_post = co2_baseline - co2_abated

fig, ax = plt.subplots(figsize=(6, 6))
categories = ['Baseline\n(Status Quo)', 'Post-Electrification\nStrategy']
emissions = [co2_baseline, co2_post]
colors = ['#dc2626', '#16a34a']

bars = ax.bar(categories, emissions, color=colors, width=0.45)
ax.set_title('Annual Fleet $\\text{CO}_2$ Emissions Impact', fontsize=13, fontweight='bold', pad=15, color='#0f172a')
ax.set_ylabel('Annual $\\text{CO}_2$ Emissions (Metric Tonnes)', fontsize=11, labelpad=10, color='#334155')
ax.grid(axis='y', linestyle='--', alpha=0.5, color='#e2e8f0')

# Label values directly on top of the bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + (co2_baseline * 0.02), 
            f"{yval:,.0f} t", ha='center', va='bottom', fontweight='bold', color='#1e293b')

ax.set_ylim(0, co2_baseline * 1.15)
plt.tight_layout()
plt.savefig('co2_emissions_comparison.png', dpi=300)
plt.close()
print("Success: 'co2_emissions_comparison.png' exported.")
print("All engineering charts compiled beautifully!")
