"""Deterministic clinker chemistry calculations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Moduli:
    """Raw-meal chemistry ratios."""

    lsf: float
    sm: float
    am: float


def calculate_moduli(cao: float, sio2: float, al2o3: float, fe2o3: float) -> Moduli:
    """Return lime saturation, silica, and alumina moduli for valid oxide inputs."""
    lsf_denominator = 2.8 * sio2 + 1.18 * al2o3 + 0.65 * fe2o3
    sm_denominator = al2o3 + fe2o3
    if lsf_denominator <= 0 or sm_denominator <= 0 or fe2o3 <= 0:
        raise ValueError("oxide inputs must produce positive moduli denominators")
    return Moduli(
        lsf=cao / lsf_denominator * 100,
        sm=sio2 / sm_denominator,
        am=al2o3 / fe2o3,
    )
