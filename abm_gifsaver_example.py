# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 15:24:06 2025

@author: swiss
"""

import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Grid class
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[[] for _ in range(width)] for _ in range(height)]

    def place_agent(self, agent, x, y):
        self.grid[y][x].append(agent)
        agent.pos = (x, y)

    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
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
        self.state = "susceptible"
        self.infection_time = 0
        self.vaccination_rate = vaccination_rate

        if random.random() < vaccination_rate:
            self.state = "vaccinated"

    def move(self):
        if self.pos is None or random.random() > 0.5:
            return

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
                for neighbor in self.grid.grid[ny][nx]:
                    if neighbor.state == "susceptible":
                        if random.random() < 0.97:
                            neighbor.state = "exposed"
                    if neighbor.state == "vaccinated":
                        if random.random() < 0.03:  # Vaccine failure chance (97% protection) 1- 0.97
                            neighbor.state = "exposed"
            self.infection_time += 1
            if self.infection_time > 10:
                self.state = "recovered"
                self.infection_time = 0

        elif self.state == "exposed":
            self.infection_time += 1
            if self.infection_time > 11:
                self.state = "infected"
                self.infection_time = 0

# Model class
class Model:
    def __init__(self, width, height, num_agents, vaccination_rate=0.8): 
        self.grid = Grid(width, height)
        self.agents = []

        for i in range(num_agents):
            agent = Agent(i, self.grid, vaccination_rate)
            self.agents.append(agent)

            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.grid.place_agent(agent, x, y)

        num_initial_infected = max(1, int(0.05 * len(self.agents)))
        initial_infected = random.sample(self.agents, num_initial_infected)
        for agent in initial_infected:
            agent.state = "infected"

    def step(self):
        for agent in self.agents:
            agent.interact()
        for agent in self.agents:
            agent.move()

# Visualization function
def visualize(model):
    plt.clf()
    states = {
        "susceptible": ("blue", [], []),
        "exposed": ("purple", [], []),
        "infected": ("red", [], []),
        "recovered": ("green", [], []),
        "vaccinated": ("grey", [], [])
    }

    for agent in model.agents:
        x, y = agent.pos
        color, xs, ys = states[agent.state]
        xs.append(x)
        ys.append(y)

    for label, (color, xs, ys) in states.items():
        plt.scatter(xs, ys, label=label.capitalize(), color=color, s=30)

    plt.xlim(-1, model.grid.width)
    plt.ylim(-1, model.grid.height)
    plt.title("Agent-Based Model")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

# Animate and save
model = Model(width=20, height=20, num_agents=400, vaccination_rate=0)
fig = plt.figure(figsize=(8, 8))

def update(frame):
    model.step()
    visualize(model)

anim = FuncAnimation(fig, update, frames=100, repeat=False)

# Uncomment one of the two lines below:
# Option A: Save as GIF
anim.save("simulation_400_0.gif", writer=PillowWriter(fps=2))

# Option B: Save as MP4 (requires ffmpeg) --> did not work...
#anim.save("simulation.mp4", writer='ffmpeg', fps=5)
