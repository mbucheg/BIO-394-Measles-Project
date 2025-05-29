# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 15:49:08 2025

@author: swiss
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the data
file_path = "cases_states2504.csv"  # Update with the correct file path
df = pd.read_csv(file_path)

# Filter for the year 2025
df_2025 = df[df["year"] == 2025]

# Filter for the year 2025 and select relevant columns
df_2025 = df[df["year"] == 2025][["geography", "cases_range"]]

# Check the categories in the cases_range column
print(df_2025["cases_range"].unique())  # This shows the categories in the cases_range column

# Define a function to convert 'cases_range' to a numerical value
def cases_range_to_numeric(cases_range):
    if cases_range == '0':
        return 0
    elif cases_range == '1-9':
        return 5
    elif cases_range == "10-49":
        return 25
    elif cases_range == '50-99':
        return 150
    elif cases_range == '250+':
        return 250
    else:
        return -1  # In case there are unexpected categories

# Apply the function to create a new numeric column
df_2025["cases_numeric"] = df_2025["cases_range"].apply(cases_range_to_numeric)

# Load a shapefile of the USA (for state boundaries)
usa_map = gpd.read_file("https://github.com/PublicaMundi/MappingAPI/raw/master/data/geojson/us-states.json")

# Make sure state names match between both datasets
df_2025["geography"] = df_2025["geography"].str.title()  # Ensure proper capitalization
usa_map["name"] = usa_map["name"].str.title()

# Merge data with the map
map_data = usa_map.merge(df_2025, left_on="name", right_on="geography")

# Plot the map with a color scale based on the numerical conversion of 'cases_range'
fig, ax = plt.subplots(figsize=(12, 8))

# Create custom boundaries for the color scale
boundaries = [0, 5, 25, 50, 100, 250]  # Define breaks where the color changes more significantly
# Create the color map (gradient) for numerical values
cmap = plt.cm.get_cmap("Reds")  # You can use any continuous colormap you prefer

norm = mcolors.BoundaryNorm(boundaries, cmap.N)  # Normalize based on the custom breaks

# Plot the states with the continuous color scale
map_data.plot(column="cases_numeric", cmap=cmap, linewidth=0.8, edgecolor="black", legend=True, ax=ax, norm=norm)

# Customize the title and labels
plt.title("Measles Cases by State in the USA (2025)", fontsize=16)

# Adjust the legend to match the color scale
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')

# Show the plot
plt.tight_layout()  # Adjust layout to avoid clipping
plt.show()
