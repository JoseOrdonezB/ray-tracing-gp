class Intercept(object):
    def __init__(self, point, normal, distance, obj, rayDirection):
        self.point = point
        self.normal = normal
        self.distance = distance
        self.rayDirection = rayDirection
        self.obj = obj