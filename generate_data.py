import pandas as pd
import numpy as np
import random

# Configuration
NUM_ENTRIES = 1000

# Define Equipment Types
types = ['Reactor', 'Separator', 'Pump', 'Heat Exchanger']
# Probabilities (30% Reactors, 30% Separators, 20% Pumps, 20% Exchangers)
type_weights = [0.3, 0.3, 0.2, 0.2]

# statuses
statuses = ['Operational', 'Maintenance', 'Error', 'Offline']
status_weights = [0.85, 0.05, 0.05, 0.05]

# Generate Base Data
data = {
    'EquipmentID': [f'EQ-{i:04d}' for i in range(1, NUM_ENTRIES + 1)],
    'Type': np.random.choice(types, NUM_ENTRIES, p=type_weights),
    'Status': np.random.choice(statuses, NUM_ENTRIES, p=status_weights)
}

# Generate Realistic Physics Data
temps = []
pressures = []
flowrates = []

for t in data['Type']:
    if t == 'Reactor':
        # Reactors: High Temp, Medium Pressure
        temps.append(random.uniform(150, 350))
        pressures.append(random.uniform(10, 50))
        flowrates.append(random.uniform(50, 150))
    elif t == 'Separator':
        # Separators: Medium Temp, Low Pressure
        temps.append(random.uniform(50, 150))
        pressures.append(random.uniform(5, 20))
        flowrates.append(random.uniform(100, 300))
    elif t == 'Pump':
        # Pumps: Low Temp, Very High Pressure
        temps.append(random.uniform(20, 80))
        pressures.append(random.uniform(50, 150)) 
        flowrates.append(random.uniform(200, 500))
    else: # Heat Exchanger
        # Exchanger: Variable Temp, Medium Pressure
        temps.append(random.uniform(80, 250))
        pressures.append(random.uniform(10, 40))
        flowrates.append(random.uniform(100, 400))

# Add to dictionary and round values
data['Temperature'] = np.round(temps, 1)
data['Pressure'] = np.round(pressures, 1)
data['Flowrate'] = np.round(flowrates, 1)

# Create DataFrame and Save
df = pd.DataFrame(data)
df.to_csv('large_dataset.csv', index=False)

print(f"✅ Success! Generated 'large_dataset.csv' with {NUM_ENTRIES} rows.")