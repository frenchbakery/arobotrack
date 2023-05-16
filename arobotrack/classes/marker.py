
from ..utilities import Vec2

class Marker:
    _unrelated_distance: int = 10
    center: Vec2
    last_center: Vec2

    def __init__(self, id) -> None:
        self.center = Vec2(0, 0)
        self.last_center = Vec2(0, 0)
        self.id = id
    
    def move(self, new_center: Vec2) -> None:
        self.last_center, self.center = self.center, new_center
    
    def maybe_move(self, other_position: Vec2) -> bool:
        dist = self.center.distance_to(other_position)
        if dist < self._unrelated_distance:
            print("Distance matched", dist)
            self.move(other_position)
            return True
        return False
