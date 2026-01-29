# Customization Guide

This guide shows you how to customize the Data Separation Tool to match your specific business needs.

## Adding New Categories

### Step 1: Edit app.py

Open `app.py` and find the `CategoryDetector` class (around line 105).

### Step 2: Add Your Category

Add your new category to the `self.categories` dictionary:

```python
self.categories = {
    'Lighting': [...existing keywords...],
    'Fans': [...existing keywords...],
    'Furniture': [...existing keywords...],
    
    # ADD YOUR NEW CATEGORY HERE
    'HVAC': [
        'hvac', 'air conditioner', 'ac unit', 'heater', 'thermostat',
        'heating', 'cooling', 'climate control', 'air handler',
        'heat pump', 'furnace', 'boiler', 'radiator', 'ductwork'
    ],
    
    # Or another category
    'Plumbing': [
        'plumbing', 'pipe', 'faucet', 'drain', 'valve', 'fixture',
        'water heater', 'pump', 'sewage', 'drainage', 'piping'
    ]
}
```

### Step 3: Save and Redeploy

**If deployed on Streamlit Cloud:**
1. Commit changes to GitHub
2. Streamlit automatically redeploys (1-2 minutes)

**If running locally:**
1. Save the file
2. Restart Streamlit: `streamlit run app.py`

---

## Adding Keywords to Existing Categories

### Find the Category

Locate the category you want to enhance in the `self.categories` dictionary.

### Add Keywords

```python
'Lighting': [
    'light', 'lamp', 'chandelier',  # existing keywords
    
    # ADD YOUR NEW KEYWORDS HERE
    'luminaire', 'lightbulb', 'dimmer', 'light switch',
    'smart light', 'rgb light', 'strip lighting'
],
```

### Keyword Guidelines

**Good Keywords:**
- Specific terms: 'pendant light', 'ceiling fan'
- Product types: 'chandelier', 'ventilator'
- Common variations: 'ac unit', 'air conditioner'
- Industry terms: 'fixture', 'luminaire'

**Avoid:**
- Generic words: 'item', 'product', 'thing'
- Numbers: '100w', '5ft'
- Brands: 'Phillips', 'GE' (unless brand-specific category)
- Too short: 'ac', 'pc' (can cause false matches)

---

## Changing UI Colors

### Primary Color (Buttons, Headers)

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#2a5298"  # Change this to your brand color
```

**Color Recommendations:**
- Professional Blue: `#2a5298` (current)
- Corporate Navy: `#1e3a5f`
- Modern Teal: `#0d9488`
- Executive Gray: `#4a5568`

### Background Colors

In `.streamlit/config.toml`:

```toml
backgroundColor="#f5f7fa"  # Main background
secondaryBackgroundColor="#ffffff"  # Card backgrounds
```

### Advanced Styling

Edit the CSS in `app.py` (search for `st.markdown("""` with `<style>`):

```python
# Header gradient
.header-container {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}

# Stat boxes gradient
.stat-box {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

---

## Changing File Size Limits

### Streamlit Configuration

Edit `.streamlit/config.toml`:

```toml
[server]
maxUploadSize=200  # Change from 200 MB to your desired limit
```

**Recommended Limits:**
- Small files (< 10 MB): Set to `50`
- Medium files (< 50 MB): Set to `200` (default)
- Large files (< 100 MB): Set to `500`
- Very large files: Consider splitting files

### Platform Limits

**Streamlit Cloud FREE:**
- Hard limit: ~1 GB per app
- Recommended: Keep under 200 MB for best performance

**Hugging Face FREE:**
- More generous limits
- Can handle larger files

---

## Adding Custom Column Detection

### Customize Column Keywords

In `app.py`, find the `find_category_columns` function (around line 190):

```python
def find_category_columns(df: pd.DataFrame) -> List[str]:
    category_keywords = [
        'type', 'category', 'description', 'item', 'product', 'name', 'title',
        
        # ADD YOUR CUSTOM COLUMN NAMES HERE
        'classification', 'group', 'department', 'section', 'line'
    ]
    # ... rest of function
```

**When to Add:**
- Your vendor files use different column names
- You want to scan additional columns
- Standard keywords don't match your data structure

---

## Customizing Output File Names

### Change Naming Pattern

In `app.py`, find the download section (around line 400):

```python
# Current format: OriginalName_Category.xlsx
filename = f"{st.session_state.original_filename}_{category}.xlsx"

# Alternative formats:
# Include date: 
filename = f"{st.session_state.original_filename}_{category}_{datetime.now().strftime('%Y%m%d')}.xlsx"

# Include company name:
filename = f"CompanyName_{category}_{st.session_state.original_filename}.xlsx"

# Simple category names:
filename = f"{category}_Data.xlsx"
```

---

## Adding Data Validation Rules

### Validate Data Before Processing

Add validation in `process_excel_file` function:

```python
def process_excel_file(file, sheet_name: str, detector: CategoryDetector):
    df = pd.read_excel(file, sheet_name=sheet_name)
    
    # ADD VALIDATION HERE
    # Example: Check required columns
    required_columns = ['Item Name', 'Price', 'Quantity']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    # Example: Check for minimum rows
    if len(df) < 10:
        raise ValueError("File must contain at least 10 rows")
    
    # ... rest of processing
