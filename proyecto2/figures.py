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

        self.bottom_cap = Disk(self.position, [0, -1, 0], radius, material)
        top_center = self.position + np.array([0, self.height, 0])
        self.top_cap = Disk(top_center, [0, 1, 0], radius, material)

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        oc = orig - self.position

        a = dir[0]**2 + dir[2]**2
        b = 2.0 * (oc[0]*dir[0] + oc[2]*dir[2])
        c = oc[0]**2 + oc[2]**2 - self.radius**2

        EPS = 1e-6
        hits = []

        if abs(a) > EPS:
            disc = b*b - 4*a*c
            if disc >= -EPS:
                disc = max(disc, 0.0)
                sqrt_disc = np.sqrt(disc)
                for t in [(-b - sqrt_disc) / (2*a), (-b + sqrt_disc) / (2*a)]:
                    if t > EPS:
                        y_local = oc[1] + t*dir[1]
                        if 0 <= y_local <= self.height:
                            point = orig + t*dir
                            dx = point[0] - self.position[0]
                            dz = point[2] - self.position[2]
                            normal = np.array([dx, 0, dz], dtype=float)
                            normal /= np.linalg.norm(normal)
                            hits.append((t, point, normal, "lateral"))

        for tag, cap in [("cap_bottom", self.bottom_cap), ("cap_top", self.top_cap)]:
            cap_hit = cap.ray_intersect(orig, dir)
            if cap_hit is not None:
                hits.append((cap_hit.distance, cap_hit.point, cap_hit.normal, tag))

        if not hits:
            return None

        t, point, normal, tag = min(hits, key=lambda h: h[0])

        if tag == "lateral":
            lx = point[0] - self.position[0]
            lz = point[2] - self.position[2]
            theta = -atan2(lz, lx)
            u = (theta / (2 * pi)) + 0.5
            v = (point[1] - self.position[1]) / self.height
        else:
            center = self.position if tag == "cap_bottom" else (self.position + np.array([0, self.height, 0]))
            rvec = point - center
            theta = -atan2(rvec[2], rvec[0])
            rho = (rvec[0]**2 + rvec[2]**2) ** 0.5 / self.radius
            u = (theta / (2 * pi)) + 0.5
            v = np.clip(rho, 0.0, 1.0)

        u = u - np.floor(u)
        v = np.clip(v, 0.0, 1.0)

        return Intercept(
            point=point,
            normal=normal,
            distance=t,
            obj=self,
            rayDirection=dir,
            texCoord=[u, v]
        )

class Ellipsoid(Shape):
    def __init__(self, position, radius, material):
        super().__init__(np.array(position, dtype=float), material)
        self.radius = np.array(radius, dtype=float)
        self.type = "Ellipsoid"

    def ray_intersect(self, orig, dir):
        EPS = 1e-6
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)

        o = (orig - self.position) / self.radius
        d = dir / self.radius

        A = np.dot(d, d)
        B = 2 * np.dot(o, d)
        C = np.dot(o, o) - 1

        disc = B*B - 4*A*C
        if disc < 0:
            return None

        sqrt_disc = np.sqrt(disc)
        t0 = (-B - sqrt_disc) / (2*A)
        t1 = (-B + sqrt_disc) / (2*A)

        t = None
        if t0 > EPS:
            t = t0
        elif t1 > EPS:
            t = t1
        if t is None:
            return None

        point = orig + dir * t

        local = (point - self.position) / (self.radius * self.radius)
        normal = local / np.linalg.norm(local)

        if np.dot(normal, dir) > 0:
            normal = -normal

        return Intercept(
            point=point,
            normal=normal,
            distance=t,
            obj=self,
            rayDirection=dir,
            texCoord=None
        )

class Cone(Shape):
    def __init__(self, position, radius, height, material):
        super().__init__(np.array(position, dtype=float), material)
        self.radius = float(radius)
        self.height = float(height)
        self.type = "Cone"
        self.base = Disk(self.position, [0, -1, 0], radius, material)
        self.apex = self.position + np.array([0.0, self.height, 0.0], dtype=float)
        self.k = self.radius / self.height
        self.k2 = self.k * self.k

    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir  = np.array(dir, dtype=float)
        EPS  = 1e-6
        hits = []

        o = orig - self.apex
        d = dir

        A = d[0]*d[0] + d[2]*d[2] - self.k2 * d[1]*d[1]
        B = 2.0 * (o[0]*d[0] + o[2]*d[2] - self.k2 * o[1]*d[1])
        C = o[0]*o[0] + o[2]*o[2] - self.k2 * o[1]*o[1]

        if abs(A) > EPS:
            disc = B*B - 4.0*A*C
            if disc >= -EPS:
                disc = max(0.0, disc)
                sqrt_disc = np.sqrt(disc)
                for t in [(-B - sqrt_disc) / (2.0*A), (-B + sqrt_disc) / (2.0*A)]:
                    if t > EPS:
                        y_local = o[1] + t * d[1]
                        if -self.height <= y_local <= 0.0:
                            point = orig + t * dir
                            lp = point - self.apex
                            normal = np.array([lp[0], -self.k2 * lp[1], lp[2]], dtype=float)
                            nlen = np.linalg.norm(normal)
                            if nlen > 0:
                                normal /= nlen
                            if np.dot(normal, dir) > 0:
                                normal = -normal
                            hits.append((t, point, normal))

        base_hit = self.base.ray_intersect(orig, dir)
        if base_hit is not None:
            hits.append((base_hit.distance, base_hit.point, base_hit.normal))

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

class Torus(Shape):
    def __init__(self, position, major_radius, minor_radius, material):
        super().__init__(np.array(position, dtype=float), material)
        self.R = float(major_radius)
        self.r = float(minor_radius)
        self.type = "Torus"

    def ray_intersect(self, orig, dir):
        EPS = 1e-6
        o = np.array(orig, dtype=float) - self.position
        d = np.array(dir, dtype=float)

        dx, dy, dz = d
        ox, oy, oz = o

        R2 = self.R * self.R
        r2 = self.r * self.r

        dd = dx*dx + dy*dy + dz*dz
        oo = ox*ox + oy*oy + oz*oz
        od = ox*dx + oy*dy + oz*dz

        k = oo - r2 - R2
        fourR2 = 4.0 * R2

        A = dd*dd
        B = 4.0 * dd * od
        C = 2.0*dd*k + 4.0*od*od + fourR2*(dy*dy)
        D = 4.0*od*k + 2.0*fourR2*(oy*dy)
        E = k*k + fourR2*(oy*oy - r2)

        coeffs = [A, B, C, D, E]
        roots = np.roots(coeffs)

        ts = [t.real for t in roots if abs(t.imag) < 1e-6 and t.real > EPS]
        if not ts:
            return None

        t = min(ts)
        point = orig + t * d
        p = point - self.position
        px, py, pz = p

        sumsq = px*px + py*py + pz*pz
        g = sumsq + R2 - r2
        nx = 4.0*g*px - 8.0*R2*px
        ny = 4.0*g*py
        nz = 4.0*g*pz - 8.0*R2*pz
        normal = np.array([nx, ny, nz], dtype=float)
        nlen = np.linalg.norm(normal)
        if nlen == 0:
            return None
        normal /= nlen
        if np.dot(normal, d) > 0:
            normal = -normal

        return Intercept(
            point=point,
            normal=normal,
            distance=t,
            obj=self,
            rayDirection=dir,
            texCoord=None
        )
