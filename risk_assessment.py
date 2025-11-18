"""
Risk Assessment Module
Translates convective indices into operational risk levels for different stakeholders
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
from convective_engine import ConvectiveIndices


class RiskLevel(Enum):
    """Risk classification levels"""
    EXTREME = "EXTREME"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    MINIMAL = "MINIMAL"
    
    @property
    def color(self) -> str:
        """Get color code for visualization"""
        colors = {
            'EXTREME': '#8B0000',  # Dark red
            'HIGH': '#FF0000',      # Red
            'MODERATE': '#FFA500',  # Orange
            'LOW': '#FFFF00',       # Yellow
            'MINIMAL': '#00FF00'    # Green
        }
        return colors[self.value]
    
    @property
    def score(self) -> int:
        """Numerical score for comparisons"""
        scores = {
            'EXTREME': 5,
            'HIGH': 4,
            'MODERATE': 3,
            'LOW': 2,
            'MINIMAL': 1
        }
        return scores[self.value]


@dataclass
class StakeholderRisk:
    """Risk assessment for a specific stakeholder"""
    activity: str
    risk_level: RiskLevel
    go_no_go: bool
    reasoning: str
    precautions: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'activity': self.activity,
            'risk_level': self.risk_level.value,
            'risk_color': self.risk_level.color,
            'go_no_go': 'GO' if self.go_no_go else 'NO-GO',
            'reasoning': self.reasoning,
            'precautions': self.precautions
        }


@dataclass
class RiskAssessment:
    """Complete multi-stakeholder risk assessment"""
    general_risk: RiskLevel
    convective_potential: str
    paragliding: StakeholderRisk
    hang_gliding: StakeholderRisk
    hot_air_balloon: StakeholderRisk
    gliding: StakeholderRisk
    general_aviation: StakeholderRisk
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'general_risk': self.general_risk.value,
            'general_risk_color': self.general_risk.color,
            'convective_potential': self.convective_potential,
            'stakeholders': {
                'paragliding': self.paragliding.to_dict(),
                'hang_gliding': self.hang_gliding.to_dict(),
                'hot_air_balloon': self.hot_air_balloon.to_dict(),
                'gliding': self.gliding.to_dict(),
                'general_aviation': self.general_aviation.to_dict(),
            }
        }


class RiskAssessor:
    """Assess convective risk for multiple stakeholders"""
    
    def __init__(self, indices: ConvectiveIndices):
        """
        Initialize with convective indices
        
        Args:
            indices: ConvectiveIndices object from analysis
        """
        self.indices = indices
        self.cape = abs(indices.cape)
        self.cin = abs(indices.cin)
        
    def classify_convective_potential(self) -> str:
        """
        Classify overall convective potential based on CAPE
        
        Returns:
            Classification string
        """
        if self.cape < 300:
            return "WEAK"
        elif self.cape < 1000:
            return "MODERATE"
        elif self.cape < 2500:
            return "STRONG"
        else:
            return "EXTREME"
    
    def assess_general_risk(self) -> RiskLevel:
        """
        Assess general atmospheric risk level
        
        Returns:
            RiskLevel enum
        """
        # High CIN provides protection
        if self.cin > 200:
            return RiskLevel.MINIMAL
        elif self.cin > 100:
            return RiskLevel.LOW
        
        # Low CIN - risk depends on CAPE
        if self.cape < 300:
            return RiskLevel.LOW
        elif self.cape < 1000:
            return RiskLevel.MODERATE
        elif self.cape < 2500:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME
    
    def assess_paragliding(self) -> StakeholderRisk:
        """Assess risk for paragliding operations"""
        precautions = []
        
        # Strong cap = excellent conditions
        if self.cin > 200:
            return StakeholderRisk(
                activity="Paragliding",
                risk_level=RiskLevel.MINIMAL,
                go_no_go=True,
                reasoning=f"Strong cap (CIN: {self.cin:.0f} J/kg) prevents convection. Excellent soaring conditions.",
                precautions=["Monitor for cap breakage", "Stay within glide range of landing zones"]
            )
        
        # Moderate cap
        if self.cin > 50:
            return StakeholderRisk(
                activity="Paragliding",
                risk_level=RiskLevel.LOW,
                go_no_go=True,
                reasoning=f"Moderate cap (CIN: {self.cin:.0f} J/kg) limits convection development.",
                precautions=["Monitor cloud development", "Land if cumulus develops rapidly", "Avoid areas of convergence"]
            )
        
        # Weak/no cap - check CAPE
        if self.cape > 1000:
            return StakeholderRisk(
                activity="Paragliding",
                risk_level=RiskLevel.EXTREME,
                go_no_go=False,
                reasoning=f"DANGEROUS: High CAPE ({self.cape:.0f} J/kg) with weak cap. Thunderstorm development likely.",
                precautions=["DO NOT FLY", "Wait for storms to pass", "Check forecast for storm timing"]
            )
        elif self.cape > 500:
            return StakeholderRisk(
                activity="Paragliding",
                risk_level=RiskLevel.HIGH,
                go_no_go=False,
                reasoning=f"Moderate CAPE ({self.cape:.0f} J/kg) with no cap. Convection possible.",
                precautions=["Fly early morning only", "Land by 11am", "Watch for first cumulus"]
            )
        else:
            return StakeholderRisk(
                activity="Paragliding",
                risk_level=RiskLevel.MODERATE,
                go_no_go=True,
                reasoning=f"Low CAPE ({self.cape:.0f} J/kg), weak convection expected.",
                precautions=["Monitor cloud development", "Avoid overdevelopment areas", "Land if conditions deteriorate"]
            )
    
    def assess_hang_gliding(self) -> StakeholderRisk:
        """Assess risk for hang gliding operations"""
        # Similar to paragliding but slightly more tolerant due to higher wing loading
        pg_risk = self.assess_paragliding()
        
        # Downgrade risk by one level for hang gliding (they handle turbulence better)
        if pg_risk.risk_level == RiskLevel.HIGH:
            risk_level = RiskLevel.MODERATE
            go_no_go = True
        elif pg_risk.risk_level == RiskLevel.MODERATE:
            risk_level = RiskLevel.LOW
            go_no_go = True
        else:
            risk_level = pg_risk.risk_level
            go_no_go = pg_risk.go_no_go
        
        return StakeholderRisk(
            activity="Hang Gliding",
            risk_level=risk_level,
            go_no_go=go_no_go,
            reasoning=f"Similar to paragliding but higher wing loading provides more stability. {pg_risk.reasoning}",
            precautions=pg_risk.precautions
        )
    
    def assess_hot_air_balloon(self) -> StakeholderRisk:
        """Assess risk for hot air balloon operations"""
        # Balloons are very sensitive to convection - cannot escape quickly
        
        if self.cape > 500:
            return StakeholderRisk(
                activity="Hot Air Balloon",
                risk_level=RiskLevel.EXTREME,
                go_no_go=False,
                reasoning=f"CAPE {self.cape:.0f} J/kg too high. Balloons cannot escape convective conditions.",
                precautions=["DO NOT FLY", "Sunrise flights only", "Check forecast carefully"]
            )
        elif self.cape > 200:
            return StakeholderRisk(
                activity="Hot Air Balloon",
                risk_level=RiskLevel.HIGH,
                go_no_go=False,
                reasoning=f"CAPE {self.cape:.0f} J/kg presents risk. Limited manoeuvrability in convection.",
                precautions=["Sunrise only", "Land before 8am", "Avoid afternoon operations"]
            )
        else:
            if self.cin > 100:
                return StakeholderRisk(
                    activity="Hot Air Balloon",
                    risk_level=RiskLevel.MINIMAL,
                    go_no_go=True,
                    reasoning=f"Low CAPE ({self.cape:.0f} J/kg) with cap. Good conditions.",
                    precautions=["Standard operating procedures", "Monitor surface heating"]
                )
            else:
                return StakeholderRisk(
                    activity="Hot Air Balloon",
                    risk_level=RiskLevel.LOW,
                    go_no_go=True,
                    reasoning=f"Low CAPE ({self.cape:.0f} J/kg). Acceptable conditions.",
                    precautions=["Fly early", "Monitor cumulus development", "Land if thermals strengthen"]
                )
    
    def assess_gliding(self) -> StakeholderRisk:
        """Assess risk for sailplane/glider operations"""
        # Gliders want some convection for lift but not storms
        
        if self.cape > 2500:
            return StakeholderRisk(
                activity="Gliding (Sailplanes)",
                risk_level=RiskLevel.HIGH,
                go_no_go=False,
                reasoning=f"Extreme CAPE ({self.cape:.0f} J/kg). Storm development likely.",
                precautions=["Morning flights only", "Land before convection develops", "Have alternate landing sites"]
            )
        elif self.cape > 1000:
            if self.cin > 100:
                return StakeholderRisk(
                    activity="Gliding (Sailplanes)",
                    risk_level=RiskLevel.LOW,
                    go_no_go=True,
                    reasoning=f"Good CAPE ({self.cape:.0f} J/kg) with cap control. Excellent XC conditions.",
                    precautions=["Monitor cap breakage", "Track storm development", "Land away from storms"]
                )
            else:
                return StakeholderRisk(
                    activity="Gliding (Sailplanes)",
                    risk_level=RiskLevel.MODERATE,
                    go_no_go=True,
                    reasoning=f"High CAPE ({self.cape:.0f} J/kg) without cap. Good lift but storm risk.",
                    precautions=["Fly early", "Land by early afternoon", "Monitor radar", "20km storm clearance"]
                )
        elif self.cape > 300:
            return StakeholderRisk(
                activity="Gliding (Sailplanes)",
                risk_level=RiskLevel.LOW,
                go_no_go=True,
                reasoning=f"Moderate CAPE ({self.cape:.0f} J/kg). Good thermal conditions.",
                precautions=["Standard XC precautions", "Monitor convection development"]
            )
        else:
            return StakeholderRisk(
                activity="Gliding (Sailplanes)",
                risk_level=RiskLevel.MINIMAL,
                go_no_go=True,
                reasoning=f"Low CAPE ({self.cape:.0f} J/kg). Weak thermals, blue day possible.",
                precautions=["Expect weak lift", "Plan for lower altitudes", "Ridge/wave soaring may be better"]
            )
    
    def assess_general_aviation(self) -> StakeholderRisk:
        """Assess risk for general aviation (VFR)"""
        
        if self.cape > 1500:
            return StakeholderRisk(
                activity="General Aviation (VFR)",
                risk_level=RiskLevel.HIGH,
                go_no_go=False,
                reasoning=f"High CAPE ({self.cape:.0f} J/kg). Embedded thunderstorms likely.",
                precautions=["IFR flight plan", "Storm avoidance equipment required", "20nm storm clearance", "Consider delaying flight"]
            )
        elif self.cape > 500:
            return StakeholderRisk(
                activity="General Aviation (VFR)",
                risk_level=RiskLevel.MODERATE,
                go_no_go=True,
                reasoning=f"Moderate CAPE ({self.cape:.0f} J/kg). Convection possible.",
                precautions=["File VFR flight plan", "Monitor weather radar", "Maintain VMC", "Have alternate routes"]
            )
        else:
            return StakeholderRisk(
                activity="General Aviation (VFR)",
                risk_level=RiskLevel.LOW,
                go_no_go=True,
                reasoning=f"Low CAPE ({self.cape:.0f} J/kg). Good VFR conditions.",
                precautions=["Standard VFR operations", "Monitor METAR/TAF"]
            )
    
    def assess_all(self) -> RiskAssessment:
        """
        Perform complete risk assessment for all stakeholders
        
        Returns:
            RiskAssessment object with all stakeholder analyses
        """
        return RiskAssessment(
            general_risk=self.assess_general_risk(),
            convective_potential=self.classify_convective_potential(),
            paragliding=self.assess_paragliding(),
            hang_gliding=self.assess_hang_gliding(),
            hot_air_balloon=self.assess_hot_air_balloon(),
            gliding=self.assess_gliding(),
            general_aviation=self.assess_general_aviation()
        )


def quick_risk_assessment(cape: float, cin: float) -> Dict:
    """
    Quick risk assessment from CAPE/CIN values
    
    Args:
        cape: CAPE value in J/kg
        cin: CIN value in J/kg (will be converted to positive)
        
    Returns:
        Dictionary with risk assessment
    """
    from convective_engine import ConvectiveIndices
    
    # Create minimal indices object
    indices = ConvectiveIndices(
        cape=cape,
        cin=cin,
        lcl_pressure=900,
        lcl_temperature=15,
        lfc_pressure=None,
        lfc_temperature=None,
        el_pressure=None,
        el_temperature=None,
        surface_temperature=25,
        surface_dewpoint=18,
        parcel_profile=None
    )
    
    assessor = RiskAssessor(indices)
    assessment = assessor.assess_all()
    
    return assessment.to_dict()
