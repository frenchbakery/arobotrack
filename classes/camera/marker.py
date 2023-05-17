
from ..utilities import Vec2

class Marker:
    _unrelated_distance: int = 10

    center = Vec2(0, 0)
    last_center = Vec2(0, 0)
    
    top_left = Vec2(0, 0)
    top_right = Vec2(0, 0)
    bottom_left = Vec2(0, 0)
    bottom_right = Vec2(0, 0)

    def __init__(self, id) -> None:
        self.id = id

    def set_frame(self, tl, tr, bl, br):
        self.top_left = tl
        self.top_right = tr
        self.bottom_left = bl
        self.bottom_right = br
    
    def move(self, new_center: Vec2) -> None:
        self.last_center, self.center = self.center, new_center
    
    def maybe_move(self, other_position: Vec2) -> bool:
        #return False
        dist = self.center.distance_to(other_position)
        if dist < self._unrelated_distance:
            print("Distance matched", dist)
            self.move(other_position)
            return True
        return False
