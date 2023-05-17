
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

    def _calculate_center(self):
        self.center = Vec2.between(self.top_left, self.bottom_right)
    
    def move(self, new_position: tuple[Vec2]) -> None:
        """
        Moves the marker to a new position determined by it's four corners provided in the
        tl, tr, bl, br order.
        """
        self.top_left = new_position[0]
        self.top_right = new_position[1]
        self.bottom_left = new_position[2]
        self.bottom_right = new_position[3]
        self._calculate_center()
    
    def maybe_move(self, new_position: tuple[Vec2]) -> bool:
        return False
        # match corners

        # create a temporary list of references to the old corners
        old_corners = [
            self.top_left,
            self.top_right,
            self.bottom_left,
            self.bottom_right
        ]


        for corner in new_position:
            # find a corner that was previously close enough to this new corner and assign them
            for index, old_corner in enumerate(old_corners):
                if old_corner.distance_to(corner) < self._unrelated_distance:
                    old_corner.assign(corner)
                    old_corners.pop(index)
                    break
        
        # if all the old corners were assigned a new one, the marker was matched successfully
        if not len(old_corners):
            self._calculate_center()
            print("Distance matched")
            return True
            
        return False
