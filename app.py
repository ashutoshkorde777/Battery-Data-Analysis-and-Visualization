import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Initialize storage for battery data
battery_data = {}

# Path to the dataset folder
dataset_path = r'D:\battery_graphs\cleaned_dataset'
dataset_path2 = r'D:\battery_graphs\cleaned_dataset\data'

# Read the metadata file
metadata_path = os.path.join(dataset_path, 'metadata.csv')
metadata_df = pd.read_csv(metadata_path)

# Helper function to safely convert to complex
def safe_eval(value):
    if isinstance(value, str):
        try:
            return complex(eval(value))
        except Exception:
            return None  # Return None for invalid data
    return value  # Return original if already numeric

# Process each row in the metadata file
for _, row in metadata_df.iterrows():
    file_type = row['type']
    file_path = os.path.join(dataset_path2, row['filename'])
    battery_id = row['battery_id']
    
    # Initialize storage for the battery ID if not already done
    if battery_id not in battery_data:
        battery_data[battery_id] = {
            'charge': [],
            'discharge': [],
            'impedance': [],
            'capacity': [],
            'Re': [],
            'Rct': []
        }

    try:
        # Read the data file based on the file type
        df = pd.read_csv(file_path)

        if file_type == 'charge':
            # Extract fields for charge
            charge_data = {
                'Voltage_measured': df['Voltage_measured'],
                'Current_measured': df['Current_measured'],
                'Temperature_measured': df['Temperature_measured'],
                'Current_charge': df['Current_charge'],
                'Voltage_charge': df['Voltage_charge'],
                'Time': df['Time']
            }
            battery_data[battery_id]['charge'].append(charge_data)

        elif file_type == 'discharge':
            # Extract fields for discharge
            discharge_data = {
                'Voltage_measured': df['Voltage_measured'],
                'Current_measured': df['Current_measured'],
                'Temperature_measured': df['Temperature_measured'],
                'Current_load': df['Current_load'],
                'Voltage_load': df['Voltage_load'],
                'Time': df['Time'],
                'Capacity': row['Capacity']
            }
            battery_data[battery_id]['discharge'].append(discharge_data)

        elif file_type == 'impedance':
            # Safely convert impedance-related columns to complex numbers
            df['Sense_current'] = df['Sense_current'].apply(safe_eval)
            df['Battery_current'] = df['Battery_current'].apply(safe_eval)
            df['Battery_impedance'] = df['Battery_impedance'].apply(safe_eval)
            df['Rectified_impedance'] = df['Rectified_Impedance'].apply(safe_eval)

            # Drop rows with invalid data
            df = df.dropna(subset=['Battery_impedance'])

            # Calculate magnitudes and phases
            df['Impedance_magnitude'] = df['Battery_impedance'].apply(np.abs)
            df['Impedance_phase'] = df['Battery_impedance'].apply(np.angle)
            df['Rectified_magnitude'] = df['Rectified_impedance'].apply(np.abs)
            df['Rectified_phase'] = df['Rectified_impedance'].apply(np.angle)

            # Extract Re and Rct (real and imaginary parts)
            df['Re'] = df['Battery_impedance'].apply(lambda z: z.real)
            df['Rct'] = df['Battery_impedance'].apply(lambda z: z.imag)

            # Store impedance data
            impedance_data = {
                'Sense_current': df['Sense_current'].tolist(),
                'Battery_current': df['Battery_current'].tolist(),
                'Battery_impedance': df['Battery_impedance'].tolist(),
                'Impedance_magnitude': df['Impedance_magnitude'].tolist(),
                'Impedance_phase': df['Impedance_phase'].tolist(),
                'Re': df['Re'].tolist(),
                'Rct': df['Rct'].tolist()
            }
            battery_data[battery_id]['impedance'].append(impedance_data)
            
            # Append Re and Rct values from metadata
            battery_data[battery_id]['Re'].extend(df['Re'].tolist())
            battery_data[battery_id]['Rct'].extend(df['Rct'].tolist())

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Function to create plots
# Function to create plots with Time on x-axis
def create_plots(battery_id, battery_data):
    # Plot Battery Impedance over Time
    impedance_data = battery_data[battery_id]['impedance']
    if impedance_data:
        fig = go.Figure()
        for idx, entry in enumerate(impedance_data):
            # Create a normalized time axis if needed
            time_axis = pd.Series(range(len(entry['Impedance_magnitude'])))
            
            # Update if 'Time' is available
            if 'Time' in entry:
                try:
                    time_axis = pd.to_datetime(entry['Time'])
                except Exception:
                    time_axis = pd.to_numeric(entry['Time'])  # Default to numeric

            fig.add_trace(go.Scatter(
                x=time_axis,
                y=entry['Impedance_magnitude'],
                mode='lines',
                name=f'Impedance Cycle {idx+1}'
            ))

        fig.update_layout(
            title=f'Battery Impedance Magnitude Over Time for Battery {battery_id}',
            xaxis_title='Time',
            yaxis_title='Impedance Magnitude (Ohms)'
        )
        fig.show()

    # Plot Re and Rct over cycles
    re_values = battery_data[battery_id]['Re']
    rct_values = battery_data[battery_id]['Rct']
    if re_values and rct_values:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, len(re_values) + 1)), y=re_values, mode='lines+markers', name='Re'))
        fig.add_trace(go.Scatter(x=list(range(1, len(rct_values) + 1)), y=rct_values, mode='lines+markers', name='Rct'))

        fig.update_layout(
            title=f'Re and Rct Over Cycles for Battery {battery_id}',
            xaxis_title='Cycles',
            yaxis_title='Resistance (Ohms)'
        )
        fig.show()

# Create plots for each battery
# creating just for five for for now
count = 0
for battery_id in battery_data:
    create_plots(battery_id, battery_data)
    count = count + 1
    if count==5:
        break
