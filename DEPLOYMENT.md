# Deployment Guide - Convective Risk Analyzer

This guide walks through deploying the Convective Risk Analyzer to Streamlit Cloud for free public hosting.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- Git installed locally

## Step 1: Prepare Repository

1. **Create GitHub repository:**
   ```bash
   # On GitHub, create new repository: convective-risk-analyzer
   # Do NOT initialize with README (we have our own)
   ```

2. **Initialize local repository:**
   ```bash
   cd convective-risk-analyzer
   git init
   git add .
   git commit -m "Initial commit: Convective Risk Analyzer"
   ```

3. **Connect to GitHub:**
   ```bash
   git remote add origin https://github.com/yourusername/convective-risk-analyzer.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Verify Files

Ensure your repository contains:

```
convective-risk-analyzer/
├── app.py                    # ✅ Main Streamlit app
├── convective_engine.py      # ✅ Core calculations
├── risk_assessment.py        # ✅ Risk logic
├── data_loader.py            # ✅ Data ingestion
├── requirements.txt          # ✅ Dependencies
├── README.md                 # ✅ Documentation
├── DEPLOYMENT.md            # ✅ This file
├── data/                     # ✅ Example data
│   ├── unstable_example.txt
│   └── stable_example.csv
└── outputs/                  # ✅ Example outputs
    └── skewt_example.png
```

## Step 3: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Create New App:**
   - Click "New app" button
   - Select your GitHub repository: `yourusername/convective-risk-analyzer`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

3. **Wait for Deployment:**
   - Streamlit Cloud will install dependencies from `requirements.txt`
   - Deployment typically takes 2-5 minutes
   - Watch logs for any errors

4. **Get Your URL:**
   - Once deployed, you'll get a URL like:
   - `https://convective-risk-analyzer.streamlit.app`
   - Or `https://yourusername-convective-risk-analyzer.streamlit.app`

## Step 4: Update README

Update the live demo link in `README.md`:

```markdown
**[🔴 Live Demo](https://your-actual-url.streamlit.app)**
```

Commit and push:
```bash
git add README.md
git commit -m "Update live demo URL"
git push
```

## Step 5: Test Deployment

1. **Visit your app URL**
2. **Test Example Data:**
   - Click "Use Example Data" in sidebar
   - Verify Skew-T diagram renders
   - Check all risk assessments display
3. **Test File Upload:**
   - Upload `data/unstable_example.txt`
   - Verify analysis completes
4. **Test Export:**
   - Download JSON and CSV exports
   - Verify data integrity

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError**
```
Solution: Ensure all dependencies are in requirements.txt with correct versions
```

**Issue: File Not Found**
```python
# Wrong (absolute path):
sounding = SoundingLoader.from_wyoming('/home/claude/data/example.txt')

# Correct (relative path):
sounding = SoundingLoader.from_wyoming('data/example.txt')
```

**Issue: Memory Error**
```
Solution: Optimize plot generation, reduce figure size in create_skewt_plot()
```

**Issue: Slow Performance**
```python
# Add caching to expensive operations:
@st.cache_data
def create_skewt_plot(sounding, indices):
    # ... plotting code ...
```

## Advanced Configuration

### Custom Domain (Optional)

Streamlit Cloud supports custom domains:

1. Go to app settings
2. Add your custom domain
3. Update DNS records as instructed

### Environment Variables (If Needed)

Create `.streamlit/secrets.toml`:
```toml
# For API keys, database connections, etc.
API_KEY = "your_key_here"
```

Access in code:
```python
import streamlit as st
api_key = st.secrets["API_KEY"]
```

### App Configuration

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200  # MB
```

## Performance Optimization

1. **Use caching aggressively:**
   ```python
   @st.cache_data
   def load_data(file_path):
       return SoundingLoader.from_wyoming(file_path)
   ```

2. **Minimize plot regeneration:**
   - Cache Skew-T plot generation
   - Only regenerate when data changes

3. **Optimize data processing:**
   - Use NumPy vectorized operations
   - Avoid Python loops where possible

## Monitoring

Streamlit Cloud provides:
- Usage analytics (viewers, sessions)
- Error logs
- Resource monitoring (CPU, memory)

Access via app dashboard on Streamlit Cloud.

## Cost

**Free Tier:**
- Public apps: Unlimited
- Private apps: 1 free
- Resources: 1 GB RAM, 2 CPU cores
- No credit card required

**Paid Tier** (if you need more):
- More private apps
- Increased resources
- Priority support
- Starting at $20/month

## Going Live Checklist

- [ ] Repository pushed to GitHub
- [ ] App deployed to Streamlit Cloud
- [ ] All example data files included
- [ ] README.md updated with live demo URL
- [ ] Test all features in production
- [ ] Example sounding loads correctly
- [ ] File upload works
- [ ] Skew-T diagram renders
- [ ] Risk assessments display
- [ ] Export functions work
- [ ] No console errors
- [ ] Add to portfolio website
- [ ] Share on LinkedIn
- [ ] Add to GitHub profile README

## Maintenance

### Updating the App

1. Make changes locally
2. Test thoroughly
3. Commit and push to GitHub
4. Streamlit Cloud auto-deploys from main branch
5. Monitor logs for issues

### Dependency Updates

Periodically update `requirements.txt`:
```bash
pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt
```

## Support

- **Streamlit Docs:** [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum:** [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues:** Report bugs in your repository

## Next Steps

After successful deployment:

1. **Portfolio Integration:**
   - Add to personal website
   - Include in CV/resume
   - Link from LinkedIn profile

2. **Promotion:**
   - Post on relevant subreddits (r/aviation, r/paragliding)
   - Share in meteorology communities
   - Write blog post about the project

3. **Enhancement:**
   - Gather user feedback
   - Add requested features
   - Improve documentation based on questions

---

**Ready to deploy?** Follow these steps and you'll have a live, professional web application in under 15 minutes!
