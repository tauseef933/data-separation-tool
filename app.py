import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); padding: 2rem;}
    .header-box {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 2.5rem 3rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.15);}
    .header-title {color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0;}
    .header-subtitle {color: #b8d4f1; font-size: 1rem; margin-top: 0.5rem;}
    .card {background: #ffffff; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); margin-bottom: 1.5rem;}
    .card-title {color: #1a1a1a; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; border-bottom: 2px solid #2a5298; padding-bottom: 0.8rem;}
    .info-box {background: #e3f2fd; border-left: 4px solid #1976d2; padding: 1rem; border-radius: 6px; margin: 1rem 0;}
    .success-box {background: #e8f5e9; border-left: 4px solid #4caf50; padding: 1rem; border-radius: 6px; margin: 1rem 0;}
    .warning-box {background: #fff3e0; border-left: 4px solid #f57c00; padding: 1rem; border-radius: 6px; margin: 1rem 0;}
    .stat-box {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center;}
    .stat-number {font-size: 2rem; font-weight: 700;}
    .stat-label {font-size: 0.9rem; opacity: 0.9;}
    .stButton>button {background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%); color: white; border: none; padding: 0.75rem 2rem; border-radius: 8px; font-weight: 600; width: 100%;}
    .category-checkbox {background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 2px solid #e9ecef;}
    .category-checkbox:hover {border-color: #2a5298; background: #f0f4f8;}
    .instruction-box {background: #fff9e6; border: 2px solid #ffd700; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;}
    .instruction-title {color: #b8860b; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;}
</style>
""", unsafe_allow_html=True)

class SmartCategoryDetector:
    def __init__(self):
        # More specific keywords with priority scoring
        self.categories = {
            'Lighting': {
                'primary': ['ceiling light', 'pendant light', 'chandelier', 'wall light', 'floor lamp', 'table lamp', 'desk lamp', 'led light', 'light fixture', 'downlight', 'spotlight', 'track light', 'recessed light', 'strip light'],
                'secondary': ['light', 'lamp', 'bulb', 'lighting', 'luminaire', 'sconce', 'lantern', 'led', 'fluorescent', 'halogen']
            },
            'Fans': {
                'primary': ['ceiling fan', 'exhaust fan', 'pedestal fan', 'table fan', 'wall fan', 'tower fan', 'stand fan', 'industrial fan', 'ventilation fan', 'oscillating fan'],
                'secondary': ['fan', 'ventilator', 'blower', 'air circulator', 'extractor']
            },
            'Furniture': {
                'primary': ['office chair', 'dining table', 'coffee table', 'office desk', 'computer desk', 'filing cabinet', 'book shelf', 'sofa set', 'bed frame', 'wardrobe', 'dresser'],
                'secondary': ['chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch', 'bed', 'bookcase', 'stool', 'bench', 'ottoman']
            },
            'Decor': {
                'primary': ['wall art', 'picture frame', 'decorative vase', 'throw pillow', 'area rug', 'wall mirror', 'wall hanging', 'centerpiece'],
                'secondary': ['decor', 'decoration', 'ornament', 'vase', 'mirror', 'sculpture', 'cushion', 'rug', 'carpet', 'curtain']
            },
            'Electronics': {
                'primary': ['television', 'smart tv', 'computer monitor', 'laptop', 'desktop computer', 'wifi router'],
                'secondary': ['tv', 'monitor', 'speaker', 'computer', 'printer', 'scanner', 'router', 'projector']
            },
            'Kitchen': {
                'primary': ['kitchen cabinet', 'dining table', 'kitchen appliance', 'cookware set'],
                'secondary': ['cookware', 'utensil', 'microwave', 'oven', 'refrigerator', 'blender', 'toaster']
            },
            'Bathroom': {
                'primary': ['bathroom vanity', 'shower head', 'bathroom cabinet', 'toilet seat'],
                'secondary': ['bathroom', 'toilet', 'sink', 'faucet', 'shower', 'bathtub']
            },
            'Outdoor': {
                'primary': ['patio furniture', 'garden furniture', 'outdoor light', 'bbq grill'],
                'secondary': ['outdoor', 'patio', 'garden', 'lawn', 'deck']
            }
        }
    
    def detect_category(self, text, enabled_categories):
        """Detect category with priority scoring - only from enabled categories"""
        if pd.isna(text):
            return None
        
        text_lower = str(text).lower().strip()
        
        # Only check enabled categories
        best_category = None
        best_score = 0
        
        for category in enabled_categories:
            if category not in self.categories:
                continue
                
            keywords = self.categories[category]
            score = 0
            
            # Primary keywords worth 10 points (more specific)
            for keyword in keywords['primary']:
                if keyword in text_lower:
                    score += 10
            
            # Secondary keywords worth 2 points (less specific)
            for keyword in keywords['secondary']:
                if keyword in text_lower:
                    score += 2
            
            # Update best match
            if score > best_score:
                best_score = score
                best_category = category
        
        # Require minimum score to avoid false positives
        if best_score >= 10:  # Must have at least one primary keyword
            return best_category
        elif best_score >= 4:  # Or at least 2 secondary keywords
            return best_category
        
        return None

def get_sheet_info(file):
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = []
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            sheets.append({
                'name': sheet_name,
                'rows': sheet.max_row,
                'cols': sheet.max_column
            })
        wb.close()
        return sheets
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return []

def process_file(file, sheet_name, detector, enabled_categories, include_unmatched):
    """Process file with selected categories only"""
    df = pd.read_excel(file, sheet_name=sheet_name)
    df['Detected_Category'] = None
    
    # Find columns that might contain category info
    category_cols = [col for col in df.columns if any(kw in str(col).lower() for kw in ['type', 'category', 'description', 'item', 'product', 'name', 'title'])]
    
    # If no specific columns found, check all text columns
    if not category_cols:
        category_cols = [col for col in df.columns if df[col].dtype == 'object']
    
    # Detect categories for each row
    for idx, row in df.iterrows():
        detected = None
        
        # Check category columns first
        for col in category_cols:
            cat = detector.detect_category(row[col], enabled_categories)
            if cat:
                detected = cat
                break
        
        df.at[idx, 'Detected_Category'] = detected
    
    # Separate data by category
    separated = {}
    
    for category in enabled_categories:
        cat_data = df[df['Detected_Category'] == category].drop('Detected_Category', axis=1)
        if len(cat_data) > 0:
            separated[category] = cat_data
    
    # Handle unmatched rows
    unmatched_data = df[df['Detected_Category'].isna()].drop('Detected_Category', axis=1)
    if include_unmatched and len(unmatched_data) > 0:
        separated['Other_Unmatched'] = unmatched_data
    
    stats = {
        'total_rows': len(df),
        'matched_rows': len(df[df['Detected_Category'].notna()]),
        'unmatched_rows': len(unmatched_data),
        'categories_found': len(separated),
        'distribution': df['Detected_Category'].value_counts().to_dict() if len(df[df['Detected_Category'].notna()]) > 0 else {}
    }
    
    return separated, stats

def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        from openpyxl.styles import Font, PatternFill, Alignment
        header_fill = PatternFill(start_color='2a5298', end_color='2a5298', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        for col in worksheet.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_len:
                        max_len = len(str(cell.value))
                except:
                    pass
            worksheet.column_dimensions[col_letter].width = min(max_len + 2, 50)
    
    output.seek(0)
    return output.getvalue()

def main():
    st.markdown('<div class="header-box"><h1 class="header-title">Data Separation Tool</h1><p class="header-subtitle">Smart Excel categorization with user-controlled category selection</p></div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = SmartCategoryDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    
    # Instructions
    st.markdown("""
    <div class="instruction-box">
        <div class="instruction-title">How to Use:</div>
        <ol style="margin: 0.5rem 0 0 1.5rem; line-height: 1.8;">
            <li><strong>Upload</strong> your Excel file</li>
            <li><strong>Select categories</strong> you want to separate (e.g., only Fans + Lighting)</li>
            <li><strong>Choose</strong> what to do with unmatched items</li>
            <li><strong>Process</strong> and download separated files</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card"><h3 class="card-title">Step 1: Upload Excel File</h3>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Select your Excel file", type=['xlsx', 'xlsm', 'xls'])
        
        if uploaded:
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
            st.markdown('<div class="info-box">✓ File loaded successfully</div>', unsafe_allow_html=True)
            
            sheets = get_sheet_info(uploaded)
            if sheets:
                sheet_options = [f"{s['name']} ({s['rows']} rows × {s['cols']} cols)" for s in sheets]
                selected = st.selectbox("Select sheet to process", sheet_options)
                sheet_name = sheets[sheet_options.index(selected)]['name']
                st.session_state.selected_sheet = sheet_name
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><h3 class="card-title">Step 2: Select Categories</h3>', unsafe_allow_html=True)
        
        st.markdown('<p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">Choose which categories to look for in your file:</p>', unsafe_allow_html=True)
        
        # Category selection
        all_categories = list(st.session_state.detector.categories.keys())
        
        # Quick select buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Select All", use_container_width=True):
                st.session_state.selected_cats = all_categories
                st.rerun()
        with col_b:
            if st.button("Clear All", use_container_width=True):
                st.session_state.selected_cats = []
                st.rerun()
        
        # Initialize if not exists
        if 'selected_cats' not in st.session_state:
            st.session_state.selected_cats = ['Lighting', 'Fans']  # Default
        
        # Category checkboxes
        selected_categories = []
        for category in all_categories:
            if st.checkbox(category, value=category in st.session_state.selected_cats, key=f"cat_{category}"):
                selected_categories.append(category)
        
        st.session_state.selected_cats = selected_categories
        
        # Unmatched handling
        st.markdown("---")
        st.markdown('<p style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Handle unmatched items:</p>', unsafe_allow_html=True)
        include_unmatched = st.radio(
            "Items not matching selected categories:",
            ["Include in 'Other' file", "Ignore completely"],
            index=0,
            help="Choose whether to create a separate file for items that don't match your selected categories"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Processing section
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="card"><h3 class="card-title">Step 3: Process Data</h3>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="info-box">Ready to process with {len(st.session_state.selected_cats)} selected categories: <strong>{", ".join(st.session_state.selected_cats)}</strong></div>', unsafe_allow_html=True)
        
        if st.button("🚀 Process Data", type="primary"):
            if len(st.session_state.selected_cats) == 0:
                st.error("Please select at least one category!")
            else:
                with st.spinner('Processing your data...'):
                    uploaded.seek(0)
                    progress = st.progress(0)
                    progress.progress(30)
                    
                    separated, stats = process_file(
                        uploaded, 
                        st.session_state.selected_sheet, 
                        st.session_state.detector,
                        st.session_state.selected_cats,
                        include_unmatched == "Include in 'Other' file"
                    )
                    
                    progress.progress(70)
                    st.session_state.processed = separated
                    st.session_state.stats = stats
                    progress.progress(100)
                
                st.markdown('<div class="success-box">✓ Processing complete!</div>', unsafe_allow_html=True)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif uploaded and not st.session_state.selected_cats:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.warning("⚠️ Please select at least one category to process")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.processed:
        st.markdown("---")
        st.markdown('<div class="card"><h3 class="card-title">Results & Downloads</h3>', unsafe_allow_html=True)
        stats = st.session_state.stats
        
        # Statistics
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]:,}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["matched_rows"]:,}</div><div class="stat-label">Matched</div></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["unmatched_rows"]:,}</div><div class="stat-label">Unmatched</div></div>', unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["categories_found"]}</div><div class="stat-label">Files</div></div>', unsafe_allow_html=True)
        
        # Warnings
        if stats['unmatched_rows'] > 0:
            percentage = (stats['unmatched_rows'] / stats['total_rows']) * 100
            st.markdown(f'<div class="warning-box"><strong>Note:</strong> {stats["unmatched_rows"]} rows ({percentage:.1f}%) did not match your selected categories.</div>', unsafe_allow_html=True)
        
        # Distribution table
        if stats['distribution']:
            st.markdown("### Category Distribution")
            dist_data = []
            for cat, count in stats['distribution'].items():
                if cat is not None:
                    percentage = (count / stats['total_rows']) * 100
                    dist_data.append({'Category': cat, 'Count': count, 'Percentage': f"{percentage:.1f}%"})
            
            if dist_data:
                dist_df = pd.DataFrame(dist_data)
                st.dataframe(dist_df, use_container_width=True, hide_index=True)
        
        # Download section
        st.markdown("### Download Separated Files")
        
        if len(st.session_state.processed) > 0:
            dl_cols = st.columns(min(len(st.session_state.processed), 3))
            for idx, (cat, data) in enumerate(st.session_state.processed.items()):
                with dl_cols[idx % 3]:
                    filename = f"{st.session_state.filename}_{cat}.xlsx"
                    excel = create_excel(data)
                    st.download_button(
                        f"📥 {cat}\n({len(data)} rows)", 
                        excel, 
                        filename, 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                        use_container_width=True
                    )
        else:
            st.info("No data matched your selected categories. Try selecting more categories or check your data.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown('<div style="text-align: center; color: #718096; font-size: 0.85rem; padding: 1rem;">Data Separation Tool v2.0 - Enhanced with Smart Category Selection</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
