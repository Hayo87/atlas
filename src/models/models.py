from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class MovementMode(Enum):
    ROAD = "road"
    AIR = "air"
    OFFROAD = "offroad"

@dataclass
class Location:
    lat: float
    lon: float

# Used to define movement matrix
@dataclass
class VehicleProfile:
    name: str
    movement_mode: MovementMode
    max_range: int

    # physical constraints
    weight_t: float
    height_m: float
    width_m: float
    length_m: float

# Used to define assignment constraints
@dataclass
class VehicleState:
    range_left: int
    payload_left: int
    status: str = "active"

# routing agent 
@dataclass
class Vehicle:
    id: str
    profile: VehicleProfile
    location: Location
    state: VehicleState

    start_index: int | None = None
    end_index: int | None = None

# Tasks to be assigned 
@dataclass
class Job:
    id: str
    location: Location

    demand: int = 0
    allowed_types: Optional[List[str]] = None

    priority: int = 1
    service_time: int = 0