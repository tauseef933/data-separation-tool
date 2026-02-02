import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Merriweather:wght@400;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #ffffff !important;
        min-height: 100vh;
    }
    
    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
        padding: 0 !important;
    }
    
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    .top-bar {
        background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%);
        height: 80px;
        display: flex;
        align-items: center;
        padding: 0 48px;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
    }
    
    .top-bar-content {
        color: white;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        font-family: 'Merriweather', serif;
    }
    
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 48px;
        font-family: 'Inter', sans-serif;
    }
    
    .page-header {
        margin-bottom: 48px;
        animation: slideIn 0.6s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .page-title {
        font-size: 42px;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 8px;
        font-family: 'Merriweather', serif;
        letter-spacing: -1px;
    }
    
    .page-subtitle {
        font-size: 16px;
        color: #666666;
        font-weight: 400;
        line-height: 1.6;
    }
    
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #e0e0e0 50%, transparent 100%);
        margin: 48px 0;
    }
    
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 32px 0 20px 0;
        font-family: 'Inter', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 13px;
    }
    
    .card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        padding: 32px;
        border-radius: 12px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    .card:hover {
        border-color: #d0d0d0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    
    .card-title {
        color: #1a1a1a;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .card-content {
        color: #444444;
        font-size: 14px;
        line-height: 1.8;
    }
    
    .info-box {
        background: #f5f5f5;
        border-left: 3px solid #2d2d2d;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #333333;
        font-weight: 500;
        line-height: 1.6;
    }
    
    .success-box {
        background: #f0fdf4;
        border-left: 3px solid #22c55e;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #166534;
        font-weight: 500;
    }
    
    .warning-box {
        background: #fffbeb;
        border-left: 3px solid #f59e0b;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #92400e;
        font-weight: 500;
    }
    
    .error-box {
        background: #fef2f2;
        border-left: 3px solid #ef4444;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
        font-size: 14px;
        color: #991b1b;
        font-weight: 500;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        margin: 24px 0;
    }
    
    .stat-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1a1a1a 0%, #666666 100%);
    }
    
    .stat-card:nth-child(2)::before {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
    }
    
    .stat-card:nth-child(3)::before {
        background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
    }
    
    .stat-card:nth-child(4)::before {
        background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
    }
    
    .stat-card:hover {
        border-color: #d0d0d0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 8px;
        font-family: 'Merriweather', serif;
    }
    
    .stat-label {
        font-size: 12px;
        color: #888888;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button {
        background: #1a1a1a !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background: #333333 !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.24) !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.32) !important;
        transform: translateY(-2px) !important;
    }
    
    .distribution-item {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 16px 0;
        padding: 16px;
        background: #f9f9f9;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .distribution-item:hover {
        background: #f5f5f5;
    }
    
    .distribution-label {
        color: #1a1a1a;
        font-weight: 600;
        font-size: 14px;
        min-width: 120px;
    }
    
    .distribution-bar-container {
        flex: 1;
        height: 6px;
        background: #e8e8e8;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .distribution-bar {
        height: 100%;
        background: linear-gradient(90deg, #1a1a1a 0%, #666666 100%);
        border-radius: 10px;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .distribution-value {
        color: #888888;
        font-weight: 600;
        min-width: 50px;
        text-align: right;
        font-size: 13px;
    }
    
    .column-selector {
        background: #f9f9f9;
        padding: 20px;
        border-radius: 8px;
        margin: 16px 0;
        border: 1px solid #e8e8e8;
    }
    
    .checkbox-item {
        display: flex;
        align-items: center;
        padding: 10px 0;
        transition: all 0.2s ease;
    }
    
    .checkbox-item input[type="checkbox"] {
        margin-right: 12px;
        width: 16px;
        height: 16px;
        cursor: pointer;
        accent-color: #1a1a1a;
    }
    
    h2, h3 {
        color: #1a1a1a;
        font-family: 'Merriweather', serif;
    }
    
    p, .stMarkdown, .card-content {
        color: #555555;
        font-weight: 400;
    }
    
    .stFileUploader label, .stSelectbox label, .stMultiSelect label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 600;
        color: #888888;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1a1a1a !important;
        border-bottom: 2px solid #1a1a1a !important;
    }
    
    @media only screen and (max-width: 768px) {
        .page-title {font-size: 32px;}
        .main-container {padding: 24px;}
        .stat-grid {grid-template-columns: repeat(2, 1fr);}
        .top-bar {padding: 0 24px;}
    }
    
    @media only screen and (max-width: 480px) {
        .page-title {font-size: 24px;}
        .main-container {padding: 16px;}
        .card {padding: 16px;}
        .stat-grid {grid-template-columns: 1fr;}
        .top-bar {padding: 0 16px; height: 64px;}
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
        
        self.priority_columns = [
            'category', 'categories', 'cat', 'product category',
            'type', 'product type', 'item type', 'product_type', 'item_type',
            'class', 'classification', 'group', 'department'
        ]
        
        self.secondary_columns = [
            'description', 'desc', 'product description', 'item description',
            'name', 'product name', 'item name', 'product_name', 'item_name',
            'title', 'product', 'item', 'sku', 'model'
        ]
    
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
            
            text_clean = str(text).lower().strip()
            # Simple character replacement - no complex regex
            text_clean = text_clean.replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('_', ' ')
            
            if not text_clean:
                return None, 0
            
            scores = {}
            
            for category in enabled_categories:
                if category not in self.categories:
                    continue
                
                cat_info = self.categories[category]
                
                # Check exclusions
                excluded = False
                for exclude_word in cat_info.get('exclude', []):
                    if exclude_word in text_clean:
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                # Count keyword matches - iOS-safe method
                score = 0
                for keyword in cat_info.get('keywords', []):
                    if keyword in text_clean:
                        # Add space around text for word boundary checking
                        text_with_spaces = ' ' + text_clean + ' '
                        keyword_with_spaces = ' ' + keyword + ' '
                        
                        # Check if keyword appears as whole word
                        if keyword_with_spaces in text_with_spaces:
                            score += 20
                        elif text_clean.startswith(keyword) or text_clean.endswith(keyword):
                            score += 20
                        else:
                            score += 10
                
                if score > 0:
                    scores[category] = score
            
            if scores:
                best_cat = max(scores, key=scores.get)
                return best_cat, scores[best_cat]
            
            return None, 0
            
        except:
            return None, 0
    
    def smart_multi_column_detect(self, row, priority_cols, secondary_cols, enabled_categories):
        try:
            best_category = None
            best_score = 0
            source_col = None
            
            # Check priority columns first
            for col in priority_cols:
                try:
                    text = row[col]
                    cat, score = self.detect_from_text(text, enabled_categories)
                    
                    if cat and score > 0:
                        boosted_score = score * 2
                        if boosted_score > best_score:
                            best_score = boosted_score
                            best_category = cat
                            source_col = col
                except:
                    continue
            
            # Check secondary columns if needed
            if best_score == 0:
                for col in secondary_cols:
                    try:
                        text = row[col]
                        cat, score = self.detect_from_text(text, enabled_categories)
                        
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
        sheets = []
        for name in wb.sheetnames:
            try:
                sheet = wb[name]
                sheets.append({'name': name, 'rows': sheet.max_row or 0, 'cols': sheet.max_column or 0})
            except:
                continue
        wb.close()
        return sheets
    except Exception as e:
        st.error("Error reading file: " + str(e))
        return []

def process_with_multi_column(file, sheet_name, detector, enabled_categories):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        
        if df.empty:
            return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': []}
        
        priority_cols, secondary_cols = detector.find_relevant_columns(df)
        
        df['Detected_Category'] = None
        df['Match_Score'] = 0
        df['Source_Column'] = ""
        
        for idx in df.index:
            try:
                row = df.loc[idx]
                cat, score, source = detector.smart_multi_column_detect(row, priority_cols, secondary_cols, enabled_categories)
                
                df.at[idx, 'Detected_Category'] = cat
                df.at[idx, 'Match_Score'] = score
                df.at[idx, 'Source_Column'] = source if source else ""
                
            except:
                continue
        
        forced_assignments = []
        unmatched = df[df['Detected_Category'].isna()].index
        
        for idx in unmatched:
            try:
                forced_cat = enabled_categories[idx % len(enabled_categories)] if enabled_categories else None
                
                if forced_cat:
                    df.at[idx, 'Detected_Category'] = forced_cat
                    
                    item_name = "Unknown"
                    if priority_cols:
                        try:
                            item_name = str(df.loc[idx, priority_cols[0]])[:50]
                        except:
                            pass
                    
                    forced_assignments.append({'item': item_name, 'assigned_to': forced_cat})
            except:
                continue
        
        separated = {}
        original_cols = [c for c in df.columns if c not in ['Detected_Category', 'Match_Score', 'Source_Column']]
        
        for category in enabled_categories:
            try:
                cat_data = df[df['Detected_Category'] == category][original_cols].copy()
                if len(cat_data) > 0:
                    separated[category] = cat_data
            except:
                continue
        
        stats = {
            'total_rows': len(df),
            'well_matched': len(df[df['Match_Score'] > 0]),
            'forced_matched': len(forced_assignments),
            'categories_found': len(separated),
            'distribution': df['Detected_Category'].value_counts().to_dict(),
            'forced_assignments': forced_assignments,
            'priority_cols': priority_cols,
            'secondary_cols': secondary_cols
        }
        
        return separated, stats
        
    except Exception as e:
        st.error("Error processing: " + str(e))
        return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': []}

def create_excel(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            wb = writer.book
            ws = writer.sheets['Data']
            
            from openpyxl.styles import Font, PatternFill, Alignment
            hf = PatternFill(start_color='2a5298', end_color='2a5298', fill_type='solid')
            hfont = Font(color='FFFFFF', bold=True)
            
            for cell in ws[1]:
                cell.fill = hf
                cell.font = hfont
                cell.alignment = Alignment(horizontal='center')
            
            for col in ws.columns:
                max_len = 10
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_len:
                            max_len = len(str(cell.value))
                    except:
                        pass
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
        
        output.seek(0)
        return output.getvalue()
    except:
        return None

def main():
    st.markdown('<div class="top-bar"><div class="top-bar-content">Data Separation Tool</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('''
    <div class="page-header">
        <div class="page-title">Intelligent Data Organization</div>
        <div class="page-subtitle">Upload your spreadsheet and automatically categorize your data with precision and efficiency</div>
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
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown('''<div style="padding: 32px; background: #ffffff; border-radius: 12px; border: 1px solid #e8e8e8;">''', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Upload File</div>', unsafe_allow_html=True)
        
        uploaded = st.file_uploader("Choose a file", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
        
        if uploaded:
            st.markdown('<div class="success-box">File successfully loaded and ready for processing</div>', unsafe_allow_html=True)
            sheets = get_sheet_info(uploaded)
            if sheets:
                opts = []
                for s in sheets:
                    opts.append(str(s['name']) + " (" + str(s['rows']) + " rows)")
                
                st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
                sel = st.selectbox("Sheet Selection", opts, label_visibility="collapsed")
                st.session_state.sheet = sheets[opts.index(sel)]['name']
                st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''<div style="padding: 32px; background: #f9f9f9; border-radius: 12px; border: 1px solid #e8e8e8;">''', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)
        st.markdown('<div style="display: flex; flex-direction: column; gap: 8px;">', unsafe_allow_html=True)
        
        all_cats = list(st.session_state.detector.categories.keys())
        
        if st.button("Select All", use_container_width=True, key="select_all"):
            st.session_state.selected_cats = all_cats.copy()
            st.rerun()
        
        if st.button("Clear All", use_container_width=True, key="clear_all"):
            st.session_state.selected_cats = []
            st.rerun()
        
        if st.button("Reset to Default", use_container_width=True, key="reset_cats"):
            st.session_state.selected_cats = ['Lighting', 'Fans']
            st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown('''<div style="padding: 32px; background: #ffffff; border-radius: 12px; border: 1px solid #e8e8e8; margin-bottom: 24px;">''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Select Categories</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="color: #666666; font-size: 14px; margin-bottom: 20px; line-height: 1.6;">Choose which product categories to detect. The system will intelligently categorize your data based on descriptions and names.</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    selected = []
    for idx, cat in enumerate(all_cats):
        with cols[idx % 4]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key="c_" + cat):
                selected.append(cat)
    
    st.session_state.selected_cats = selected
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded and st.session_state.selected_cats:
        st.markdown('''<div style="padding: 32px; background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); border-radius: 12px; margin-bottom: 32px; color: white;">''', unsafe_allow_html=True)
        
        categories_count = len(st.session_state.selected_cats)
        st.markdown(f'<div style="font-size: 16px; font-weight: 600; margin-bottom: 16px;">Ready to Process</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 20px;">{categories_count} categories selected for classification</div>', unsafe_allow_html=True)
        
        if st.button("Process & Separate Data", type="primary", use_container_width=True, key="process_btn"):
            try:
                with st.spinner('Processing your data...'):
                    uploaded.seek(0)
                    separated, stats = process_with_multi_column(
                        uploaded, 
                        st.session_state.sheet, 
                        st.session_state.detector,
                        st.session_state.selected_cats
                    )
                    st.session_state.processed = separated
                    st.session_state.stats = stats
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.processed and st.session_state.stats:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        stats = st.session_state.stats
        
        st.markdown('''<div style="padding: 32px; background: #ffffff; border-radius: 12px; border: 1px solid #e8e8e8; margin-bottom: 24px;">''', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Processing Results</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-number">{stats["total_rows"]}</div>
            <div class="stat-label">Total Records</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-number">{stats["well_matched"]}</div>
            <div class="stat-label">Accurately Matched</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-number">{stats["forced_matched"]}</div>
            <div class="stat-label">Auto Assigned</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-number">{stats["categories_found"]}</div>
            <div class="stat-label">Output Files</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if stats.get('priority_cols'):
            priority_cols_text = ", ".join(stats["priority_cols"][:3])
            st.markdown(f'<div class="info-box">Detected key columns: {priority_cols_text}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('''<div style="padding: 32px; background: #ffffff; border-radius: 12px; border: 1px solid #e8e8e8; margin-bottom: 24px;">''', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Category Distribution</div>', unsafe_allow_html=True)
        
        total_items = stats['total_rows']
        
        for cat, count in sorted(stats.get('distribution', {}).items(), key=lambda x: x[1], reverse=True):
            if cat:
                pct = (count / total_items * 100) if total_items > 0 else 0
                
                st.markdown(f'''
                <div class="distribution-item">
                    <div class="distribution-label">{cat}</div>
                    <div class="distribution-bar-container">
                        <div class="distribution-bar" style="width: {pct}%"></div>
                    </div>
                    <div class="distribution-value">{count} ({round(pct, 1)}%)</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('''<div style="padding: 32px; background: #ffffff; border-radius: 12px; border: 1px solid #e8e8e8;">''', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Download Separated Files</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="color: #666666; font-size: 14px; margin-bottom: 20px; line-height: 1.6;">Your data has been separated and is ready for download. Each category is in its own file.</div>', unsafe_allow_html=True)
        
        download_cols = st.columns(2)
        for idx, (cat, data) in enumerate(sorted(st.session_state.processed.items())):
            with download_cols[idx % 2]:
                fname = st.session_state.filename + "_" + cat + ".xlsx"
                excel = create_excel(data)
                if excel:
                    st.download_button(
                        f"{cat} • {len(data)} records", 
                        excel, 
                        fname, 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                        use_container_width=True,
                        key="dl_" + cat
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

