"""Data classes for TwistExtrude configuration."""

from dataclasses import dataclass


@dataclass
class TwistConfig:
    total_height: float = 100.0
    total_angle: float = 360.0
    twist_easing: str = "Linear"
    num_sections: int = 24
    equation_str: str = "1.0"
    sketches_only: bool = False
