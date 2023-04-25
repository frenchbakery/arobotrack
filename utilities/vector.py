"""
ELEKTRON (c) 2022
Written by melektron (Matteo Reiter)
www.elektron.work
02.05.22 20:20

A class that represents a 2D vector for the simulation

Inspiration:
https://scipython.com/book2/chapter-4-the-core-python-language-ii/examples/a-2d-vector-class/
"""


import math

class Vec2:
    # cartesian values
    _valx: float = 0
    _valy: float = 0

    def __init__(self, x: float, y: float):
        self._valx, self._valy = x, y

    @classmethod
    def from_cart(cls, values: tuple | list) -> "Vec2":
        return cls(values[0], values[1])
    
    @classmethod
    def from_polar(cls, values: tuple | list) -> "Vec2":
        new = cls(1, 1)
        new.phi = values[0]
        new.r = values[1]
        return new

    @classmethod
    def between(cls, first: "Vec2", second: "Vec2"):
        return cls(
            (first._valx + second._valx) / 2,
            (first._valy + second._valy) / 2
        )
    
    def copy(self) -> "Vec2":
        return Vec2(self._valx, self._valy)

    # properties for cartesian values
    @property
    def x(self) -> float:
        return self._valx
    
    @x.setter
    def x(self, value):
        self._valx = value

    @property
    def y(self) -> float:
        return self._valy
    
    @y.setter
    def y(self, value):
        self._valy = value
    
    @property
    def cart(self) -> tuple[float, float]:
        return (self._valx, self._valy)
    
    @cart.setter
    def cart(self, value: tuple[float, float]):
        self._valx = value[0]
        self._valy = value[1]

    @property
    def icart(self) -> tuple[int, int]:
        return (int(self._valx), int(self._valy))
    
    @cart.setter
    def cart(self, value: tuple[int, int]):
        self._valx = float(value[0])
        self._valy = float(value[1])

    # properties for polar values
    @property
    def r(self) -> float:
        return math.sqrt(pow(self._valx, 2) + pow(self._valy, 2))
    
    @r.setter
    def r(self, value):
        keepphi = self.phi
        self._valx = math.cos(keepphi) * value
        self._valy = math.sin(keepphi) * value
    
    @property
    def phi(self) -> float:
        return math.atan2(self._valy, self._valx)
    
    @phi.setter
    def phi(self, value):
        keepr = self.r
        self._valx = math.cos(value) * keepr
        self._valy = math.sin(value) * keepr


    # operators
    
    def __str__(self):
        # Human-readable string representation of the vector
        return '({:g};{:g})'.format(self._valx, self._valy)

    def __repr__(self):
        # Unambiguous string representation of the vector
        return repr((self._valx, self._valy))

    def dot(self, other):
        # The scalar (dot) product of self and other. Both must be vectors
        if not isinstance(other, Vec2):
            raise TypeError("Can only dot-multiply Vec2 by Vec2")
        return self._valx * other._valx + self._valy * other._valy
    
    # Alias the __matmul__ method to enable matrix multiplication with "a @ b" syntax
    __matmul__ = dot

    def __sub__(self, other: "Vec2"):
        # Vector subtraction
        return Vec2(self._valx - other._valx, self._valy - other._valy)

    def __add__(self, other: "Vec2"):
        # Vector addition
        return Vec2(self._valx + other._valx, self._valy + other._valy)

    def __mul__(self, scalar):
        # Multiplication of a vector by a scalar (single factor)

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vec2(self._valx*scalar, self._valy*scalar)
        raise NotImplementedError('Can only multiply Vec2 by a number')

    def __rmul__(self, scalar):
        # Reflected multiplication so scalar * vector also works
        return self.__mul__(scalar)
    
    def __pow__(self, power):
        # power operator (**)

        if isinstance(power, int) or isinstance(power, float):
            return Vec2(self._valx**power, self._valy**power)

    def __iadd__(self, other: "Vec2"):
        self._valx += other._valx
        self._valy += other._valy
        return self
    
    def __isub__(self, other: "Vec2"):
        self._valx -= other._valx
        self._valy -= other._valy
        return self

    def __neg__(self):
        # Negation of the vector (invert through origin)
        return Vec2(-self._valx, -self._valy)

    def __truediv__(self, scalar):
        # True division of the vector by a scalar
        return Vec2(self._valx / scalar, self._valy / scalar)

    def __mod__(self, scalar):
        # One way to implement modulus operation: for each component
        return Vec2(self.x % scalar, self.y % scalar)

    def __abs__(self):
        #Absolute value (magnitude, length) of the vector
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, other) -> float:
        # absolute distance between vectors self and other
        return abs(self - other)