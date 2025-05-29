# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 13:08:14 2025

@author: swiss
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the data
file_path = "weekly_cases_usa2504.csv"
df = pd.read_csv(file_path)

# Convert date columns to datetime
df['week_start'] = pd.to_datetime(df['week_start'])
df['week_end'] = pd.to_datetime(df['week_end'])

# Plot real-world measles cases
plt.figure(figsize=(12, 6))
plt.plot(df['week_start'], df['cases'], label="Reported Measles Cases (USA)", color='red', marker='o')

# Add labels and title
plt.xlabel("Time (Weeks)")
plt.ylabel("Number of Cases")
plt.title("Weekly Measles Cases in the USA")
plt.legend()
plt.grid()
plt.show()


