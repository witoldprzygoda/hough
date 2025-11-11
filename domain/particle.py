"""
Particle domain models and charge registry.

Implements the Registry pattern for particle charge lookup.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class Particle:
    """
    Immutable value object representing a particle.

    Attributes:
        pdg_id: PDG particle identification code
        charge: Electric charge in units of e
        pt: Transverse momentum
        eta: Pseudorapidity
        phi: Azimuthal angle
        pz: Longitudinal momentum
        vz: Vertex z-position
    """
    pdg_id: int
    charge: float
    pt: float
    eta: float
    phi: float
    pz: float
    vz: float

    @property
    def pz_over_pt(self) -> float:
        """Calculate pz/pt ratio."""
        return self.pz / self.pt if self.pt != 0 else 0.0

    @property
    def cotangent(self) -> float:
        """Calculate cotangent of theta (cot(theta) = pz/pt)."""
        return self.pz_over_pt

    def is_charged(self) -> bool:
        """Check if particle is charged."""
        return self.charge != 0


class ParticleChargeRegistry:
    """
    Registry for PDG particle ID to charge mappings.

    Implements Singleton pattern to ensure one global registry.
    """

    _instance: Optional['ParticleChargeRegistry'] = None

    # Extended particle charge dictionary
    _CHARGE_MAP: Dict[int, float] = {
        # Gauge bosons
        22: 0, 23: 0, 24: 1, -24: -1, 21: 0,

        # Leptons
        11: -1, -11: 1, 12: 0, -12: 0,
        13: -1, -13: 1, 14: 0, -14: 0,
        15: -1, -15: 1, 16: 0, -16: 0,

        # Quarks
        1: -1/3, -1: 1/3, 2: 2/3, -2: -2/3,
        3: -1/3, -3: 1/3, 4: 2/3, -4: -2/3,
        5: -1/3, -5: 1/3, 6: 2/3, -6: -2/3,

        # Light mesons
        111: 0, 211: 1, -211: -1, 113: 0, 213: 1, -213: -1,
        221: 0, 331: 0, 130: 0, 310: 0, 311: 0, -311: 0,
        321: 1, -321: -1,

        # Charmed mesons
        411: 1, -411: -1, 421: 0, -421: 0,

        # Bottom mesons
        511: 0, -511: 0, 521: 1, -521: -1,

        # Baryons
        2212: 1, -2212: -1, 2112: 0, -2112: 0,
        3122: 0, -3122: 0, 3222: 1, -3222: -1,
        3212: 0, -3212: 0, 3112: -1, -3112: 1,
        3312: -1, -3312: 1, 3322: 0, -3322: 0,
    }

    def __new__(cls) -> 'ParticleChargeRegistry':
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_charge(self, pdg_id: int) -> Optional[float]:
        """
        Get electric charge for a given PDG ID.

        Args:
            pdg_id: PDG particle identification code

        Returns:
            Electric charge in units of e, or None if unknown
        """
        if pdg_id in self._CHARGE_MAP:
            return self._CHARGE_MAP[pdg_id]

        # Handle antiparticles automatically
        if pdg_id < 0 and -pdg_id in self._CHARGE_MAP:
            return -self._CHARGE_MAP[-pdg_id]

        return None

    def get_charge_safe(self, pdg_id: int, default: float = 0.0) -> float:
        """
        Get charge with default fallback.

        Args:
            pdg_id: PDG particle identification code
            default: Default value if charge is unknown

        Returns:
            Electric charge or default value
        """
        charge = self.get_charge(pdg_id)
        return charge if charge is not None else default

    def register_particle(self, pdg_id: int, charge: float) -> None:
        """
        Register a new particle type.

        Args:
            pdg_id: PDG particle identification code
            charge: Electric charge in units of e
        """
        self._CHARGE_MAP[pdg_id] = charge
