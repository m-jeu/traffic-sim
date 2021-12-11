import mesa
import mesa.time
import mesa.space


class World(mesa.Model):
    """A world, in which vehicles move.

    Whether this is a lane, or a road, is yet to be determined."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize class instance."""

        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa.space.SingleGrid(width, height, torus=True)
