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
    
class Plane(Shape):
    def __init__(self, position, normal, material):
        super().__init__(position, material)
        self.normal = np.array(normal, dtype=float)
        self.normal /= np.linalg.norm(self.normal)
        self.type = 'Plane'

    def ray_intersect(self, orig, dir):
        denom = np.dot(self.normal, dir)

        if abs(denom) < 1e-6:
            return None

        t = np.dot(np.subtract(self.position, orig), self.normal) / denom
        if t < 0:
            return None

        point = np.add(orig, np.multiply(dir, t))

        return Intercept(
            point=point,
            normal=self.normal,
            distance=t,
            obj=self,
            rayDirection=dir,
            texCoord=None
        )

    
class Disk(Plane):
    def __init__(self, position, normal, radius, material):
        super().__init__(position, normal, material)
        self.radius = radius
        self.type = 'Disk'

    def ray_intersect(self, orig, dir):
        plane_hit = super().ray_intersect(orig, dir)
        if plane_hit is None:
            return None

        v = np.subtract(plane_hit.point, self.position)

        if np.dot(v, v) <= self.radius * self.radius:
            return Intercept(
                point=plane_hit.point,
                normal=plane_hit.normal,
                distance=plane_hit.distance,
                obj=self,
                rayDirection=dir,
                texCoord=None
            )
        return None
        
    
class AABB(Shape):
    def __init__():
        return
    
class Triangle(Shape):
    def __init__():
        return