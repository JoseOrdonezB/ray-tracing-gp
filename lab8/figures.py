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
    def __init__(self, center, size, material):
        super().__init__(np.array(center, dtype=float), material)

        half = np.array(size, dtype=float) / 2.0
        self.min_bound = self.position - half
        self.max_bound = self.position + half
        self.type = 'AABB'

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)

        invdir = 1.0 / dir
        sign = [invdir[i] < 0 for i in range(3)]

        tmin = (self.max_bound[0] if sign[0] else self.min_bound[0] - orig[0]) * invdir[0]
        tmax = (self.min_bound[0] if sign[0] else self.max_bound[0] - orig[0]) * invdir[0]

        tymin = (self.max_bound[1] if sign[1] else self.min_bound[1] - orig[1]) * invdir[1]
        tymax = (self.min_bound[1] if sign[1] else self.max_bound[1] - orig[1]) * invdir[1]

        if (tmin > tymax) or (tymin > tmax):
            return None

        if tymin > tmin:
            tmin = tymin
        if tymax < tmax:
            tmax = tymax

        tzmin = (self.max_bound[2] if sign[2] else self.min_bound[2] - orig[2]) * invdir[2]
        tzmax = (self.min_bound[2] if sign[2] else self.max_bound[2] - orig[2]) * invdir[2]

        if (tmin > tzmax) or (tzmin > tmax):
            return None

        if tzmin > tmin:
            tmin = tzmin
        if tzmax < tmax:
            tmax = tzmax

        if tmin < 0 and tmax < 0:
            return None

        distance = tmin if tmin > 0 else tmax
        point = orig + distance * dir

        epsilon = 1e-6
        normal = [0, 0, 0]
        for i in range(3):
            if abs(point[i] - self.min_bound[i]) < epsilon:
                normal[i] = -1
            elif abs(point[i] - self.max_bound[i]) < epsilon:
                normal[i] = 1
        normal = np.array(normal, dtype=float)

        return Intercept(
            point=point,
            normal=normal,
            distance=distance,
            obj=self,
            rayDirection=dir,
            texCoord=None
        )

class Triangle(Shape):
    def __init__(self, v0, v1, v2, material):
        super().__init__(v0, material)
        self.v0 = np.array(v0, dtype=float)
        self.v1 = np.array(v1, dtype=float)
        self.v2 = np.array(v2, dtype=float)
        self.type = 'Triangle'

        e1 = self.v1 - self.v0
        e2 = self.v2 - self.v0
        self.normal = np.cross(e1, e2)
        self.normal /= np.linalg.norm(self.normal)

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)

        EPSILON = 1e-6
        e1 = self.v1 - self.v0
        e2 = self.v2 - self.v0
        h = np.cross(dir, e2)
        a = np.dot(e1, h)

        if abs(a) < EPSILON:
            return None

        f = 1.0 / a
        s = orig - self.v0
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            return None

        q = np.cross(s, e1)
        v = f * np.dot(dir, q)
        if v < 0.0 or (u + v) > 1.0:
            return None

        t = f * np.dot(e2, q)
        if t > EPSILON:
            point = orig + dir * t
            return Intercept(
                point=point,
                normal=self.normal,
                distance=t,
                obj=self,
                rayDirection=dir,
                texCoord=None
            )
        return None
    
class Cylinder(Shape):
    def __init__(self, position, radius, height, material):
        super().__init__(np.array(position, dtype=float), material)
        self.radius = float(radius)
        self.height = float(height)
        self.type = "Cylinder"

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)

        oc = orig - self.position

        a = dir[0]**2 + dir[2]**2
        b = 2.0 * (oc[0]*dir[0] + oc[2]*dir[2])
        c = oc[0]**2 + oc[2]**2 - self.radius**2

        EPS = 1e-6
        hits = []

        # Cuerpo del cilindro
        if abs(a) > EPS:
            disc = b*b - 4*a*c
            if disc >= 0:
                sqrt_disc = np.sqrt(disc)
                for t in [(-b - sqrt_disc)/(2*a), (-b + sqrt_disc)/(2*a)]:
                    if t > EPS:
                        y = oc[1] + t*dir[1]
                        if 0 <= y <= self.height:
                            point = orig + t*dir
                            normal = np.array([point[0]-self.position[0], 0, point[2]-self.position[2]])
                            normal /= np.linalg.norm(normal)
                            hits.append((t, point, normal))

        # Tapas del cilindro
        for cap_y, n in [(0, np.array([0,-1,0])), (self.height, np.array([0,1,0]))]:
            if abs(dir[1]) > EPS:
                t = (cap_y - oc[1]) / dir[1]
                if t > EPS:
                    p = orig + t*dir
                    d = p - self.position
                    if d[0]**2 + d[2]**2 <= self.radius**2:
                        point = p
                        normal = n
                        hits.append((t, point, normal))

        if not hits:
            return None

        t, point, normal = min(hits, key=lambda h: h[0])
        return Intercept(
            point=point,
            normal=normal,
            distance=t,
            obj=self,
            rayDirection=dir,
            texCoord=None
        )
