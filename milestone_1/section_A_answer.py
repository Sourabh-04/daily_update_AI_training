import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("urban_mobility.csv")

print(df.head())

print("This file is structure one becasue it have well define rows ad column")

df["Energy_Per_Km"] = (df["Energy_Used_kWh"]/df["Distance_Km"])

# ----
result = df[(df["Vehicle_Type"]=="Electric Van") & (df['Maintenance_Flag']=='Yes')]
print(result)

# ---
result = df.groupby("Vehicle_Type").agg(Average_Distance_km=("Distance_Km","mean"),
                                         Total_Trip_Count=("Trips_Count","sum"))
print("Answer for the average distance",result)

# ----

energy = df["Energy_Per_Km"].to_numpy()
print("Mean",np.mean(energy))
print("Max",np.max(energy))
print("Min",np.min(energy))


avg_energy = df.groupby("Vehicle_Type")["Energy_Used_kWh"].mean()
avg_energy.plot(kind="bar")
plt.xlabel("Vehicle Type")
plt.ylabel("Energy Used (kWh)")
plt.title("Energy Used (kWh)")
plt.tight_layout()
plt.show()

import json
with open('equipment_events.json','r') as file:
    df_eq = json.load(file)

print("A7:")
for event in df_eq:
    print(
        f"Event ID: {event.get('event_id')}, "
        f"Asset Type: {event.get('asset_type')}, "
        f"Site: {event.get('site')}, "
        f"Severity: {event.get('severity')}"
    )

print("\nA8:")
for event in df_eq:
    if event.get("temperature", 0) > 70:
        actions = event.get("actions", "No actions recorded")
        print(event)
        print("Actions:", actions)

# A9
with open("coastal_monitoring_log.txt", "r") as file:
    text = file.read()

words = text.split()
total_words = len(words)
inspection_count = text.lower().count("inspection")

print("Total Words:", total_words)
print("Inspection Count:", inspection_count)


# A10

for line in text.split("\n"):


    for word in line.split():

        if word in ["boardwalk", "maintenance", "wind"]:
            print(line)

# .json is semi structure
#
# .csv is structure and .txt is unstructure one.