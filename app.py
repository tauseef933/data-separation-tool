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
    .category-badge {display: inline-block; background: #2a5298; color: white; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; margin: 0.3rem;}
</style>
""", unsafe_allow_html=True)

class CategoryDetector:
    def __init__(self):
        self.categories = {
            'Lighting': ['light', 'lamp', 'chandelier', 'fixture', 'bulb', 'sconce', 'pendant', 'lantern', 'led', 'fluorescent', 'halogen', 'spotlight', 'floodlight', 'downlight', 'track light', 'recessed', 'table lamp', 'floor lamp', 'desk lamp', 'wall light', 'ceiling light', 'strip light', 'tube light'],
            'Fans': ['fan', 'ceiling fan', 'exhaust', 'ventilator', 'blower', 'pedestal fan', 'table fan', 'wall fan', 'tower fan', 'stand fan', 'portable fan', 'oscillating fan', 'cooling fan', 'air circulator', 'extractor fan', 'industrial fan'],
            'Furniture': ['chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch', 'bed', 'dresser', 'wardrobe', 'bookcase', 'stool', 'bench', 'ottoman', 'sectional', 'loveseat', 'recliner', 'armchair', 'dining table', 'coffee table', 'nightstand', 'credenza', 'buffet', 'console', 'vanity', 'armoire', 'filing cabinet', 'storage unit', 'media center', 'tv stand', 'computer desk', 'office chair', 'workstation'],
            'Decor': ['decor', 'decoration', 'ornament', 'vase', 'picture frame', 'mirror', 'wall art', 'sculpture', 'statue', 'figurine', 'candle holder', 'plant pot', 'planter', 'centerpiece', 'tapestry', 'wall hanging', 'clock', 'throw pillow', 'cushion', 'rug', 'carpet', 'mat', 'curtain', 'drape', 'blind', 'wreath', 'basket', 'tray', 'bowl'],
            'Electronics': ['electronic', 'device', 'gadget', 'appliance', 'tv', 'television', 'monitor', 'speaker', 'audio', 'video', 'phone', 'tablet', 'computer', 'laptop', 'printer', 'scanner', 'router', 'camera', 'projector'],
            'Kitchen': ['kitchen', 'cookware', 'utensil', 'pot', 'pan', 'plate', 'bowl', 'cup', 'glass', 'cutlery', 'knife', 'fork', 'spoon', 'microwave', 'oven', 'stove', 'refrigerator', 'blender', 'mixer', 'toaster', 'kettle'],
            'Bathroom': ['bathroom', 'toilet', 'sink', 'faucet', 'shower', 'bathtub', 'vanity', 'medicine cabinet', 'towel rack', 'soap dispenser', 'bath mat', 'shower curtain'],
            'Outdoor': ['outdoor', 'patio', 'garden', 'lawn', 'deck', 'balcony', 'gazebo', 'pergola', 'umbrella', 'grill', 'bbq', 'outdoor furniture', 'hammock', 'swing', 'fire pit']
        }
    
    def detect_category(self, text):
        if pd.isna(text):
            return 'Uncategorized'
        text_lower = str(text).lower()
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        return max(category_scores, key=category_scores.get) if category_scores else 'Uncategorized'

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

def process_file(file, sheet_name, detector):
    df = pd.read_excel(file, sheet_name=sheet_name)
    df['Detected_Category'] = 'Uncategorized'
    
    category_cols = [col for col in df.columns if any(kw in str(col).lower() for kw in ['type', 'category', 'description', 'item', 'product', 'name'])]
    
    for idx, row in df.iterrows():
        found = False
        for col in category_cols:
            cat = detector.detect_category(row[col])
            if cat != 'Uncategorized':
                df.at[idx, 'Detected_Category'] = cat
                found = True
                break
        
        if not found:
            for col in df.columns:
                if df[col].dtype == 'object':
                    cat = detector.detect_category(row[col])
                    if cat != 'Uncategorized':
                        df.at[idx, 'Detected_Category'] = cat
                        break
    
    separated = {}
    for category in df['Detected_Category'].unique():
        separated[category] = df[df['Detected_Category'] == category].drop('Detected_Category', axis=1)
    
    stats = {
        'total_rows': len(df),
        'categories_found': len(separated),
        'distribution': df['Detected_Category'].value_counts().to_dict(),
        'uncategorized': len(df[df['Detected_Category'] == 'Uncategorized'])
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
    st.markdown('<div class="header-box"><h1 class="header-title">Data Separation Tool</h1><p class="header-subtitle">Intelligent Excel data categorization system</p></div>', unsafe_allow_html=True)
    
    if 'detector' not in st.session_state:
        st.session_state.detector = CategoryDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card"><h3 class="card-title">Upload Excel File</h3>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Select your Excel file", type=['xlsx', 'xlsm', 'xls'])
        
        if uploaded:
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
            st.markdown('<div class="info-box">File loaded successfully</div>', unsafe_allow_html=True)
            
            sheets = get_sheet_info(uploaded)
            if sheets:
                sheet_options = [f"{s['name']} ({s['rows']} rows × {s['cols']} cols)" for s in sheets]
                selected = st.selectbox("Select sheet", sheet_options)
                sheet_name = sheets[sheet_options.index(selected)]['name']
                
                if st.button("Process Data", type="primary"):
                    with st.spinner('Processing...'):
                        uploaded.seek(0)
                        progress = st.progress(0)
                        progress.progress(30)
                        separated, stats = process_file(uploaded, sheet_name, st.session_state.detector)
                        progress.progress(70)
                        st.session_state.processed = separated
                        st.session_state.stats = stats
                        progress.progress(100)
                    st.markdown('<div class="success-box">Processing complete!</div>', unsafe_allow_html=True)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><h3 class="card-title">Categories</h3>', unsafe_allow_html=True)
        badges = "".join([f'<span class="category-badge">{cat}</span>' for cat in st.session_state.detector.categories.keys()])
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.processed:
        st.markdown("---")
        st.markdown('<div class="card"><h3 class="card-title">Results</h3>', unsafe_allow_html=True)
        stats = st.session_state.stats
        
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]:,}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["categories_found"]}</div><div class="stat-label">Categories</div></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["uncategorized"]:,}</div><div class="stat-label">Uncategorized</div></div>', unsafe_allow_html=True)
        
        if stats['uncategorized'] > 0:
            st.markdown(f'<div class="warning-box"><strong>Note:</strong> {stats["uncategorized"]} rows could not be categorized.</div>', unsafe_allow_html=True)
        
        st.markdown("### Download Files")
        dl_cols = st.columns(min(len(st.session_state.processed), 3))
        for idx, (cat, data) in enumerate(st.session_state.processed.items()):
            with dl_cols[idx % 3]:
                filename = f"{st.session_state.filename}_{cat}.xlsx"
                excel = create_excel(data)
                st.download_button(f"{cat} ({len(data)})", excel, filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
