"""
Convective Risk Analysis Engine
Core thermodynamic calculations for severe weather assessment
"""

import numpy as np
import metpy.calc as mpcalc
from metpy.units import units
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SoundingData:
    """Container for atmospheric sounding data"""
    pressure: np.ndarray  # hPa
    temperature: np.ndarray  # degC
    dewpoint: np.ndarray  # degC
    height: Optional[np.ndarray] = None  # meters
    wind_direction: Optional[np.ndarray] = None  # degrees
    wind_speed: Optional[np.ndarray] = None  # knots
    
    def __post_init__(self):
        """Validate data consistency"""
        base_length = len(self.pressure)
        if len(self.temperature) != base_length or len(self.dewpoint) != base_length:
            raise ValueError("Pressure, temperature, and dewpoint must have same length")


@dataclass
class ConvectiveIndices:
    """Results from convective analysis"""
    cape: float  # J/kg
    cin: float  # J/kg
    lcl_pressure: float  # hPa
    lcl_temperature: float  # degC
    lfc_pressure: Optional[float]  # hPa
    lfc_temperature: Optional[float]  # degC
    el_pressure: Optional[float]  # hPa
    el_temperature: Optional[float]  # degC
    surface_temperature: float  # degC
    surface_dewpoint: float  # degC
    parcel_profile: np.ndarray  # degC
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'cape': round(self.cape, 1),
            'cin': round(self.cin, 1),
            'lcl_pressure': round(self.lcl_pressure, 1),
            'lcl_temperature': round(self.lcl_temperature, 1),
            'lfc_pressure': round(self.lfc_pressure, 1) if self.lfc_pressure else None,
            'lfc_temperature': round(self.lfc_temperature, 1) if self.lfc_temperature else None,
            'el_pressure': round(self.el_pressure, 1) if self.el_pressure else None,
            'el_temperature': round(self.el_temperature, 1) if self.el_temperature else None,
            'surface_temperature': round(self.surface_temperature, 1),
            'surface_dewpoint': round(self.surface_dewpoint, 1),
        }


class ConvectiveAnalyzer:
    """Main engine for convective potential analysis"""
    
    def __init__(self, sounding: SoundingData):
        """
        Initialize analyzer with sounding data
        
        Args:
            sounding: SoundingData object with atmospheric profile
        """
        self.sounding = sounding
        self._attach_units()
        
    def _attach_units(self):
        """Attach MetPy units to arrays"""
        self.p = self.sounding.pressure * units.hPa
        self.T = self.sounding.temperature * units.degC
        self.Td = self.sounding.dewpoint * units.degC
        
    def calculate_indices(self) -> ConvectiveIndices:
        """
        Calculate all convective indices
        
        Returns:
            ConvectiveIndices object with all calculated values
        """
        # Calculate LCL
        lcl_p, lcl_t = mpcalc.lcl(self.p[0], self.T[0], self.Td[0])
        
        # Calculate parcel profile
        parcel_prof = mpcalc.parcel_profile(self.p, self.T[0], self.Td[0])
        
        # Calculate LFC and EL
        lfc_p, lfc_t = mpcalc.lfc(self.p, self.T, self.Td)
        el_p, el_t = mpcalc.el(self.p, self.T, self.Td)
        
        # Calculate CAPE and CIN
        cape, cin = mpcalc.cape_cin(self.p, self.T, self.Td, parcel_prof)
        
        # Check if LFC/EL exist (not nan)
        import numpy as np
        lfc_p_val = lfc_p.magnitude if not np.isnan(lfc_p.magnitude) else None
        lfc_t_val = lfc_t.magnitude if not np.isnan(lfc_t.magnitude) else None
        el_p_val = el_p.magnitude if not np.isnan(el_p.magnitude) else None
        el_t_val = el_t.magnitude if not np.isnan(el_t.magnitude) else None
        
        return ConvectiveIndices(
            cape=cape.magnitude,
            cin=cin.magnitude,
            lcl_pressure=lcl_p.magnitude,
            lcl_temperature=lcl_t.magnitude,
            lfc_pressure=lfc_p_val,
            lfc_temperature=lfc_t_val,
            el_pressure=el_p_val,
            el_temperature=el_t_val,
            surface_temperature=self.T[0].magnitude,
            surface_dewpoint=self.Td[0].magnitude,
            parcel_profile=parcel_prof.to('degC').magnitude
        )
    
    def get_key_levels(self) -> Dict[str, Tuple[float, float]]:
        """
        Get key atmospheric levels for plotting
        
        Returns:
            Dictionary with level names and (pressure, temperature) tuples
        """
        indices = self.calculate_indices()
        
        levels = {
            'lcl': (indices.lcl_pressure, indices.lcl_temperature),
        }
        
        if indices.lfc_pressure:
            levels['lfc'] = (indices.lfc_pressure, indices.lfc_temperature)
            
        if indices.el_pressure:
            levels['el'] = (indices.el_pressure, indices.el_temperature)
            
        return levels


def quick_analysis(pressure: np.ndarray, 
                   temperature: np.ndarray, 
                   dewpoint: np.ndarray) -> ConvectiveIndices:
    """
    Quick analysis from raw arrays
    
    Args:
        pressure: Pressure levels in hPa
        temperature: Temperature in degC
        dewpoint: Dewpoint temperature in degC
        
    Returns:
        ConvectiveIndices with all calculated values
    """
    sounding = SoundingData(
        pressure=pressure,
        temperature=temperature,
        dewpoint=dewpoint
    )
    
    analyzer = ConvectiveAnalyzer(sounding)
    return analyzer.calculate_indices()