```

---

## Customizing Statistics Display

### Add Custom Metrics

In `app.py`, modify the stats display section:

```python
# Current metrics
stats_html = f"""
<div class="stats-container">
    <div class="stat-box">
        <div class="stat-number">{stats['total_rows']:,}</div>
        <div class="stat-label">Total Rows</div>
    </div>
    
    # ADD NEW METRICS HERE
    <div class="stat-box">
        <div class="stat-number">{stats['your_custom_metric']}</div>
        <div class="stat-label">Your Metric</div>
    </div>
</div>
"""
```

---

## Adding Export Formats

### Current: Excel Files Only

To add CSV export:

```python
# In the download section, add:
csv_data = data.to_csv(index=False)
st.download_button(
    label=f"Download {category} CSV",
    data=csv_data,
    file_name=f"{filename}.csv",
    mime="text/csv"
)
```

To add JSON export:

```python
json_data = data.to_json(orient='records', indent=2)
st.download_button(
    label=f"Download {category} JSON",
    data=json_data,
    file_name=f"{filename}.json",
    mime="application/json"
)
```

---

## Branding Customization

### Add Company Logo

1. Upload logo image to GitHub repository (e.g., `logo.png`)

2. In `app.py`, modify header section:

```python
st.markdown(f"""
<div class="header-container">
    <img src="logo.png" style="height: 60px; margin-bottom: 1rem;">
    <h1 class="header-title">Data Separation Tool</h1>
    <p class="header-subtitle">Your Company Name</p>
</div>
""", unsafe_allow_html=True)
```

### Add Company Name

Replace "Data Separation Tool" with your branding:

```python
# In page config
st.set_page_config(
    page_title="YourCompany - Data Tool",
    ...
)

# In header
<h1 class="header-title">YourCompany Data Separator</h1>
```

---

## Advanced: Adding Authentication

### Simple Password Protection

Add at the top of `main()` function:

```python
def main():
    # Check password
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        password = st.text_input("Enter Password:", type="password")
        if st.button("Login"):
            if password == "YOUR_SECURE_PASSWORD":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()
    
    # ... rest of your code
```

**Security Note:** For production, use proper authentication like OAuth or Streamlit's built-in authentication.

---

## Performance Optimization

### For Very Large Files (100,000+ rows)

1. **Add chunk processing:**

```python
# Process in chunks
chunk_size = 10000
chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

for chunk in chunks:
    # Process chunk
    pass
```

2. **Use progress indicators:**

```python
progress_bar = st.progress(0)
for i, chunk in enumerate(chunks):
    # Process chunk
    progress_bar.progress((i + 1) / len(chunks))
```

---

## Common Customization Requests

### Request: "Add more furniture keywords"

**Location:** `app.py` line ~120

**Add:**
```python
'Furniture': [
    # existing keywords...
    'workstation', 'cubicle', 'partition', 'file cabinet',
    'storage bench', 'shoe rack', 'coat rack', 'umbrella stand'
]
```

### Request: "Change button color"

**Location:** `.streamlit/config.toml`

**Change:**
```toml
primaryColor="#YOUR_HEX_COLOR"
```

### Request: "Add category for Tools"

**Location:** `app.py` line ~105

**Add:**
```python
'Tools': [
    'tool', 'drill', 'hammer', 'screwdriver', 'wrench',
    'saw', 'toolbox', 'power tool', 'hand tool', 'equipment'
]
```

### Request: "Export to Google Sheets"

**Requires:** Additional code and Google API setup

**Difficulty:** Advanced (contact developer)

---

## Updating After Deployment

### GitHub + Streamlit Cloud

1. Edit files locally or on GitHub
2. Commit changes
3. Push to GitHub
4. Streamlit auto-deploys (1-2 minutes)

### Direct Edit on Hugging Face

1. Go to your Space
2. Click "Files and versions"
3. Click on file to edit
4. Make changes
5. Commit
6. Auto-rebuilds

---

## Version Control Best Practices

### Keep Track of Changes

Create a `CHANGELOG.md`:

```markdown
# Changelog

## v1.1 - 2024-02-15
- Added HVAC category
- Increased file size limit to 300 MB
- Improved detection accuracy

## v1.0 - 2024-01-29
- Initial release
```

### Tag Releases on GitHub

```bash
git tag -a v1.0 -m "Initial release"
git push origin v1.0
```

---

## Testing Your Customizations

After making changes:

1. **Local Test**
   ```bash
   streamlit run app.py
   ```

2. **Check Console** for errors

3. **Test All Features:**
   - Upload file
   - Select sheet
   - Process data
   - Download results
   - Verify categories

4. **Deploy** when everything works

---

## Getting Help

### Streamlit Community
- Forum: https://discuss.streamlit.io
- Docs: https://docs.streamlit.io
- Gallery: https://streamlit.io/gallery

### Python Libraries
- Pandas: https://pandas.pydata.org/docs
- OpenPyXL: https://openpyxl.readthedocs.io

---

## Backup & Restore

### Before Major Changes

1. Create backup branch on GitHub:
   ```bash
   git checkout -b backup-before-changes
   git push origin backup-before-changes
   ```

2. Make your changes on main branch

3. If something breaks:
   ```bash
   git checkout backup-before-changes
   git branch -D main
   git checkout -b main
   git push -f origin main
   ```

---

## Professional Tips

1. **Start Small**: Add 1-2 keywords at a time, test thoroughly
2. **User Feedback**: Collect uncategorized patterns from users
3. **Regular Updates**: Review and update categories monthly
4. **Documentation**: Update README.md when adding categories
5. **Testing**: Always test locally before deploying

---

## Summary

You can customize:
- ✓ Categories and keywords
- ✓ UI colors and styling  
- ✓ File size limits
- ✓ Column detection logic
- ✓ Output file naming
- ✓ Export formats
- ✓ Validation rules
- ✓ Authentication
- ✓ Branding and logos

The tool is designed to be easily customizable while maintaining professional quality.

**Need help?** Refer to the full README.md and DEPLOYMENT.md guides.
