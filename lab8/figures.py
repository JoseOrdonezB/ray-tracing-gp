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
                            hits.append((t, point, normal))

        for cap in [self.bottom_cap, self.top_cap]:
            cap_hit = cap.ray_intersect(orig, dir)
            if cap_hit is not None:
                hits.append((cap_hit.distance, cap_hit.point, cap_hit.normal))

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

class Toroid(Shape):
    """
    Toroide centrado en `position`, orientado alrededor del eje Y.
    - major_radius (R): radio mayor (del centro del toro al centro del tubo)
    - minor_radius (r): radio menor (radio del tubo)

    Ecuación implícita (con el centro en el origen y eje Y):
      F(x,y,z) = (x^2 + y^2 + z^2 + R^2 - r^2)^2 - 4 R^2 (x^2 + z^2) = 0

    Intersección rayo (o + t d):
      Se obtiene un polinomio de grado 4 en t. Se resuelve con numpy.roots
      y se elige la raíz real positiva más cercana.

    Normal:
      ∇F = ( ∂F/∂x, ∂F/∂y, ∂F/∂z )
      con:
        g = x^2 + y^2 + z^2 + R^2 - r^2
        ∂F/∂x = 4 x (g - 2 R^2)
        ∂F/∂y = 4 y g
        ∂F/∂z = 4 z (g - 2 R^2)
    """
    def __init__(self, position, major_radius, minor_radius, material):
        super().__init__(np.array(position, dtype=float), material)
        self.R = float(major_radius)
        self.r = float(minor_radius)
        self.type = "Toroid"

    def ray_intersect(self, orig, dir):
        EPS = 1e-6

        # Pasar a coords locales del toro (centro en el origen)
        o = np.array(orig, dtype=float) - self.position
        d = np.array(dir, dtype=float)

        # Coeficientes auxiliares
        dx, dy, dz = d
        ox, oy, oz = o

        # P(t) = x^2 + y^2 + z^2 = (d·d) t^2 + 2(o·d) t + (o·o)
        A = np.dot(d, d)                   # d·d
        B = 2.0 * np.dot(o, d)             # 2 o·d
        C = np.dot(o, o) + self.R**2 - self.r**2

        # S(t) = x^2 + z^2
        D = dx*dx + dz*dz
        E = 2.0 * (ox*dx + oz*dz)
        F = ox*ox + oz*oz

        # Polinomio cuártico: (A t^2 + B t + C)^2 - 4 R^2 S(t) = 0
        a4 = A*A
        a3 = 2.0*A*B
        a2 = B*B + 2.0*A*C - 4.0*self.R*self.R*D
        a1 = 2.0*B*C - 8.0*self.R*self.R*(ox*dx + oz*dz)
        a0 = C*C - 4.0*self.R*self.R*F

        # Resolver raíces (t puede ser complejo). Filtrar reales y positivas.
        coeffs = np.array([a4, a3, a2, a1, a0], dtype=float)

        # Si el término líder es ~0 por alguna razón numérica, no intentamos intersección.
        if abs(coeffs[0]) < EPS:
            return None

        roots = np.roots(coeffs)
        # Nos quedamos con raíces reales (parte imaginaria ~ 0) y t > 0
        real_ts = []
        for r in roots:
            if abs(r.imag) < 1e-6:
                t = r.real
                if t > EPS:
                    real_ts.append(t)

        if not real_ts:
            return None

        t = min(real_ts)  # intersección más cercana

        # Punto de impacto en coords globales
        point = np.add(orig, np.multiply(dir, t))

        # Normal por el gradiente de F, evaluado en coords locales
        p_local = o + d * t
        x, y, z = p_local
        g = x*x + y*y + z*z + self.R*self.R - self.r*self.r

        nx = 4.0 * x * (g - 2.0*self.R*self.R)
        ny = 4.0 * y * g
        nz = 4.0 * z * (g - 2.0*self.R*self.R)

        normal = np.array([nx, ny, nz], dtype=float)
        nlen = np.linalg.norm(normal)
        if nlen < EPS:
            # Fallback muy raro (evita división por cero)
            # Usamos una aproximación: proyectar al anillo y salir radialmente
            rho = np.hypot(x, z) + EPS
            # vector desde el "centro del tubo" hacia el punto
            cx = x * (1.0 - self.R / rho)
            cz = z * (1.0 - self.R / rho)
            normal = np.array([cx, y, cz], dtype=float)
            nlen = np.linalg.norm(normal)
            if nlen < EPS:
                return None

        normal /= nlen

        return Intercept(
            point=point,
            normal=normal,
            distance=t,
            obj=self,
            rayDirection=dir,
            texCoord=None
        )
