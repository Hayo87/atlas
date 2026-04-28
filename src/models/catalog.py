from src.models.models import VehicleProfile
from src.models.models import MovementMode

JEEP = VehicleProfile(
    name="jeep",
    movement_mode=MovementMode.ROAD,
    max_range=300_000,
    weight_t=3.5,
    height_m=2.2,
    width_m=2.0,
    length_m=5.0,
)

TRUCK = VehicleProfile(
    name="truck",
    movement_mode=MovementMode.ROAD,
    max_range=200_000,
    weight_t=18.0,
    height_m=3.5,
    width_m=2.8,
    length_m=9.0,
)

DRONE = VehicleProfile(
    name="drone",
    movement_mode=MovementMode.AIR,
    max_range=50_000,
    weight_t=0.02,
    height_m=0.2,
    width_m=0.5,
    length_m=0.5,
)