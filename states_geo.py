# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 13:17:38 2025

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
df_2025 = df[df["year"] == 2025][["geography", "cases_calendar_year"]]

# Check if there are multiple rows per state
#cases_df = df_2025["geography"].value_counts()
print(df_2025.head())  # Check if each state has only one row
print(df_2025.columns)


# Load a shapefile of the USA (for state boundaries)
usa_map = gpd.read_file("https://github.com/PublicaMundi/MappingAPI/raw/master/data/geojson/us-states.json")

# Make sure state names match between both datasets
df_2025["geography"] = df_2025["geography"].str.title()  # Ensure proper capitalization
usa_map["name"] = usa_map["name"].str.title()

# Merge data with the map
map_data = usa_map.merge(df_2025, left_on="name", right_on="geography")

# Plot the map with a color scale based on measles cases
fig, ax = plt.subplots(figsize=(12, 8))

# Customize the color map
norm = mcolors.Normalize(vmin=map_data["cases_calendar_year"].min(), vmax=map_data["cases_calendar_year"].max())
cmap = plt.cm.Reds  # You can change the colormap to others like 'coolwarm', 'viridis', etc.

map_data.plot(column="cases_calendar_year", cmap="Reds", linewidth=0.8, edgecolor="black", legend=True, ax=ax)

plt.title("Measles Cases by State in the USA (2025)", fontsize = 16)
plt.tight_layout()  # Adjust layout to avoid clipping
plt.show()

new_df = pd.read_csv("vaccination_rates_states.csv")

df_2024 = new_df[new_df["school_year"] == "2023-24"][["geography", "categories;"]]
df_2024["geography"] = df_2024["geography"].str.title() 

# Merge data with the map
map_data = usa_map.merge(df_2024, left_on="name", right_on="geography")

# Plot the map with a color scale based on measles cases
fig, ax = plt.subplots(figsize=(10, 6))
map_data.plot(column="categories;", cmap="Blues", linewidth=0.8, edgecolor="black", legend=True, ax=ax)

plt.title("Vaccination Rates by State in the USA")
plt.show()



# Filter the data for Texas
texas_df = new_df[new_df["geography"] == "Texas"]
# Ensure the vaccination rate is in numeric format, removing any '%' symbol if present
texas_df["vaccination_rate"] = texas_df["estimate_pct"].replace("%", "", regex=True).astype(float)

# If there's a year column, we can plot over time (let's assume the column is called "year")
# Ensure that the 'year' column is in the correct format (e.g., string or datetime)
#texas_df["school_year"] = texas_df["school_year"].astype(str)  # Or adjust this to match your year format


# Extract the start year from the 'year' column (split "2023-24" to "2023")
texas_df["start_year"] = texas_df["school_year"].str.split('-').str[0].astype(int)

# Exclude rows where start_year is 2010 or 2009
texas_df_filtered = texas_df[~texas_df["start_year"].isin([2010, 2009])]



# Plot the vaccination rate over the years for Texas
plt.figure(figsize=(10, 6))
plt.plot(texas_df_filtered["start_year"], texas_df_filtered["vaccination_rate"], marker='o', color='b', label="Vaccination Rate")
plt.xlabel("School Year")
plt.ylabel("Vaccination Rate (%)")
plt.title("Vaccination Rates in Texas Over Time")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.show()



# Load the measles cases data (adjust the path to your file)
tex = pd.read_csv("texas2.csv", delimiter=";") 

# Load the shapefile for Texas counties (adjust the shapefile path accordingly)
shapefile_path = "texas/County_Boundaries.shp"  # Update with your actual shapefile path

counties_gdf = gpd.read_file(shapefile_path)


# Inspect the columns and first few rows to confirm county names are in the "CNTY_NM" column
print(counties_gdf.columns)  # Check column names in the shapefile --
print(counties_gdf[['CNTY_NM']].head())  # Preview first few rows of county names

# Ensure that both the county names in the shapefile and measles data are clean
counties_gdf["CNTY_NM"] = counties_gdf["CNTY_NM"].str.strip().str.title()  # Clean the county names
tex["geography"] = tex["geography"].str.strip().str.title()  # Clean the measles data county names


# Merge the measles cases data with the shapefile data using county names
merged = counties_gdf.merge(tex, left_on="CNTY_NM", right_on="geography", how="left")

print(tex.columns)

# Fill missing cases with 0 (or another placeholder)
#merged["cases"] = merged["cases"].fillna(0)  # Replace NaN with 0 for display purposes

# Check if the merge worked and see the result
print(merged[['CNTY_NM', 'cases']].head())  # Or replace 'cases' with your actual column name for measles cases

# Plot the map with measles cases
fig, ax = plt.subplots(figsize=(10, 10))
merged.plot(column='cases', cmap='YlOrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True, missing_kwds={"color": "lightgrey", "label": "No Data"})


# Add title and labels
plt.title("Measles Cases by County in Texas (2025)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()