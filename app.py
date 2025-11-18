"""
Convective Risk Analyzer
Real-time atmospheric instability assessment for aviation safety
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import json

from convective_engine import ConvectiveAnalyzer, ConvectiveIndices
from risk_assessment import RiskAssessor, RiskLevel
from data_loader import SoundingLoader, SoundingValidator, load_example_sounding
from metpy.plots import SkewT
from metpy.units import units

# Page config
st.set_page_config(
    page_title="Convective Risk Analyzer",
    page_icon="⛈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .go-status {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .go {
        background-color: #d4edda;
        color: #155724;
    }
    .no-go {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


def create_skewt_plot(sounding, indices):
    """Create Skew-T Log-P diagram with analysis"""
    fig = plt.figure(figsize=(12, 10))
    skew = SkewT(fig, rotation=45)
    
    # Add reference lines
    skew.plot_dry_adiabats(colors='grey', alpha=0.3, linewidth=0.8)
    skew.plot_moist_adiabats(colors='red', alpha=0.3, linewidth=0.8)
    skew.plot_mixing_lines(
        pressure=np.linspace(1000, 250, 1000) * units.hPa,
        colors='tab:cyan', alpha=0.3, linewidth=0.8
    )
    
    # Plot profiles
    p = sounding.pressure * units.hPa
    T = sounding.temperature * units.degC
    Td = sounding.dewpoint * units.degC
    
    skew.plot(p, T, 'r', linewidth=2.5, label='Temperature')
    skew.plot(p, Td, 'g', linewidth=2.5, label='Dewpoint')
    
    # Plot parcel profile
    parcel_prof = indices.parcel_profile * units.degC
    skew.plot(p, parcel_prof, 'k--', linewidth=2, label='Parcel Profile')
    
    # Mark key levels
    skew.plot(indices.lcl_pressure, indices.lcl_temperature, 'o', 
             markersize=12, color='blue', markeredgecolor='black', 
             markeredgewidth=2, label=f'LCL ({indices.lcl_pressure:.0f} hPa)')
    
    if indices.lfc_pressure:
        skew.plot(indices.lfc_pressure, indices.lfc_temperature, '^',
                 markersize=14, color='purple', markeredgecolor='black',
                 markeredgewidth=2, label=f'LFC ({indices.lfc_pressure:.0f} hPa)')
    
    if indices.el_pressure:
        skew.plot(indices.el_pressure, indices.el_temperature, 'v',
                 markersize=14, color='orange', markeredgecolor='black',
                 markeredgewidth=2, label=f'EL ({indices.el_pressure:.0f} hPa)')
    
    # Shade CAPE and CIN
    skew.shade_cape(p, T, parcel_prof, alpha=0.3, label='CAPE')
    skew.shade_cin(p, T, parcel_prof, alpha=0.3, label='CIN')
    
    # Configure axes
    skew.ax.set_xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
    skew.ax.set_ylabel('Pressure (hPa)', fontsize=12, fontweight='bold')
    skew.ax.set_ylim(1000, 200)
    skew.ax.set_xlim(-40, 40)
    
    plt.title('Skew-T Log-P Diagram - Convective Analysis', 
             fontsize=14, fontweight='bold', pad=15)
    plt.legend(loc='upper left', fontsize=9)
    plt.tight_layout()
    
    return fig


def display_risk_card(stakeholder_risk):
    """Display a risk assessment card for a stakeholder"""
    risk_colors = {
        'EXTREME': '#8B0000',
        'HIGH': '#FF4444',
        'MODERATE': '#FFA500',
        'LOW': '#FFD700',
        'MINIMAL': '#90EE90'
    }
    
    color = risk_colors.get(stakeholder_risk.risk_level.value, '#CCCCCC')
    
    st.markdown(f"""
    <div class="risk-box" style="border-left-color: {color};">
        <h3 style="margin-top: 0;">{stakeholder_risk.activity}</h3>
        <div class="go-status {'go' if stakeholder_risk.go_no_go else 'no-go'}">
            {'✓ GO' if stakeholder_risk.go_no_go else '✗ NO-GO'}
        </div>
        <p><strong>Risk Level:</strong> <span style="color: {color}; font-weight: bold;">{stakeholder_risk.risk_level.value}</span></p>
        <p><strong>Assessment:</strong> {stakeholder_risk.reasoning}</p>
        <p><strong>Precautions:</strong></p>
        <ul>
            {''.join([f'<li>{p}</li>' for p in stakeholder_risk.precautions])}
        </ul>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<div class="main-header">⛈️ Convective Risk Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time atmospheric instability assessment for aviation safety</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("📊 Data Input")
    
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["Upload File", "Use Example Data", "Manual Entry"]
    )
    
    sounding = None
    
    if input_method == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload sounding data",
            type=['txt', 'csv'],
            help="Supports Wyoming format (.txt) or CSV files"
        )
        
        if uploaded_file:
            try:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.read())
                
                # Detect format and load
                if uploaded_file.name.endswith('.csv'):
                    sounding_data = SoundingLoader.from_csv(temp_path)
                else:
                    # Try Wyoming format
                    content = open(temp_path, 'r').read()
                    sounding_data = SoundingLoader.from_wyoming_text(content)
                
                sounding = sounding_data
                st.sidebar.success(f"✓ Loaded {len(sounding.pressure)} data points")
                
            except Exception as e:
                st.sidebar.error(f"Error loading file: {str(e)}")
                st.sidebar.info("Please ensure file is in Wyoming or CSV format")
    
    elif input_method == "Use Example Data":
        sounding = load_example_sounding()
        st.sidebar.success("✓ Loaded example unstable sounding")
        st.sidebar.info("This is a synthetic sounding with strong convective potential")
    
    elif input_method == "Manual Entry":
        st.sidebar.info("Enter comma-separated values for each level")
        
        pressure_input = st.sidebar.text_area(
            "Pressure (hPa)",
            "1000,950,900,850,800,700,500,300",
            height=80
        )
        temp_input = st.sidebar.text_area(
            "Temperature (°C)",
            "28,24,20,16,12,4,-12,-40",
            height=80
        )
        dewpoint_input = st.sidebar.text_area(
            "Dewpoint (°C)",
            "22,18,14,10,6,-2,-20,-50",
            height=80
        )
        
        if st.sidebar.button("Analyze Manual Data"):
            try:
                pressure = np.array([float(x.strip()) for x in pressure_input.split(',')])
                temperature = np.array([float(x.strip()) for x in temp_input.split(',')])
                dewpoint = np.array([float(x.strip()) for x in dewpoint_input.split(',')])
                
                sounding = SoundingLoader.from_arrays(pressure, temperature, dewpoint)
                st.sidebar.success(f"✓ Created sounding with {len(pressure)} levels")
            except Exception as e:
                st.sidebar.error(f"Error parsing data: {str(e)}")
    
    # Main content
    if sounding is None:
        st.info("👈 Please upload a sounding file or select example data to begin analysis")
        
        # Show format examples
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Wyoming Format Example")
            st.code("""
PRES   HGHT   TEMP   DWPT
 hPa     m      C      C
1000    104   28.0   22.0
 975    305   26.0   20.0
 950    511   24.0   18.0
 925    722   22.0   16.0
            """)
        
        with col2:
            st.subheader("📊 CSV Format Example")
            st.code("""
pressure,temperature,dewpoint
1000,28,22
975,26,20
950,24,18
925,22,16
            """)
        
        return
    
    # Validate data
    validator = SoundingValidator()
    validation = validator.validate(sounding)
    
    if not validation['valid']:
        st.error("⚠️ Data validation failed")
        for error in validation['errors']:
            st.error(f"• {error}")
        return
    
    if validation['warnings']:
        with st.expander("⚠️ Data Quality Warnings", expanded=False):
            for warning in validation['warnings']:
                st.warning(f"• {warning}")
    
    # Perform analysis
    with st.spinner("Analyzing atmospheric conditions..."):
        analyzer = ConvectiveAnalyzer(sounding)
        indices = analyzer.calculate_indices()
        
        assessor = RiskAssessor(indices)
        assessment = assessor.assess_all()
    
    # Display results in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "✈️ Risk Assessment", 
        "📈 Skew-T Diagram",
        "💾 Export Data"
    ])
    
    with tab1:
        st.header("Convective Indices Summary")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("CAPE", f"{indices.cape:.0f} J/kg")
        with col2:
            st.metric("CIN", f"{indices.cin:.0f} J/kg")
        with col3:
            st.metric("LCL", f"{indices.lcl_pressure:.0f} hPa")
        with col4:
            potential_color = {
                'WEAK': '🟢',
                'MODERATE': '🟡',
                'STRONG': '🟠',
                'EXTREME': '🔴'
            }
            st.metric("Potential", f"{potential_color.get(assessment.convective_potential, '⚪')} {assessment.convective_potential}")
        
        # Detailed indices
        st.subheader("Atmospheric Levels")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Lifting Condensation Level (LCL)**")
            st.write(f"Pressure: {indices.lcl_pressure:.1f} hPa")
            st.write(f"Temperature: {indices.lcl_temperature:.1f}°C")
        
        with col2:
            if indices.lfc_pressure:
                st.markdown("**Level of Free Convection (LFC)**")
                st.write(f"Pressure: {indices.lfc_pressure:.1f} hPa")
                st.write(f"Temperature: {indices.lfc_temperature:.1f}°C")
            else:
                st.markdown("**Level of Free Convection (LFC)**")
                st.write("Not present")
        
        with col3:
            if indices.el_pressure:
                st.markdown("**Equilibrium Level (EL)**")
                st.write(f"Pressure: {indices.el_pressure:.1f} hPa")
                st.write(f"Temperature: {indices.el_temperature:.1f}°C")
            else:
                st.markdown("**Equilibrium Level (EL)**")
                st.write("Not present")
        
        # General risk
        st.subheader("General Risk Assessment")
        risk_emoji = {
            'EXTREME': '🔴',
            'HIGH': '🟠',
            'MODERATE': '🟡',
            'LOW': '🟢',
            'MINIMAL': '🟢'
        }
        st.markdown(f"### {risk_emoji.get(assessment.general_risk.value, '⚪')} {assessment.general_risk.value}")
    
    with tab2:
        st.header("Multi-Stakeholder Risk Assessment")
        
        st.markdown("### Aviation Operations Risk Analysis")
        
        # Display each stakeholder assessment
        display_risk_card(assessment.paragliding)
        display_risk_card(assessment.hang_gliding)
        display_risk_card(assessment.hot_air_balloon)
        display_risk_card(assessment.gliding)
        display_risk_card(assessment.general_aviation)
        
        # Comparison table
        st.subheader("Risk Comparison Table")
        
        comparison_data = {
            'Activity': [
                'Paragliding',
                'Hang Gliding',
                'Hot Air Balloon',
                'Gliding',
                'General Aviation'
            ],
            'Risk Level': [
                assessment.paragliding.risk_level.value,
                assessment.hang_gliding.risk_level.value,
                assessment.hot_air_balloon.risk_level.value,
                assessment.gliding.risk_level.value,
                assessment.general_aviation.risk_level.value
            ],
            'Go/No-Go': [
                '✓ GO' if assessment.paragliding.go_no_go else '✗ NO-GO',
                '✓ GO' if assessment.hang_gliding.go_no_go else '✗ NO-GO',
                '✓ GO' if assessment.hot_air_balloon.go_no_go else '✗ NO-GO',
                '✓ GO' if assessment.gliding.go_no_go else '✗ NO-GO',
                '✓ GO' if assessment.general_aviation.go_no_go else '✗ NO-GO'
            ]
        }
        
        st.dataframe(
            pd.DataFrame(comparison_data),
            hide_index=True,
            use_container_width=True
        )
    
    with tab3:
        st.header("Skew-T Log-P Diagram")
        
        with st.spinner("Generating diagram..."):
            fig = create_skewt_plot(sounding, indices)
            st.pyplot(fig)
            
            # Download button for plot
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="📥 Download Diagram",
                data=buf,
                file_name="skewt_diagram.png",
                mime="image/png"
            )
    
    with tab4:
        st.header("Export Analysis Results")
        
        # Prepare export data
        export_data = {
            'indices': indices.to_dict(),
            'risk_assessment': assessment.to_dict(),
            'data_quality': {
                'n_points': validation['n_points'],
                'quality_score': validation['quality_score'],
                'warnings': validation['warnings']
            }
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            json_str = json.dumps(export_data, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="convective_analysis.json",
                mime="application/json"
            )
        
        with col2:
            # CSV export of indices
            indices_df = pd.DataFrame([indices.to_dict()])
            csv = indices_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="convective_indices.csv",
                mime="text/csv"
            )
        
        # Display JSON preview
        with st.expander("Preview Export Data"):
            st.json(export_data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "⛈️ Convective Risk Analyzer | Built for aviation safety operations"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
