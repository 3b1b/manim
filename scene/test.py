import numpy as np
import random

class CowProblem():
    def __init__(self):
        self.reset()
        self.directions = [
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
        ]

    def reset(self):
        self.field = np.ones((11, 11), dtype = 'bool')
        self.cow_x = 0
        self.cow_y = 0

    def step(self):
        valid_step = False
        while not valid_step:
            step_x, step_y = random.choice(self.directions)
            if self.cow_x + step_x > 0 and self.cow_x + step_x < 11 and self.cow_y + step_y > 0 and self.cow_y + step_y < 11:
                valid_step = True
        self.cow_x += step_x
        self.cow_y += step_y
        self.field[self.cow_x, self.cow_y] = False

    def total_grass_after_n_steps(self, n):
        for x in range(n):
            self.step()
        return sum(sum(self.field))

    def num_steps_for_half_eaten(self):
        result = 0
        while sum(sum(self.field)) > 121/2:
            self.step()
            result += 1
        return result

    def average_number_of_steps_for_half_eaten(self, sample_size):
        run_times = []
        for x in range(sample_size):
            run_times.append(
                self.num_steps_for_half_eaten()
            )
            self.reset()
        return np.mean(run_times)






