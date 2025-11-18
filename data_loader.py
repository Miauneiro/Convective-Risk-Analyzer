"""
Data Loader Module
Handles multiple atmospheric sounding data formats
"""

import pandas as pd
import numpy as np
from io import StringIO, BytesIO
from typing import Tuple, Optional, Dict
from pathlib import Path
from convective_engine import SoundingData


class SoundingLoader:
    """Load atmospheric sounding data from various formats"""
    
    @staticmethod
    def from_wyoming(file_path: str) -> SoundingData:
        """
        Load data from University of Wyoming format
        
        Args:
            file_path: Path to Wyoming format text file
            
        Returns:
            SoundingData object
        """
        df = pd.read_fwf(
            file_path,
            skiprows=5,
            usecols=[0, 1, 2, 3, 6, 7],
            names=['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed']
        )
        
        # Drop rows with all NaN in critical columns
        df = df.dropna(subset=('temperature', 'dewpoint'), how='all').reset_index(drop=True)
        
        return SoundingData(
            pressure=df['pressure'].values,
            temperature=df['temperature'].values,
            dewpoint=df['dewpoint'].values,
            height=df['height'].values if 'height' in df.columns else None,
            wind_direction=df['direction'].values if 'direction' in df.columns else None,
            wind_speed=df['speed'].values if 'speed' in df.columns else None
        )
    
    @staticmethod
    def from_wyoming_text(text_content: str) -> SoundingData:
        """
        Load data from Wyoming format text content (not file)
        
        Args:
            text_content: Wyoming format text as string
            
        Returns:
            SoundingData object
        """
        lines = text_content.strip().split('\n')
        
        # Skip header lines (usually first 5-7 lines)
        data_start = 0
        for i, line in enumerate(lines):
            if 'PRES' in line or 'hPa' in line:
                data_start = i + 1
                break
        
        if data_start == 0:
            # Try to find where numeric data starts
            for i, line in enumerate(lines):
                if line.strip() and line.strip()[0].isdigit():
                    data_start = i
                    break
        
        data_lines = lines[data_start:]
        
        # Parse data
        df = pd.read_fwf(
            StringIO('\n'.join(data_lines)),
            usecols=[0, 1, 2, 3, 6, 7],
            names=['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed']
        )
        
        df = df.dropna(subset=('temperature', 'dewpoint'), how='all').reset_index(drop=True)
        
        return SoundingData(
            pressure=df['pressure'].values,
            temperature=df['temperature'].values,
            dewpoint=df['dewpoint'].values,
            height=df['height'].values if 'height' in df.columns else None,
            wind_direction=df['direction'].values if 'direction' in df.columns else None,
            wind_speed=df['speed'].values if 'speed' in df.columns else None
        )
    
    @staticmethod
    def from_csv(file_path: str, 
                 pressure_col: str = 'pressure',
                 temp_col: str = 'temperature', 
                 dewpoint_col: str = 'dewpoint',
                 **kwargs) -> SoundingData:
        """
        Load data from CSV file
        
        Args:
            file_path: Path to CSV file
            pressure_col: Name of pressure column (hPa)
            temp_col: Name of temperature column (°C)
            dewpoint_col: Name of dewpoint column (°C)
            **kwargs: Additional arguments passed to pd.read_csv
            
        Returns:
            SoundingData object
        """
        df = pd.read_csv(file_path, **kwargs)
        
        # Check required columns exist
        required = {pressure_col, temp_col, dewpoint_col}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required}. Found: {set(df.columns)}")
        
        # Drop rows with missing critical data
        df = df.dropna(subset=[pressure_col, temp_col, dewpoint_col]).reset_index(drop=True)
        
        # Optional columns
        height = df['height'].values if 'height' in df.columns else None
        direction = df['direction'].values if 'direction' in df.columns else None
        speed = df['speed'].values if 'speed' in df.columns else None
        
        return SoundingData(
            pressure=df[pressure_col].values,
            temperature=df[temp_col].values,
            dewpoint=df[dewpoint_col].values,
            height=height,
            wind_direction=direction,
            wind_speed=speed
        )
    
    @staticmethod
    def from_dataframe(df: pd.DataFrame,
                       pressure_col: str = 'pressure',
                       temp_col: str = 'temperature',
                       dewpoint_col: str = 'dewpoint') -> SoundingData:
        """
        Load data from pandas DataFrame
        
        Args:
            df: DataFrame with sounding data
            pressure_col: Name of pressure column
            temp_col: Name of temperature column
            dewpoint_col: Name of dewpoint column
            
        Returns:
            SoundingData object
        """
        # Check columns exist
        required = {pressure_col, temp_col, dewpoint_col}
        if not required.issubset(df.columns):
            raise ValueError(f"DataFrame must contain columns: {required}")
        
        df = df.dropna(subset=[pressure_col, temp_col, dewpoint_col]).reset_index(drop=True)
        
        height = df['height'].values if 'height' in df.columns else None
        direction = df['direction'].values if 'direction' in df.columns else None
        speed = df['speed'].values if 'speed' in df.columns else None
        
        return SoundingData(
            pressure=df[pressure_col].values,
            temperature=df[temp_col].values,
            dewpoint=df[dewpoint_col].values,
            height=height,
            wind_direction=direction,
            wind_speed=speed
        )
    
    @staticmethod
    def from_arrays(pressure: np.ndarray,
                    temperature: np.ndarray,
                    dewpoint: np.ndarray,
                    **kwargs) -> SoundingData:
        """
        Load data from numpy arrays
        
        Args:
            pressure: Pressure array (hPa)
            temperature: Temperature array (°C)
            dewpoint: Dewpoint array (°C)
            **kwargs: Optional arrays (height, wind_direction, wind_speed)
            
        Returns:
            SoundingData object
        """
        return SoundingData(
            pressure=pressure,
            temperature=temperature,
            dewpoint=dewpoint,
            **kwargs
        )
    
    @staticmethod
    def auto_detect(file_path: str) -> SoundingData:
        """
        Auto-detect file format and load appropriately
        
        Args:
            file_path: Path to data file
            
        Returns:
            SoundingData object
            
        Raises:
            ValueError: If format cannot be determined
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        # Try CSV first
        if suffix in ['.csv', '.txt']:
            try:
                return SoundingLoader.from_csv(file_path)
            except:
                pass
        
        # Try Wyoming format
        try:
            return SoundingLoader.from_wyoming(file_path)
        except:
            pass
        
        # Try Wyoming text format
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return SoundingLoader.from_wyoming_text(content)
        except:
            pass
        
        raise ValueError(f"Could not detect format for file: {file_path}")


class SoundingValidator:
    """Validate sounding data quality"""
    
    @staticmethod
    def validate(sounding: SoundingData) -> Dict[str, any]:
        """
        Validate sounding data and return quality metrics
        
        Args:
            sounding: SoundingData object to validate
            
        Returns:
            Dictionary with validation results and warnings
        """
        warnings = []
        errors = []
        
        # Check minimum data points
        n_points = len(sounding.pressure)
        if n_points < 10:
            errors.append(f"Insufficient data points: {n_points} (minimum 10 required)")
        elif n_points < 20:
            warnings.append(f"Limited data points: {n_points} (20+ recommended)")
        
        # Check pressure range
        p_min, p_max = sounding.pressure.min(), sounding.pressure.max()
        if p_max < 900:
            warnings.append(f"Missing surface data? Max pressure: {p_max:.0f} hPa")
        if p_min > 300:
            warnings.append(f"Limited upper air data? Min pressure: {p_min:.0f} hPa")
        
        # Check for inversions
        temp_diff = np.diff(sounding.temperature)
        n_inversions = np.sum(temp_diff > 0)
        if n_inversions > 0:
            warnings.append(f"Temperature inversion detected ({n_inversions} layers)")
        
        # Check dewpoint depression
        depression = sounding.temperature - sounding.dewpoint
        if np.any(depression < 0):
            errors.append("Invalid data: dewpoint > temperature")
        
        max_depression = depression.max()
        if max_depression > 30:
            warnings.append(f"Very dry layer detected (depression: {max_depression:.1f}°C)")
        
        # Check for supersaturation
        if np.any(depression < 0.1):
            warnings.append("Near-saturated layer present (cloud/fog)")
        
        # Overall quality score
        quality_score = 100
        quality_score -= len(warnings) * 10
        quality_score -= len(errors) * 30
        quality_score = max(0, quality_score)
        
        return {
            'valid': len(errors) == 0,
            'quality_score': quality_score,
            'n_points': n_points,
            'pressure_range': (p_min, p_max),
            'warnings': warnings,
            'errors': errors
        }
    
    @staticmethod
    def print_validation(validation: Dict):
        """Pretty print validation results"""
        print("=== SOUNDING VALIDATION ===")
        print(f"Valid: {'✓' if validation['valid'] else '✗'}")
        print(f"Quality Score: {validation['quality_score']}/100")
        print(f"Data Points: {validation['n_points']}")
        print(f"Pressure Range: {validation['pressure_range'][1]:.0f} - {validation['pressure_range'][0]:.0f} hPa")
        
        if validation['errors']:
            print("\nERRORS:")
            for error in validation['errors']:
                print(f"  ✗ {error}")
        
        if validation['warnings']:
            print("\nWARNINGS:")
            for warning in validation['warnings']:
                print(f"  ! {warning}")


def load_example_sounding(risk_level: str = "high") -> SoundingData:
    """
    Load example sounding data for testing
    
    Args:
        risk_level: "low", "moderate", or "high" risk scenario
    
    Returns:
        SoundingData object with atmospheric profile from Wyoming format files
    """
    # Map risk levels to Wyoming format files
    file_map = {
        "low": "data/low_risk_example.txt",
        "moderate": "data/moderate_risk_example.txt",
        "high": "data/high_risk_example.txt"
    }
    
    filepath = file_map.get(risk_level, "data/moderate_risk_example.txt")
    
    try:
        # Try to load from Wyoming format file
        return SoundingLoader.from_wyoming(filepath)
    except Exception as e:
        # Fallback to synthetic sounding if file not found
        if risk_level == "low":
            # Strong cap, minimal CAPE - safe flying conditions
            pressure = np.array([1013, 1000, 975, 950, 925, 900, 850, 800, 750, 700, 
                                650, 600, 550, 500, 450, 400, 350, 300, 250, 200])
            
            temperature = np.array([10, 9, 7, 5, 3, 1, -2, -5, -8, -11,
                                   -14, -17.5, -21, -25, -29.5, -34.5, -40, -46.5, -54, -62])
            
            dewpoint = np.array([-5, -5.5, -6, -6.5, -7, -8, -10, -12, -14, -16,
                                -18.5, -21.5, -25, -29, -33.5, -38.5, -44, -50.5, -58, -66])
        
        elif risk_level == "moderate":
            # Weak cap, moderate CAPE - typical summer day
            pressure = np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650,
                                600, 550, 500, 450, 400, 350, 300, 250, 200])
            
            temperature = np.array([26, 24, 22, 20, 18, 14, 10, 6, 2, -2,
                                   -6, -10.5, -15, -20, -25.5, -31.5, -38.5, -46.5, -55.5])
            
            dewpoint = np.array([18, 17, 16, 15, 14, 11, 8, 4, 0, -4,
                                -9, -14.5, -20, -26, -32.5, -39.5, -47.5, -56.5, -66.5])
        
        else:  # high risk
            # No cap, high CAPE - severe thunderstorm potential
            pressure = np.array([1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 
                                600, 550, 500, 450, 400, 350, 300, 250, 200])
            
            temperature = np.array([28, 26, 24, 22, 20, 16, 12, 8, 4, 0,
                                   -4, -8, -12, -17, -22, -28, -35, -44, -54])
            
            dewpoint = np.array([22, 20, 18, 16, 14, 10, 6, 2, -2, -6,
                                -10, -14, -18, -23, -28, -34, -41, -50, -60])
    
    return SoundingData(
        pressure=pressure,
        temperature=temperature,
        dewpoint=dewpoint
    )
