import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Configuration
NUM_TRUCKS = 40
DAYS = 365
RECORDS_PER_DAY_PER_TRUCK = 10  # Simulating aggregated haul cycles per shift

start_date = datetime(2026, 1, 1)
data = []

print("Generating operational telemetry dataset...")

for day in range(DAYS):
    current_date = start_date + timedelta(days=day)
    for truck_id in range(1, NUM_TRUCKS + 1):
        for cycle in range(RECORDS_PER_DAY_PER_TRUCK):
            
            pit_floor_liters = random.uniform(15.0, 25.0)
            surface_liters = random.uniform(10.0, 18.0)
            ramp_climb_liters = random.uniform(22.0, 30.0) 
            
            total_diesel_burned = pit_floor_liters + ramp_climb_liters + surface_liters
            diesel_displaced = ramp_climb_liters
            electricity_kwh_needed = (diesel_displaced * 10) / 3.0
            
            data.append({
                "Timestamp": current_date.strftime("%Y-%m-%d"),
                "Truck_ID": f"CAT-793-{truck_id:02d}",
                "Cycle_ID": f"CYC-{day:03d}-{cycle:02d}",
                "Total_Diesel_Consumed_L": round(total_diesel_burned, 2),
                "Ramp_Diesel_Displaced_L": round(diesel_displaced, 2),
                "Grid_Electricity_Drawn_kWh": round(electricity_kwh_needed, 2)
            })

df = pd.DataFrame(data)
df.to_csv("mine_fleet_telemetry.csv", index=False)
print("Success! 'mine_fleet_telemetry.csv' generated with data links.")
