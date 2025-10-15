import numpy as np
from Mathlib import reflectVector
from math import pi, cos

class Light(object):
    def __init__(self, color = [1,1,1], intensity = 1.0, lightType = 'None'):
        self.color = color
        self.intensity = intensity
        self.lightType = lightType

    def GetLightColor(self, intercept = None):
        return [(i * self.intensity) for i in self.color]
    
    def GetSpecularColor(self, intercept, viewPos):
        return [0,0,0]
    
class DirectionalLight(Light):
    def __init__(self, color = [1,1,1], intensity = 1.0, direction = [0,-1,0]):
        super().__init__(color, intensity, 'Directional')
        self.direction = direction / np.linalg.norm(direction)

    def GetLightColor(self, intercept = None):
        lightColor =  super().GetLightColor()

        if intercept:
            dir = [(i * -1) for i in self.direction]
            surfaceIntensity = np.dot(intercept.normal, dir)
            # surfaceIntensity *= 1 - intercept.obj.material.ks
            surfaceIntensity = max(0, min(1, surfaceIntensity))
            lightColor = [(i * surfaceIntensity) for i in lightColor]

        return lightColor
    
    def GetSpecularColor(self, intercept, viewPos):
        specColor = self.color
        if intercept:
            dir = [(i * -1) for i in self.direction]
            reflect = reflectVector(intercept.normal, dir)

            viewDir = np.subtract(viewPos, intercept.point)
            viewDir /= np.linalg.norm(viewDir)

            specIntensity = max(0, np.dot(viewDir, reflect)) ** intercept.obj.material.spec
            specIntensity *= intercept.obj.material.ks
            specIntensity *= self.intensity 
            specColor = [(i * specIntensity) for i in specColor] 

        return specColor
    
class AmbientLight(Light):
    def __init__(self, color = [1,1,1], intensity = 0.1):
        super().__init__(color, intensity, 'Ambient')

class PointLight(Light):
    def __init__(self, color=[1,1,1], intensity=1.0, position=[0,0,0]):
        super().__init__(color, intensity, 'Point')
        self.position = np.array(position, dtype=float)
        self.lightType = 'Point'
    
    def GetLightColor(self, intercept=None):
        lightColor = super().GetLightColor()
        if intercept is not None:
            dir_vec = self.position - intercept.point
            R = np.linalg.norm(dir_vec)
            if R == 0:
                return [0,0,0]
            wi = dir_vec / R
            surfaceIntensity = max(0.0, np.dot(intercept.normal, wi))
            surfaceIntensity *= self.intensity / (R*R)
            lightColor = [c * surfaceIntensity for c in self.color]
        return lightColor

    def GetSpecularColor(self, intercept, viewPos):
        if intercept is None:
            return [0,0,0]
        dir_vec = self.position - intercept.point
        R = np.linalg.norm(dir_vec)
        if R == 0:
            return [0,0,0]
        wi = dir_vec / R
        reflect = reflectVector(intercept.normal, wi)
        viewDir = np.array(viewPos, dtype=float) - intercept.point
        viewDir /= np.linalg.norm(viewDir)
        specIntensity = max(0.0, np.dot(viewDir, reflect)) ** intercept.obj.material.spec
        specIntensity *= intercept.obj.material.ks
        specIntensity *= self.intensity / (R*R)
        return [c * specIntensity for c in self.color]


class SpotLight(PointLight):
    def __init__(self, color=[1,1,1], intensity=1.0, position=[0,0,0],
                 direction=[0,-1,0], innerAngle=30, outerAngle=40):
        super().__init__(color, intensity, position)
        d = np.array(direction, dtype=float)
        self.direction = d / np.linalg.norm(d)
        self.innerAngle = float(innerAngle)
        self.outerAngle = float(outerAngle)
        self.lightType = 'Spot'

    def _edge_attenuation(self, intercept):
        if intercept is None:
            return 0.0
        wi = self.position - intercept.point
        wi /= np.linalg.norm(wi)
        innerRad = self.innerAngle * pi / 180.0
        outerRad = self.outerAngle * pi / 180.0
        cosTheta = np.dot(self.direction, -wi)
        denom = (cos(innerRad) - cos(outerRad))
        if abs(denom) < 1e-8:
            return 0.0
        att = (cosTheta - cos(outerRad)) / denom
        return max(0.0, min(1.0, att))

    def GetLightColor(self, intercept=None):
        base = super().GetLightColor(intercept)
        edge = self._edge_attenuation(intercept)
        return [c * edge for c in base]

    def GetSpecularColor(self, intercept, viewPos):
        base = super().GetSpecularColor(intercept, viewPos)
        edge = self._edge_attenuation(intercept)
        return [c * edge for c in base]