import mesa

import model


class Car(mesa.Agent):
    """Vroom vroom."""

    def __init__(self, m: model.World) -> None:
        super().__init__(m.next_id(), m)
        # Add speed and other attributes here.
