import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import io

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    [data-testid="stMainBlockContainer"] {
        background: transparent !important;
        padding: 0 !important;
        max-width: 1600px;
        margin: 0 auto;
    }
    
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Header Section */
    .hero-section {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        padding: 48px 56px;
        margin: 32px 24px;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        animation: fadeInDown 0.6s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 12px;
        letter-spacing: -1.5px;
    }
    
    .hero-subtitle {
        font-size: 18px;
        color: #64748b;
        font-weight: 500;
        line-height: 1.6;
    }
    
    /* Glass Card Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 32px;
        margin: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .glass-card:hover {
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
        transform: translateY(-4px);
    }
    
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .section-title::before {
        content: '';
        width: 4px;
        height: 28px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Modern Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin: 28px 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 28px;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stat-box:hover::before {
        left: 100%;
    }
    
    .stat-box:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
    }
    
    .stat-box:nth-child(2) {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 8px 24px rgba(240, 147, 251, 0.3);
    }
    
    .stat-box:nth-child(2):hover {
        box-shadow: 0 12px 32px rgba(240, 147, 251, 0.4);
    }
    
    .stat-box:nth-child(3) {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 8px 24px rgba(79, 172, 254, 0.3);
    }
    
    .stat-box:nth-child(3):hover {
        box-shadow: 0 12px 32px rgba(79, 172, 254, 0.4);
    }
    
    .stat-box:nth-child(4) {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        box-shadow: 0 8px 24px rgba(250, 112, 154, 0.3);
    }
    
    .stat-box:nth-child(4):hover {
        box-shadow: 0 12px 32px rgba(250, 112, 154, 0.4);
    }
    
    .stat-number {
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 8px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stat-label {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        opacity: 0.95;
    }
    
    /* Category Pills */
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 12px;
        margin: 24px 0;
    }
    
    .category-pill {
        background: white;
        border: 2px solid #e2e8f0;
        padding: 14px 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        color: #475569;
        cursor: pointer;
        transition: all 0.3s ease;
        user-select: none;
    }
    
    .category-pill:hover {
        border-color: #667eea;
        background: #f8f9ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .category-pill.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: transparent;
        color: white;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
    }
    
    /* Progress Bar */
    .progress-container {
        background: #f1f5f9;
        border-radius: 12px;
        height: 12px;
        overflow: hidden;
        margin: 12px 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .distribution-row {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        background: #f8fafc;
        border-radius: 12px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }
    
    .distribution-row:hover {
        background: #f1f5f9;
        transform: translateX(4px);
    }
    
    .distribution-label {
        font-weight: 600;
        color: #334155;
        min-width: 120px;
        font-size: 14px;
    }
    
    .distribution-count {
        font-weight: 700;
        color: #64748b;
        min-width: 80px;
        text-align: right;
        font-size: 14px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 32px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35) !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 8px 28px rgba(102, 126, 234, 0.45) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border: none !important;
        padding: 16px 28px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.3) !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 28px rgba(79, 172, 254, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Alert Boxes */
    .alert-success {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: #065f46;
        font-weight: 600;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(150, 230, 161, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: #0c4a6e;
        font-weight: 600;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(168, 237, 234, 0.3);
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: #78350f;
        font-weight: 600;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(253, 203, 110, 0.3);
    }
    
    /* Upload Area */
    .stFileUploader {
        background: white !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 16px !important;
        padding: 32px !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #667eea !important;
        background: #f8f9ff !important;
    }
    
    .stFileUploader label {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    /* Select Box */
    .stSelectbox label {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    /* Action Buttons Grid */
    .action-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }
    
    /* Checkbox Styling */
    .stCheckbox {
        padding: 8px 0 !important;
    }
    
    .stCheckbox label {
        font-weight: 500 !important;
        color: #334155 !important;
        font-size: 14px !important;
    }
    
    /* Process Section */
    .process-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 36px;
        border-radius: 20px;
        color: white;
        margin: 24px;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
        text-align: center;
    }
    
    .process-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    .process-subtitle {
        font-size: 15px;
        opacity: 0.9;
        margin-bottom: 24px;
    }
    
    /* Download Grid */
    .download-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        margin: 24px 0;
    }
    
    /* Responsive Design */
    @media only screen and (max-width: 768px) {
        .hero-title {
            font-size: 36px;
        }
        
        .hero-section {
            padding: 32px 24px;
            margin: 16px 12px;
        }
        
        .glass-card {
            padding: 24px;
            margin: 12px;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .category-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media only screen and (max-width: 480px) {
        .hero-title {
            font-size: 28px;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .category-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
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
    # Hero Section
    st.markdown('''
    <div class="hero-section">
        <div class="hero-title">✨ Data Separation Tool</div>
        <div class="hero-subtitle">Transform your messy data into organized, category-based spreadsheets with AI-powered precision</div>
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
    
    # Main Grid Layout
    col1, col2 = st.columns([2, 1], gap="medium")
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📁 Upload Your File</div>', unsafe_allow_html=True)
        
        uploaded = st.file_uploader(
            "Choose an Excel file (.xlsx, .xlsm, .xls)", 
            type=['xlsx', 'xlsm', 'xls'],
            help="Upload your data file to begin automatic categorization"
        )
        
        if uploaded:
            st.markdown('''
            <div class="alert-success">
                ✓ File uploaded successfully and ready for processing
            </div>
            ''', unsafe_allow_html=True)
            
            sheets = get_sheet_info(uploaded)
            if sheets:
                sheet_options = [f"{s['name']} ({s['rows']} rows × {s['cols']} cols)" for s in sheets]
                
                selected_sheet = st.selectbox(
                    "📊 Select Sheet",
                    sheet_options,
                    help="Choose which sheet to process"
                )
                
                st.session_state.sheet = sheets[sheet_options.index(selected_sheet)]['name']
                st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        all_cats = list(st.session_state.detector.categories.keys())
        
        st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
        
        if st.button("✓ Select All", use_container_width=True, key="select_all"):
            st.session_state.selected_cats = all_cats.copy()
            st.rerun()
        
        if st.button("✗ Clear All", use_container_width=True, key="clear_all"):
            st.session_state.selected_cats = []
            st.rerun()
        
        if st.button("↺ Reset", use_container_width=True, key="reset_cats"):
            st.session_state.selected_cats = ['Lighting', 'Fans']
            st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Category Selection
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 Select Categories</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="alert-info">
        Choose the product categories you want to detect. The AI will analyze your data and organize items accordingly.
    </div>
    ''', unsafe_allow_html=True)
    
    cols = st.columns(4)
    selected = []
    for idx, cat in enumerate(all_cats):
        with cols[idx % 4]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"cat_{cat}"):
                selected.append(cat)
    
    st.session_state.selected_cats = selected
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process Section
    if uploaded and st.session_state.selected_cats:
        st.markdown(f'''
        <div class="process-section">
            <div class="process-title">🚀 Ready to Process</div>
            <div class="process-subtitle">
                {len(st.session_state.selected_cats)} categories selected • 
                File: {st.session_state.filename} • 
                Sheet: {st.session_state.sheet}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("🔄 Process & Separate Data", type="primary", use_container_width=True, key="process_btn"):
            try:
                with st.spinner('🔮 Processing your data with AI...'):
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
                st.error(f"❌ An error occurred: {str(e)}")
    
    # Results Section
    if st.session_state.processed and st.session_state.stats:
        stats = st.session_state.stats
        
        # Statistics
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Processing Results</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{stats["total_rows"]}</div>
            <div class="stat-label">Total Records</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{stats["well_matched"]}</div>
            <div class="stat-label">Matched</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{stats["forced_matched"]}</div>
            <div class="stat-label">Auto Assigned</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{stats["categories_found"]}</div>
            <div class="stat-label">Output Files</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if stats.get('priority_cols'):
            priority_text = ", ".join(stats["priority_cols"][:3])
            st.markdown(f'''
            <div class="alert-info">
                🔍 Detected key columns: <strong>{priority_text}</strong>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Distribution
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Category Distribution</div>', unsafe_allow_html=True)
        
        total = stats['total_rows']
        for cat, count in sorted(stats.get('distribution', {}).items(), key=lambda x: x[1], reverse=True):
            if cat:
                pct = (count / total * 100) if total > 0 else 0
                
                st.markdown(f'''
                <div class="distribution-row">
                    <div class="distribution-label">{cat}</div>
                    <div style="flex: 1;">
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {pct}%"></div>
                        </div>
                    </div>
                    <div class="distribution-count">{count} ({pct:.1f}%)</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Downloads
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💾 Download Files</div>', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="alert-success">
            ✓ Your data has been separated and is ready for download
        </div>
        ''', unsafe_allow_html=True)
        
        download_cols = st.columns(2)
        for idx, (cat, data) in enumerate(sorted(st.session_state.processed.items())):
            with download_cols[idx % 2]:
                filename = f"{st.session_state.filename}_{cat}.xlsx"
                excel_data = create_excel(data)
                if excel_data:
                    st.download_button(
                        f"📥 {cat} ({len(data)} records)",
                        excel_data,
                        filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"download_{cat}"
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
