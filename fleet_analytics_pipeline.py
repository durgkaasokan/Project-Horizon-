import pandas as pd

# Load the telemetry data
df = pd.read_csv("mine_fleet_telemetry.csv")

# Core Carbon Logic Constants
DIESEL_EMISSIONS_FACTOR = 2.68  # kg CO2 per Liter
CARBON_TAX_PER_TONNE = 100.0

# Aggregations
total_diesel_consumed = df["Total_Diesel_Consumed_L"].sum()
total_diesel_saved = df["Ramp_Diesel_Displaced_L"].sum()
total_electricity_bought = df["Grid_Electricity_Drawn_kWh"].sum()

# Carbon calculations
co2_emitted_baseline_tonnes = (total_diesel_consumed * DIESEL_EMISSIONS_FACTOR) / 1000
co2_abated_tonnes = (total_diesel_saved * DIESEL_EMISSIONS_FACTOR) / 1000
carbon_tax_saved = co2_abated_tonnes * CARBON_TAX_PER_TONNE

# Format the output block string
output_text = f"""=== PROJECT HORIZON ADVISORY DATA PIPELINE OUTPUT ===
Total Fleet Operational Rows Processed: {len(df):,}
Baseline Fleet Diesel Footprint:        {total_diesel_consumed:,.2f} Liters
Displaced Ramp Diesel (Trolley):        {total_diesel_saved:,.2f} Liters
New Mine Grid Energy Demand:            {total_electricity_bought:,.2f} kWh
Total Carbon Abated:                    {co2_abated_tonnes:,.2f} Tonnes CO2
Avoided Carbon Regulatory Penalties:    ${carbon_tax_saved:,.2f} USD
"""

# 1. Print to the terminal screen as usual
print(output_text)

# 2. Save the exact same output to a text file
with open("pipeline_summary_output.txt", "w") as f:
    f.write(output_text)

print("Success! Summary report exported to 'pipeline_summary_output.txt'")
