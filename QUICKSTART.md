# Quick Start Guide

Get the Convective Risk Analyzer running in 5 minutes.

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/convective-risk-analyzer.git
cd convective-risk-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

Open browser to `http://localhost:8501`

## Quick Test

1. **Click "Use Example Data"** in sidebar
2. **View results** in Overview tab
3. **Check Risk Assessment** tab for all 5 aviation categories
4. **Explore Skew-T Diagram** tab for visualization
5. **Export data** from Export Data tab

## Upload Your Own Data

### Wyoming Format
1. Go to [University of Wyoming](http://weather.uwyo.edu/upperair/sounding.html)
2. Select station, date, time
3. Copy text output to file (e.g., `sounding.txt`)
4. Upload in app sidebar

### CSV Format
Create CSV with columns: `pressure`, `temperature`, `dewpoint`
```csv
pressure,temperature,dewpoint
1000,28,22
950,24,18
900,20,14
```

## Command Line Usage

```python
from data_loader import SoundingLoader
from convective_engine import ConvectiveAnalyzer
from risk_assessment import RiskAssessor

# Load
sounding = SoundingLoader.from_wyoming('data/unstable_example.txt')

# Analyze
analyzer = ConvectiveAnalyzer(sounding)
indices = analyzer.calculate_indices()

# Assess
assessor = RiskAssessor(indices)
assessment = assessor.assess_all()

# Results
print(f"CAPE: {indices.cape:.0f} J/kg")
print(f"Paragliding: {assessment.paragliding.risk_level.value}")
```

## Troubleshooting

**Issue:** ImportError for MetPy  
**Fix:** `pip install metpy`

**Issue:** Streamlit won't start  
**Fix:** `pip install streamlit`

**Issue:** Data file not loading  
**Fix:** Check file format matches examples in `/data` folder

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) to deploy to web
- Explore [PORTFOLIO_SHOWCASE.md](PORTFOLIO_SHOWCASE.md) for project context

---

Questions? Check the README or open an issue on GitHub.
