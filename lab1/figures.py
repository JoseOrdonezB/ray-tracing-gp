import numpy as np

class Shape(object):
    def __init__(self, position):
        self.position = np.array(position, dtype=float)
        self.type = 'None'

    def ray_intersect(self, orig, dir):
        return False


class Sphere(Shape):
    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = float(radius)
        self.type = 'Sphere'

    def ray_intersect(self, orig, dir):
        L = orig - self.position

        a = np.dot(dir, dir)
        b = 2 * np.dot(dir, L)
        c = np.dot(L, L) - self.radius * self.radius

        disc = b * b - 4 * a * c
        if disc < 0:
            return False

        sqrt_disc = np.sqrt(disc)
        t0 = (-b - sqrt_disc) / (2 * a)
        t1 = (-b + sqrt_disc) / (2 * a)

        if t0 > t1:
            t0, t1 = t1, t0

        if t0 < 0:
            t0 = t1
            if t0 < 0:
                return False

        return True