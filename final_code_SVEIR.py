# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 14:33:27 2025

@author: swiss
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import pearsonr

# Load data
df = pd.read_excel("april30cases.xlsx")

# Preprocess observed data
df['cumulative_cases'] = df['cases'].cumsum()
df['new_cases'] = df['cases']
df['smoothed_cases'] = (df['new_cases']
    .rolling(3, center=True) # 3 day moving average, smooth fluctuations
    .mean()
    .bfill()
    .ffill()
)

# Remove the first 6 cases
df = df.iloc[6:].reset_index(drop=True)  # Drop first 6 rows and reset the index


# Prepare time series
days_since_start = np.arange(len(df))
observed_daily_cases = df['new_cases'].values #without smoothed values, otherwise change here

# Parameters
N = 7000 #but child population in Texas: 7 million, 7-8000 in Gaines community
gamma_fixed = 1 / 10  # Recovery rate roughly 10 days
sigma = 1 / 11      # Incubation to infectious transition rate, latent period roughly 12 days
I0 = 20
vaccination_rate = 0.8 #change this to 0, 0.5, 0.8, 0.95
#1 leads to false interpretations!!!!

# Initial populations
Sv0 = int(N * vaccination_rate)
E0 = 50
R0 = 0
S0 = N - I0 - Sv0 - E0 -R0
vacc_factor = 1- 0.97 #vaccine protection, 3% still susceptible

# Time settings
t_max = len(df) + 400  # Slightly extend past available data
t_eval = np.linspace(0, t_max - 1, t_max)

# SEIR ODE SYstem
def seir_vaccine_model(t, y, beta, gamma, sigma, vacc_factor):
    S, Sv, E, I, R = y
    N = S + Sv + E + I + R
    dSdt = -beta * S * I / N
    dSvdt = -beta * vacc_factor * Sv * I / N
    dEdt = beta * S * I / N + beta * vacc_factor * Sv * I / N - sigma * E
    dIdt = sigma * E - gamma * I
    dRdt = gamma * I
    return [dSdt, dSvdt, dEdt, dIdt, dRdt]

# Objective function, solves ODE for a trial beta
def objective(beta):
    
    sol = solve_ivp(seir_vaccine_model, [0, t_max], [S0, Sv0, E0, I0, R0], t_eval=t_eval,
                    args=(beta[0], gamma_fixed, sigma, vacc_factor))
    
    E = sol.y[2]
    predicted_daily_cases = sigma * E #new daily cases should come from the transition from Exposed → Infected,
    
    # Match length to observed data
    min_len = min(len(predicted_daily_cases), len(observed_daily_cases))
    predicted_trimmed = predicted_daily_cases[:min_len]
    observed_trimmed = observed_daily_cases[:min_len]
    
    diff = predicted_trimmed - observed_trimmed #compares cases
    return np.sum(diff ** 2) #minimize squared error to fit beta

# Optimization
initial_beta_guess = [0.5]
result = minimize(objective, initial_beta_guess, method='Nelder-Mead')
beta_opt = result.x[0]
print(f"Optimized beta: {beta_opt:.4f}, gamma: {gamma_fixed:.4f}, sigma: {sigma:.4f}")

# Final model run with optimal beta

sol = solve_ivp(seir_vaccine_model, [0, t_max], [S0, Sv0, E0, I0, R0], t_eval=t_eval,
                args=(beta_opt, gamma_fixed, sigma, vacc_factor))
S, Sv, E, I, R = sol.y
predicted_daily_cases = sigma * E

# Match data lengths
min_len = min(len(predicted_daily_cases), len(observed_daily_cases))
predicted_trimmed = predicted_daily_cases[:min_len]
observed_trimmed = observed_daily_cases[:min_len]

R0_estimate = beta_opt / gamma_fixed
print(f"Estimated R0: {R0_estimate:.2f}")
vaccine_efficacy = 0.97
Reff = R0_estimate * (1 - vaccination_rate * vaccine_efficacy)
print(f"Estimated Effective Reproduction Number (Reff): {Reff:.2f}")

# Fit evaluation
mse = mean_squared_error(observed_trimmed, predicted_trimmed)
rmse = np.sqrt(mse)
r2 = r2_score(observed_trimmed, predicted_trimmed)
 

print(f"\nModel Fit Statistics:")
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
print(f"R² Score: {r2:.4f}")


"""Model Fit Statistics:
Mean Squared (MSE): 27.2783
Root Mean Squared Error (RMSE): 5.2229, off by 5 cases per day, on average
R² Score: -2.1811"""


# Compute Pearson correlation coefficient and p-value
r_value, p_value = pearsonr(predicted_trimmed, observed_trimmed)

#print(f"Pearson Correlation (r): {r_value:.4f}")
#print(f"P-value: {p_value:.4e}")
""" pearson correlation = 0.73 strong positive correlation
 p value: 6.4592e-13: <0.05 the correlation is unlikely due to chance"""

# Residual plot
residuals = observed_trimmed - predicted_trimmed
plt.figure(figsize=(10, 4))
plt.plot(residuals, marker='o', linestyle='-', color='gray')
plt.axhline(0, color='black', linestyle='--')
plt.title("Residuals (Observed - Predicted)")
plt.xlabel("Day")
plt.ylabel("Residual")
plt.grid(True)
plt.tight_layout()
plt.show()



# Plotting
plt.figure(figsize=(12, 8))

plt.plot(days_since_start, df['new_cases'] , label="Observed Daily Cases (Smoothed)", color='black', marker='o')
plt.plot(t_eval, predicted_daily_cases, label="Predicted Daily Cases", color='orange', linewidth=2)
plt.xlabel("Days")
plt.ylabel("Cases")
plt.grid()
plt.tight_layout()
plt.show()


plt.figure(figsize=(12, 8))
plt.plot(t_eval, S, label="Susceptible (Unvaccinated)", color='blue', linestyle='--')
plt.plot(t_eval, Sv, label="Susceptible (Vaccinated)", color='grey', linestyle=':')
plt.plot(t_eval, E, label="Exposed", color='purple', linestyle='-.')
plt.plot(t_eval, I, label="Infected", color='red')
plt.plot(t_eval, R, label="Recovered", color='green')

plt.xlabel("Days")
plt.ylabel("Population / Cases")
#plt.ylim(0, 7000)  # <-- Enforces plot scale for 0.5
plt.title(f"SVEIR Model Fit with {int(vaccination_rate * 100)}% Vaccination")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()


