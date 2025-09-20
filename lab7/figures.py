import numpy as np
from intercept import Intercept
from math import acos, atan2, pi

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

        L = np.subtract(self.position, orig)
        tca = np.dot(L, dir)
        d = (np.linalg.norm(L) ** 2 - tca ** 2) ** 0.5

        if d > self.radius:
            return None
        
        thc = (self.radius ** 2 - d ** 2) ** 0.5

        distance = tca - thc
        t1 = tca + thc

        if distance < 0:
            distance = t1
        if distance < 0:
            return None
        
        point = np.add(orig, np.multiply(dir, distance))

        normal = np.subtract(point, self.position)
        normal /= np.linalg.norm(normal)

        u = -atan2(normal[2], normal[0])/(2 * pi) + 0.5
        v = acos(-normal[1])/pi

        return Intercept(
            point=point,
            normal=normal,
            distance=distance,
            obj=self,
            rayDirection=dir,
            texCoord = [u,v]
        )