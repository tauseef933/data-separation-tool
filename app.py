import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background with subtle pattern */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        margin: 0;
    }
    
    .main > div {
        background: #f8fafc;
        min-height: 100vh;
        padding: 2rem;
    }
    
    /* Stunning header with glassmorphism */
    .hero-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        backdrop-filter: blur(10px);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 15s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(-10%, -10%) scale(1.1); }
    }
    
    .hero-title {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 20px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Premium cards */
    .premium-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        transform: scaleY(0);
        transition: transform 0.3s ease;
    }
    
    .premium-card:hover::before {
        transform: scaleY(1);
    }
    
    .card-title {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Modern info boxes */
    .info-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #e0f2fe 100%);
        border-left: 4px solid #667eea;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: #1e40af;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        color: #065f46;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        color: #92400e;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
    }
    
    /* Stunning stat boxes */
    .stat-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-box::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
        transition: all 0.5s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
    }
    
    .stat-box:hover::before {
        top: -60%;
        right: -60%;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        position: relative;
        z-index: 1;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
    }
    
    /* Premium buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        background: #f8fafc;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.3rem 0;
        transition: all 0.2s ease;
        border: 2px solid transparent;
    }
    
    .stCheckbox:hover {
        background: #f1f5f9;
        border-color: #667eea;
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
    }
    
    /* File uploader */
    .stFileUploader {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
    }
    
    /* Distribution section */
    .distribution-item {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
    }
    
    .distribution-item:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    /* Mobile responsiveness */
    @media only screen and (max-width: 768px) {
        .main > div {
            padding: 1rem;
        }
        
        .hero-header {
            padding: 2rem 1.5rem;
        }
        
        .hero-title {
            font-size: 1.8rem;
        }
        
        .hero-subtitle {
            font-size: 0.95rem;
        }
        
        .premium-card {
            padding: 1.5rem;
        }
        
        .stat-number {
            font-size: 2rem;
        }
        
        .stat-container {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8rem;
        }
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Smooth animations */
    .premium-card, .stat-box, .stButton>button, .distribution-item {
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

class MultiColumnDetector:
    def __init__(self):
        self.categories = {
            'Fans': {
                'keywords': ['fan', 'ventilator', 'blower', 'exhaust', 'ventilation', 'air circulator', 'cooling fan', 'pedestal', 'tower fan', 'ceiling fan', 'table fan', 'wall fan', 'stand fan', 'industrial fan', 'oscillating'],
                'exclude': ['light', 'lamp', 'bulb', 'led', 'fixture', 'lighting', 'illumination']
            },
            'Lighting': {
                'keywords': ['light', 'lamp', 'bulb', 'lighting', 'led', 'fixture', 'chandelier', 'luminaire', 'illumination', 'lantern', 'sconce', 'pendant', 'downlight', 'spotlight', 'track light', 'ceiling light', 'wall light', 'floor lamp', 'table lamp', 'desk lamp'],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling']
            },
            'Furniture': {
                'keywords': ['chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch', 'bed', 'furniture', 'wardrobe', 'dresser', 'bookcase', 'stool', 'bench', 'ottoman'],
                'exclude': []
            },
            'Decor': {
                'keywords': ['decor', 'decoration', 'vase', 'mirror', 'sculpture', 'cushion', 'rug', 'carpet', 'curtain', 'decorative', 'ornament'],
                'exclude': []
            },
            'Electronics': {
                'keywords': ['tv', 'television', 'monitor', 'speaker', 'computer', 'laptop', 'printer', 'electronic', 'router'],
                'exclude': []
            },
            'Kitchen': {
                'keywords': ['kitchen', 'cookware', 'utensil', 'microwave', 'oven', 'refrigerator', 'blender'],
                'exclude': []
            },
            'Bathroom': {
                'keywords': ['bathroom', 'toilet', 'sink', 'shower', 'bathtub', 'vanity'],
                'exclude': []
            },
            'Outdoor': {
                'keywords': ['outdoor', 'patio', 'garden', 'lawn', 'bbq', 'grill'],
                'exclude': []
            }
        }
        
        self.priority_columns = ['category', 'categories', 'cat', 'product category', 'type', 'product type', 'item type', 'product_type', 'item_type', 'class', 'classification', 'group', 'department']
        self.secondary_columns = ['description', 'desc', 'product description', 'item description', 'name', 'product name', 'item name', 'product_name', 'item_name', 'title', 'product', 'item', 'sku', 'model']
    
    def find_relevant_columns(self, df):
        priority_cols = []
        secondary_cols = []
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(pcol in col_lower for pcol in self.priority_columns):
                priority_cols.append(col)
            elif any(scol in col_lower for scol in self.secondary_columns):
                secondary_cols.append(col)
            elif df[col].dtype == 'object':
                secondary_cols.append(col)
        return priority_cols, secondary_cols
    
    def detect_from_text(self, text, enabled_categories):
        try:
            if pd.isna(text) or text is None:
                return None, 0
            text_clean = str(text).lower().strip().replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('_', ' ')
            if not text_clean:
                return None, 0
            scores = {}
            for category in enabled_categories:
                if category not in self.categories:
                    continue
                cat_info = self.categories[category]
                excluded = False
                for exclude_word in cat_info.get('exclude', []):
                    if exclude_word in text_clean:
                        excluded = True
                        break
                if excluded:
                    continue
                score = 0
                for keyword in cat_info.get('keywords', []):
                    if keyword in text_clean:
                        text_with_spaces = ' ' + text_clean + ' '
                        keyword_with_spaces = ' ' + keyword + ' '
                        if keyword_with_spaces in text_with_spaces or text_clean.startswith(keyword) or text_clean.endswith(keyword):
                            score += 20
                        else:
                            score += 10
                if score > 0:
                    scores[category] = score
            if scores:
                return max(scores, key=scores.get), scores[max(scores, key=scores.get)]
            return None, 0
        except:
            return None, 0
    
    def smart_multi_column_detect(self, row, priority_cols, secondary_cols, enabled_categories):
        try:
            best_category = None
            best_score = 0
            source_col = None
            for col in priority_cols:
                try:
                    cat, score = self.detect_from_text(row[col], enabled_categories)
                    if cat and score > 0:
                        boosted_score = score * 2
                        if boosted_score > best_score:
                            best_score = boosted_score
                            best_category = cat
                            source_col = col
                except:
                    continue
            if best_score == 0:
                for col in secondary_cols:
                    try:
                        cat, score = self.detect_from_text(row[col], enabled_categories)
                        if cat and score > best_score:
                            best_score = score
                            best_category = cat
                            source_col = col
                    except:
                        continue
            return best_category, best_score, source_col
        except:
            return None, 0, None

def get_sheet_info(file):
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = [{'name': name, 'rows': wb[name].max_row or 0, 'cols': wb[name].max_column or 0} for name in wb.sheetnames]
        wb.close()
        return sheets
    except:
        return []

def process_with_multi_column(file, sheet_name, detector, enabled_categories):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        if df.empty:
            return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': []}
        priority_cols, secondary_cols = detector.find_relevant_columns(df)
        df['Detected_Category'] = None
        df['Match_Score'] = 0
        for idx in df.index:
            try:
                cat, score, _ = detector.smart_multi_column_detect(df.loc[idx], priority_cols, secondary_cols, enabled_categories)
                df.at[idx, 'Detected_Category'] = cat
                df.at[idx, 'Match_Score'] = score
            except:
                continue
        forced_assignments = []
        for idx in df[df['Detected_Category'].isna()].index:
            try:
                forced_cat = enabled_categories[idx % len(enabled_categories)] if enabled_categories else None
                if forced_cat:
                    df.at[idx, 'Detected_Category'] = forced_cat
                    forced_assignments.append({'item': str(df.loc[idx, priority_cols[0]])[:50] if priority_cols else "Unknown", 'assigned_to': forced_cat})
            except:
                continue
        separated = {}
        original_cols = [c for c in df.columns if c not in ['Detected_Category', 'Match_Score']]
        for category in enabled_categories:
            cat_data = df[df['Detected_Category'] == category][original_cols].copy()
            if len(cat_data) > 0:
                separated[category] = cat_data
        return separated, {'total_rows': len(df), 'well_matched': len(df[df['Match_Score'] > 0]), 'forced_matched': len(forced_assignments), 'categories_found': len(separated), 'distribution': df['Detected_Category'].value_counts().to_dict(), 'forced_assignments': forced_assignments, 'priority_cols': priority_cols}
    except Exception as e:
        st.error("Error: " + str(e))
        return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': []}

def create_excel(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            from openpyxl.styles import Font, PatternFill, Alignment
            ws = writer.sheets['Data']
            hf = PatternFill(start_color='667eea', end_color='667eea', fill_type='solid')
            for cell in ws[1]:
                cell.fill = hf
                cell.font = Font(color='FFFFFF', bold=True)
                cell.alignment = Alignment(horizontal='center')
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(max(len(str(cell.value)) for cell in col) + 2, 50)
        output.seek(0)
        return output.getvalue()
    except:
        return None

def main():
    # Hero Header
    st.markdown('''
    <div class="hero-header">
        <h1 class="hero-title">Data Separation Tool</h1>
        <p class="hero-subtitle">Professional Excel categorization with intelligent multi-column detection</p>
        <span class="hero-badge">Powered by AI</span>
    </div>
    ''', unsafe_allow_html=True)
    
    if 'detector' not in st.session_state:
        st.session_state.detector = MultiColumnDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    
    # Step 1: Upload
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">1</span>Upload Your File</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
    if uploaded:
        st.markdown('<div class="success-box">✓ File loaded successfully</div>', unsafe_allow_html=True)
        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = [str(s['name']) + " (" + str(s['rows']) + " rows)" for s in sheets]
            sel = st.selectbox("Select sheet to process", opts, label_visibility="collapsed")
            st.session_state.sheet = sheets[opts.index(sel)]['name']
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 2: Categories
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">2</span>Select Categories</h3>', unsafe_allow_html=True)
    all_cats = list(st.session_state.detector.categories.keys())
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Select All", use_container_width=True):
            st.session_state.selected_cats = all_cats.copy()
            st.rerun()
    with c2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.selected_cats = []
            st.rerun()
    selected = [cat for cat in all_cats if st.checkbox(cat, value=cat in st.session_state.selected_cats, key="c_" + cat)]
    st.session_state.selected_cats = selected
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 3: Process
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">3</span>Process Data</h3>', unsafe_allow_html=True)
        if st.button("Start Processing", type="primary", use_container_width=True):
            with st.spinner('Processing your data...'):
                uploaded.seek(0)
                separated, stats = process_with_multi_column(uploaded, st.session_state.sheet, st.session_state.detector, st.session_state.selected_cats)
                st.session_state.processed = separated
                st.session_state.stats = stats
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results
    if st.session_state.processed and st.session_state.stats:
        stats = st.session_state.stats
        
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["total_rows"]) + '</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["well_matched"]) + '</div><div class="stat-label">Well Matched</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["forced_matched"]) + '</div><div class="stat-label">Force Assigned</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["categories_found"]) + '</div><div class="stat-label">Files Created</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if stats.get('priority_cols'):
            st.markdown('<div class="info-box">✓ Priority columns detected: ' + ", ".join(stats["priority_cols"][:3]) + '</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card"><h3 class="card-title">Category Distribution</h3>', unsafe_allow_html=True)
        for cat, count in stats.get('distribution', {}).items():
            if cat:
                pct = round((count / stats['total_rows'] * 100), 1) if stats['total_rows'] > 0 else 0
                st.write("**" + str(cat) + "**: " + str(count) + " items (" + str(pct) + "%)")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card"><h3 class="card-title">Download Your Files</h3>', unsafe_allow_html=True)
        for cat, data in st.session_state.processed.items():
            fname = st.session_state.filename + "_" + cat + ".xlsx"
            excel = create_excel(data)
            if excel:
                st.download_button("Download " + cat + " (" + str(len(data)) + " rows)", excel, fname, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="dl_" + cat)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
