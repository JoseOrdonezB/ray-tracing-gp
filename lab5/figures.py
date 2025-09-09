import numpy as np
from intercept import Intercept

class Shape(object):
    def __init__(self, position, material):
        self.position = position
        self.material = material
        self.type = 'None'

    def ray_intersect(self, orig, dir):
        return None


class Sphere(Shape):
    def __init__(self, position, radius, material):
        super().__init__(position, material)
        self.radius = radius
        self.type = 'Sphere'

    def ray_intersect(self, orig, dir):
        orig = np.asarray(orig, dtype=np.float64)
        dir  = np.asarray(dir,  dtype=np.float64)
        pos  = np.asarray(self.position, dtype=np.float64)

        dir_len2 = float(np.dot(dir, dir))
        if dir_len2 == 0.0:
            return None

        L = orig - pos

        a = dir_len2
        b = 2.0 * float(np.dot(dir, L))
        c = float(np.dot(L, L)) - self.radius * self.radius

        disc = b * b - 4.0 * a * c
        if disc < 0.0:
            return None

        sqrt_disc = float(np.sqrt(disc))

        if b >= 0.0:
            q = -0.5 * (b + sqrt_disc)
        else:
            q = -0.5 * (b - sqrt_disc)

        if q == 0.0:
            t0 = (-b - sqrt_disc) / (2.0 * a)
            t1 = (-b + sqrt_disc) / (2.0 * a)
        else:
            t0 = q / a
            t1 = c / q

        if t0 > t1:
            t0, t1 = t1, t0

        epsilon = 1e-5
        t = t0 if t0 >= epsilon else (t1 if t1 >= epsilon else None)
        if t is None:
            return None

        point = orig + dir * t
        normal = (point - pos) / self.radius
        nl = np.linalg.norm(normal)
        if nl != 0.0:
            normal = normal / nl

        if float(np.dot(normal, dir)) > 0.0:
            normal = -normal

        distance = float(t * np.sqrt(dir_len2))

        return Intercept(
            point=point,
            normal=normal,
            distance=distance,
            obj=self,
            rayDirection=dir
        )