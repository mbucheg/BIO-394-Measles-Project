# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 15:34:44 2025

@author: swiss
"""

import random
import matplotlib.pyplot as plt

# Step 1: Define the Grid and Agents
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[[] for _ in range(width)] for _ in range(height)]  # each cell holds a list of agents

    def place_agent(self, agent, x, y):
        self.grid[y][x].append(agent)
        agent.pos = (x, y)

    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, E, W directions
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny))
        return neighbors

# Agent class
class Agent:
    def __init__(self, unique_id, grid, vaccination_rate=0):
        self.unique_id = unique_id
        self.grid = grid
        self.pos = None
        self.state = "susceptible"  # Can be "susceptible", "exposed", "infected", "recovered", "vaccinated"
        self.infection_time = 0
        self.vaccination_rate = vaccination_rate

        # Vaccinated or not based on vaccination_rate
        if random.random() < vaccination_rate:
            self.state = "vaccinated"
            if random.random() < 0.03:  # 3% of vaccinated people are unprotected
                self.vaccine_failed = True
            else: self.vaccine_failed = False
          

    def move(self):
        if self.pos is None or random.random() > 0.5:
            return  # 80% chance to move each time
    
        x, y = self.pos
        neighbors = self.grid.get_neighbors(x, y)
        if not neighbors:
            return
    
        new_x, new_y = random.choice(neighbors)
    
        self.grid.grid[y][x].remove(self)
        self.grid.place_agent(self, new_x, new_y)



    def interact(self):
        if self.state == "infected":
            x, y = self.pos
            neighbors = self.grid.get_neighbors(x, y)
            for nx, ny in neighbors:
                neighbor_agents = self.grid.grid[ny][nx]
                for neighbor in neighbor_agents:
                    if neighbor.state == "susceptible":
                        if random.random() < 0.97:  # Infection probability at 97%
                            neighbor.state = "exposed"
                    if neighbor.state == "vaccinated" and neighbor.vaccine_failed: #only the 3%
                        neighbor.state = "exposed"
                       

            self.infection_time += 1
            if self.infection_time > 10:  # After 10 steps, recover
                self.state = "recovered"
                self.infection_time = 0

        elif self.state == "exposed":
            self.infection_time += 1
            if self.infection_time > 11:  # After 11 steps, become infected
                self.state = "infected"
                self.infection_time = 0

# Step 2: Create the Model
class Model:
    def __init__(self, width, height, num_agents, vaccination_rate=0.5):  #default value, will be overridden below if there's a value
        self.grid = Grid(width, height)
        self.agents = []

        for i in range(num_agents):
            agent = Agent(i, self.grid, vaccination_rate)
            self.agents.append(agent)

            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.grid.place_agent(agent, x, y)

       
        # Randomly infect multiple agents initially
        #num_initial_infected = max(1, int(0.05 * len(self.agents)))  # 5% of agents
        num_initial_infected = 1
        
        initial_infected_agents = random.sample(self.agents, num_initial_infected)
        
        for agent in initial_infected_agents:
            agent.state = "infected"


    def step(self):
        for agent in self.agents:
            agent.interact()
        for agent in self.agents:
            agent.move()
        

    def get_state(self):
        state = {"susceptible": 0, "exposed": 0, "infected": 0, "recovered": 0, "vaccinated": 0}
        for agent in self.agents:
            state[agent.state] += 1
        return state

# Step 3: Run Simulation
def run_simulation(model, num_steps):
    susceptible_counts = []
    exposed_counts = []
    infected_counts = []
    recovered_counts = []
    vaccinated_counts = []

    for step in range(num_steps):
        model.step()
        state = model.get_state()
        susceptible_counts.append(state["susceptible"])
        exposed_counts.append(state["exposed"])
        infected_counts.append(state["infected"])
        recovered_counts.append(state["recovered"])
        vaccinated_counts.append(state["vaccinated"])

    return susceptible_counts, exposed_counts, infected_counts, recovered_counts, vaccinated_counts

# Step 4: Visualization with Matplotlib (Real-Time Grid View)
def visualize(model):
    susceptible_x = []
    susceptible_y = []
    infected_x = []
    infected_y = []
    exposed_x = []
    exposed_y = []
    recovered_x = []
    recovered_y = []
    vaccinated_x = []
    vaccinated_y = []

    for agent in model.agents:
        x, y = agent.pos
        if agent.state == "susceptible":
            susceptible_x.append(x)
            susceptible_y.append(y)
        elif agent.state == "infected":
            infected_x.append(x)
            infected_y.append(y)
        elif agent.state == "exposed":
            exposed_x.append(x)
            exposed_y.append(y)
        elif agent.state == "recovered":
            recovered_x.append(x)
            recovered_y.append(y)
        elif agent.state == "vaccinated":
            vaccinated_x.append(x)
            vaccinated_y.append(y)

    plt.clf()
    plt.scatter(susceptible_x, susceptible_y, color='blue', label='Susceptible', s=30)
    plt.scatter(infected_x, infected_y, color='red', label='Infected', s=30)
    plt.scatter(exposed_x, exposed_y, color='purple', label='Exposed', s=30)
    plt.scatter(recovered_x, recovered_y, color='green', label='Recovered', s=30)
    plt.scatter(vaccinated_x, vaccinated_y, color='grey', label='Vaccinated', s=30)

    plt.xlim(-1, model.grid.width)
    plt.ylim(-1, model.grid.height)
    plt.xlabel("X Position")
    plt.ylabel("Y Position")

    plt.title("Infection Simulation")

    # Only draw one legend per frame
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Remove duplicates
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.pause(0.2)

# Step 5: SIR-style Plot
def plot_results(susceptible_counts, exposed_counts, infected_counts, recovered_counts, vaccinated_counts):
    plt.figure(figsize=(10, 6))
    plt.plot(susceptible_counts, label="Susceptible", color='blue')
    plt.plot(exposed_counts, label="Exposed", color='purple')
    plt.plot(infected_counts, label="Infected", color='red')
    plt.plot(recovered_counts, label="Recovered", color='green')
    plt.plot(vaccinated_counts, label="Vaccinated", color='grey')
    plt.xlabel("Time (Steps)")
    plt.ylabel("Number of Agents")
    plt.ylim(0, 7000)
    plt.title("Agent-Based Model: Infection Dynamics")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.grid()
    plt.show()

# Step 6: Run the Real-Time Visualization
model_for_visual = Model(width=20, height=20, num_agents=400, vaccination_rate=0.5)
plt.figure(figsize=(8, 8))

for _ in range(100):
    model_for_visual.step()
    visualize(model_for_visual)

plt.show()

# Step 7: Plot the SIR Curve with Exposed and Vaccinated
model_for_data = Model(width=80, height=85, num_agents=7000, vaccination_rate=0.5)
num_steps = 500
susceptible_counts, exposed_counts, infected_counts, recovered_counts, vaccinated_counts = run_simulation(model_for_data, num_steps)
plot_results(susceptible_counts, exposed_counts, infected_counts, recovered_counts, vaccinated_counts)
