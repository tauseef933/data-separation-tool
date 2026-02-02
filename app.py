import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import io

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #f5f7fa !important;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stMainBlockContainer"] {
        padding: 2rem 3rem !important;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Header */
    .header {
        background: white;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
    
    .header-title {
        font-size: 32px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 16px;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Card Styles */
    .card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f3f4f6;
    }
    
    /* Stats Cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
    }
    
    .stat-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .stat-card:nth-child(1) {
        border-top: 3px solid #3b82f6;
    }
    
    .stat-card:nth-child(2) {
        border-top: 3px solid #10b981;
    }
    
    .stat-card:nth-child(3) {
        border-top: 3px solid #f59e0b;
    }
    
    .stat-card:nth-child(4) {
        border-top: 3px solid #8b5cf6;
    }
    
    .stat-value {
        font-size: 36px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Buttons */
    .stButton > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3) !important;
        width: 100% !important;
        height: 44px !important;
    }
    
    .stButton > button:hover {
        background: #2563eb !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    .stDownloadButton > button {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        padding: 0.875rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3) !important;
        width: 100% !important;
        height: 48px !important;
    }
    
    .stDownloadButton > button:hover {
        background: #059669 !important;
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Category Selection */
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    /* Alert Messages */
    .success-message {
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-left: 4px solid #10b981;
        color: #065f46;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 14px;
    }
    
    .info-message {
        background: #eff6ff;
        border: 1px solid #3b82f6;
        border-left: 4px solid #3b82f6;
        color: #1e40af;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 14px;
    }
    
    .warning-message {
        background: #fffbeb;
        border: 1px solid #f59e0b;
        border-left: 4px solid #f59e0b;
        color: #92400e;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Distribution Bars */
    .distribution-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border: 1px solid #e5e7eb;
    }
    
    .distribution-label {
        font-weight: 600;
        color: #374151;
        min-width: 120px;
        font-size: 14px;
    }
    
    .progress-wrapper {
        flex: 1;
        background: #e5e7eb;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: #3b82f6;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    .distribution-value {
        font-weight: 700;
        color: #6b7280;
        min-width: 90px;
        text-align: right;
        font-size: 14px;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: white !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }
    
    .stFileUploader:hover {
        border-color: #3b82f6 !important;
    }
    
    .stFileUploader label {
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Select Box */
    .stSelectbox label {
        color: #111827 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Checkbox */
    .stCheckbox {
        background: white;
        padding: 0.75rem 1rem !important;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .stCheckbox:hover {
        border-color: #3b82f6;
        background: #f0f9ff;
    }
    
    .stCheckbox label {
        font-weight: 600 !important;
        color: #374151 !important;
        font-size: 14px !important;
    }
    
    /* Process Button Container */
    .process-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .process-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .process-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Action Buttons */
    .action-btn-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    /* Download Section */
    .download-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1rem !important;
        }
        
        .header {
            padding: 1.5rem;
        }
        
        .header-title {
            font-size: 24px;
        }
        
        .card {
            padding: 1.5rem;
        }
        
        .stats-container {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .action-btn-grid {
            grid-template-columns: 1fr;
        }
        
        .category-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

class MultiColumnDetector:
    def __init__(self):
        self.categories = {
            'Fans': {
                'keywords': ['fan', 'ventilator', 'blower', 'exhaust', 'ventilation', 'air circulator', 
                           'cooling fan', 'pedestal', 'tower fan', 'ceiling fan', 'table fan', 'wall fan', 
                           'stand fan', 'industrial fan', 'oscillating'],
                'exclude': ['light', 'lamp', 'bulb', 'led', 'fixture', 'lighting', 'illumination']
            },
            'Lighting': {
                'keywords': ['light', 'lamp', 'bulb', 'lighting', 'led', 'fixture', 'chandelier', 
                           'luminaire', 'illumination', 'lantern', 'sconce', 'pendant', 'downlight', 
                           'spotlight', 'track light', 'ceiling light', 'wall light', 'floor lamp', 
                           'table lamp', 'desk lamp'],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling']
            },
            'Furniture': {
                'keywords': ['chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch', 'bed', 
                           'furniture', 'wardrobe', 'dresser', 'bookcase', 'stool', 'bench', 'ottoman'],
                'exclude': []
            },
            'Decor': {
                'keywords': ['decor', 'decoration', 'vase', 'mirror', 'sculpture', 'cushion', 'rug', 
                           'carpet', 'curtain', 'decorative', 'ornament'],
                'exclude': []
            },
            'Electronics': {
                'keywords': ['tv', 'television', 'monitor', 'speaker', 'computer', 'laptop', 'printer', 
                           'electronic', 'router'],
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
            text_clean = text_clean.replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('_', ' ')
            
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
                sheets.append({
                    'name': name, 
                    'rows': sheet.max_row or 0, 
                    'cols': sheet.max_column or 0
                })
            except:
                continue
        wb.close()
        return sheets
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        return []

def process_with_multi_column(file, sheet_name, detector, enabled_categories):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        
        if df.empty:
            return {}, {
                'total_rows': 0, 
                'well_matched': 0, 
                'forced_matched': 0, 
                'categories_found': 0, 
                'distribution': {}, 
                'forced_assignments': []
            }
        
        priority_cols, secondary_cols = detector.find_relevant_columns(df)
        
        df['Detected_Category'] = None
        df['Match_Score'] = 0
        df['Source_Column'] = ""
        
        for idx in df.index:
            try:
                row = df.loc[idx]
                cat, score, source = detector.smart_multi_column_detect(
                    row, priority_cols, secondary_cols, enabled_categories
                )
                
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
                    
                    forced_assignments.append({
                        'item': item_name, 
                        'assigned_to': forced_cat
                    })
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
        st.error(f"❌ Error processing: {str(e)}")
        return {}, {
            'total_rows': 0, 
            'well_matched': 0, 
            'forced_matched': 0, 
            'categories_found': 0, 
            'distribution': {}, 
            'forced_assignments': []
        }

def create_excel(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            wb = writer.book
            ws = writer.sheets['Data']
            
            header_fill = PatternFill(start_color='667eea', end_color='667eea', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True, size=11)
            header_alignment = Alignment(horizontal='center', vertical='center')
            
            thin_border = Border(
                left=Side(style='thin', color='E2E8F0'),
                right=Side(style='thin', color='E2E8F0'),
                top=Side(style='thin', color='E2E8F0'),
                bottom=Side(style='thin', color='E2E8F0')
            )
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = thin_border
            
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical='center')
            
            for col in ws.columns:
                max_len = 10
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_len:
                            max_len = len(str(cell.value))
                    except:
                        pass
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 50)
        
        output.seek(0)
        return output.getvalue()
    except:
        return None

def main():
    # Header
    st.markdown('''
    <div class="header">
        <div class="header-title">📊 Data Separation Tool</div>
        <div class="header-subtitle">Automatically organize and categorize your Excel data into separate files</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = MultiColumnDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    
    # Upload Section
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📁 Upload File</div>', unsafe_allow_html=True)
        
        uploaded = st.file_uploader(
            "Choose Excel file", 
            type=['xlsx', 'xlsm', 'xls'],
            label_visibility="collapsed"
        )
        
        if uploaded:
            st.markdown('<div class="success-message">✓ File uploaded successfully</div>', unsafe_allow_html=True)
            
            sheets = get_sheet_info(uploaded)
            if sheets:
                sheet_options = [f"{s['name']} ({s['rows']} rows, {s['cols']} columns)" for s in sheets]
                
                selected_sheet = st.selectbox(
                    "Select Sheet",
                    sheet_options
                )
                
                st.session_state.sheet = sheets[sheet_options.index(selected_sheet)]['name']
                st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        all_cats = list(st.session_state.detector.categories.keys())
        
        st.markdown('<div class="action-btn-grid">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Select All", use_container_width=True, key="select_all"):
            st.session_state.selected_cats = all_cats.copy()
            st.rerun()
        
        if st.button("Clear All", use_container_width=True, key="clear_all"):
            st.session_state.selected_cats = []
            st.rerun()
        
        if st.button("Reset Default", use_container_width=True, key="reset_cats"):
            st.session_state.selected_cats = ['Lighting', 'Fans']
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Category Selection
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">🎯 Select Categories</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-message">Choose which product categories to detect in your data</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="category-grid">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    selected = []
    for idx, cat in enumerate(all_cats):
        with cols[idx % 4]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"cat_{cat}"):
                selected.append(cat)
    
    st.session_state.selected_cats = selected
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process Button
    if uploaded and st.session_state.selected_cats:
        st.markdown(f'''
        <div class="process-container">
            <div class="process-title">Ready to Process</div>
            <div class="process-subtitle">
                {len(st.session_state.selected_cats)} categories selected | File: {st.session_state.filename} | Sheet: {st.session_state.sheet}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("Process Data", type="primary", use_container_width=True, key="process_btn"):
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
                st.error(f"Error: {str(e)}")
    
    # Results Section
    if st.session_state.processed and st.session_state.stats:
        stats = st.session_state.stats
        
        # Statistics Cards
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{stats["total_rows"]}</div>
            <div class="stat-label">Total Records</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{stats["well_matched"]}</div>
            <div class="stat-label">Well Matched</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{stats["forced_matched"]}</div>
            <div class="stat-label">Auto Assigned</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{stats["categories_found"]}</div>
            <div class="stat-label">Output Files</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Key Columns Info
        if stats.get('priority_cols'):
            priority_text = ", ".join(stats["priority_cols"][:3])
            st.markdown(f'<div class="info-message">🔍 Key columns detected: {priority_text}</div>', unsafe_allow_html=True)
        
        # Distribution
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📈 Category Distribution</div>', unsafe_allow_html=True)
        
        total = stats['total_rows']
        for cat, count in sorted(stats.get('distribution', {}).items(), key=lambda x: x[1], reverse=True):
            if cat:
                pct = (count / total * 100) if total > 0 else 0
                
                st.markdown(f'''
                <div class="distribution-item">
                    <div class="distribution-label">{cat}</div>
                    <div class="progress-wrapper">
                        <div class="progress-fill" style="width: {pct}%"></div>
                    </div>
                    <div class="distribution-value">{count} ({pct:.1f}%)</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">💾 Download Files</div>', unsafe_allow_html=True)
        st.markdown('<div class="success-message">✓ Data separated successfully - ready for download</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="download-grid">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        download_cols = st.columns(2)
        for idx, (cat, data) in enumerate(sorted(st.session_state.processed.items())):
            with download_cols[idx % 2]:
                filename = f"{st.session_state.filename}_{cat}.xlsx"
                excel_data = create_excel(data)
                if excel_data:
                    st.download_button(
                        f"{cat} • {len(data)} records",
                        excel_data,
                        filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"download_{cat}"
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
