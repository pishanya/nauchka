import numpy as np


class Glucose:
    def __init__(self, t_min=0, t_max=100, num_points=1000, fraction=0.35):
        self.t_min = t_min
        self.t_max = t_max
        self.num_points = num_points
        self.t = np.linspace(t_min, t_max, num_points)
        self.values = self.glucose_func(self.t)
        self.G_min = np.round(np.min(self.values), 1)
        self.G_max = np.round(np.max(self.values), 1)

        self.G_middle = np.round((self.G_min + self.G_max) / 2.0, 1)
        self.G_range = self.G_max - self.G_min
        self.G_min_bound = np.round(self.G_min + fraction * self.G_range, 1)
        self.G_max_bound = np.round(self.G_min + (1 - fraction) * self.G_range, 1)

    def glucose_func(self, t):
        return np.sin(t/2)
    
    def modify_G(self, G: float) -> int:
        if G < self.G_min_bound:
            return self.G_min  # LOW
        if G < self.G_max_bound:
            return self.G_middle  # NORMAL
        return self.G_max  # HIGH
    

glucose = Glucose(t_min=0, t_max=100, num_points=1000)