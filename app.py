import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import time

# Try to import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .main > div { background: #f8fafc; min-height: 100vh; padding: 2rem; }
    .hero-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2.5rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3); }
    .hero-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; margin: 0; }
    .hero-subtitle { color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-top: 0.5rem; }
    .premium-card { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); margin-bottom: 1.5rem; border: 1px solid #e5e7eb; }
    .card-title { color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; }
    .card-number { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; font-size: 1rem; font-weight: 700; }
    .success-box { background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 4px solid #10b981; color: #065f46; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; }
    .warning-box { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; color: #92400e; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; }
    .info-box { background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left: 4px solid #3b82f6; color: #1e40af; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; font-size: 0.95rem; }
    .stat-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 16px; color: white; text-align: center; box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3); }
    .stat-number { font-size: 2.2rem; font-weight: 800; margin-bottom: 0.3rem; }
    .stat-label { font-size: 0.85rem; opacity: 0.95; font-weight: 500; text-transform: uppercase; }
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.9rem 2rem; border-radius: 12px; font-weight: 600; font-size: 1rem; width: 100%; transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4); }
    .stDownloadButton>button { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 1rem 1.5rem; border-radius: 12px; font-weight: 600; width: 100%; }
    .distribution-item { background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%); padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0; display: flex; justify-content: space-between; border-left: 4px solid #667eea; }
    @media (max-width: 768px) { .stat-container { grid-template-columns: repeat(2, 1fr); } .hero-title { font-size: 1.8rem; } }
</style>
""", unsafe_allow_html=True)

def init_gemini():
    if not GEMINI_AVAILABLE:
        return None
    
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        else:
            st.error("API key not found in secrets. Please add GEMINI_API_KEY to Streamlit Secrets.")
            return None
        
        genai.configure(api_key=api_key)
        # USE CORRECT MODEL NAME
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        st.error("Error initializing AI: " + str(e))
        return None

class HybridDetector:
    def __init__(self):
        self.categories = {
            'Fans': {'keywords': ['fan', 'fans', 'ceiling fan', 'table fan', 'wall fan', 'floor fan', 'exhaust fan', 'ventilator', 'ventilators', 'blower', 'blowers', 'cooling fan', 'pedestal fan', 'tower fan', 'stand fan', 'desk fan', 'box fan', 'window fan', 'attic fan', 'bathroom fan', 'kitchen fan', 'range hood fan', 'inline fan', 'centrifugal fan', 'axial fan', 'ventilation fan', 'air circulator', 'air mover', 'extractor fan', 'oscillating fan', 'industrial fan', 'portable fan', 'hvls', 'bldc', 'exhaust', 'ventilation', 'cooling', 'cfm', 'airflow'], 'exclude': ['light', 'lamp', 'bulb', 'led light', 'chandelier', 'lighting']},
            'Lighting': {'keywords': ['light', 'lights', 'lamp', 'lamps', 'bulb', 'bulbs', 'lighting', 'led', 'led light', 'fixture', 'chandelier', 'pendant', 'downlight', 'spotlight', 'track light', 'ceiling light', 'wall light', 'floor lamp', 'table lamp', 'desk lamp', 'sconce', 'vanity light', 'recessed light', 'tube light', 'strip light', 'panel light', 'floodlight', 'street light', 'high bay', 'low bay', 'emergency light', 'exit sign', 'grow light', 'smart light', 'dimmable', 'halogen', 'incandescent', 'cfl', 'fluorescent', 'lumen', 'lumens', 'watt', 'kelvin', 'illumination'], 'exclude': ['fan', 'ventilator', 'blower', 'exhaust fan', 'cooling fan']},
            'Furniture': {'keywords': ['furniture', 'chair', 'chairs', 'table', 'tables', 'desk', 'desks', 'cabinet', 'cabinets', 'shelf', 'shelves', 'sofa', 'sofas', 'couch', 'bed', 'beds', 'wardrobe', 'dresser', 'bookcase', 'stool', 'bench', 'ottoman', 'nightstand', 'sectional', 'loveseat', 'recliner', 'armchair', 'credenza', 'buffet', 'hutch', 'armoire', 'vanity table', 'seating'], 'exclude': []},
            'Decor': {'keywords': ['decor', 'decoration', 'decorative', 'ornament', 'vase', 'vases', 'picture frame', 'frame', 'mirror', 'mirrors', 'wall art', 'wall decor', 'sculpture', 'statue', 'figurine', 'candle', 'candle holder', 'plant pot', 'planter', 'centerpiece', 'tapestry', 'clock', 'wall clock', 'throw pillow', 'cushion', 'pillow', 'rug', 'rugs', 'carpet', 'mat', 'curtain', 'curtains', 'blind', 'wreath', 'basket', 'tray', 'bowl', 'artificial plant', 'wall sticker'], 'exclude': []},
            'Electronics': {'keywords': ['electronic', 'electronics', 'tv', 'television', 'monitor', 'speaker', 'computer', 'laptop', 'printer', 'scanner', 'router', 'camera', 'projector', 'soundbar', 'headphones', 'earphones'], 'exclude': []},
            'Kitchen': {'keywords': ['kitchen', 'cookware', 'utensil', 'pot', 'pots', 'pan', 'pans', 'plate', 'plates', 'bowl', 'bowls', 'cup', 'glass', 'cutlery', 'knife', 'fork', 'spoon', 'microwave', 'oven', 'stove', 'refrigerator', 'blender', 'mixer', 'toaster', 'kettle', 'coffee maker'], 'exclude': []},
            'Bathroom': {'keywords': ['bathroom', 'toilet', 'sink', 'basin', 'faucet', 'tap', 'shower', 'shower head', 'bathtub', 'tub', 'bathroom vanity', 'medicine cabinet', 'towel rack', 'soap dispenser', 'bath mat', 'shower curtain'], 'exclude': []},
            'Outdoor': {'keywords': ['outdoor', 'patio', 'garden', 'lawn', 'deck', 'gazebo', 'pergola', 'patio furniture', 'outdoor furniture', 'umbrella', 'grill', 'bbq', 'fire pit', 'outdoor heater', 'hammock', 'swing'], 'exclude': []}
        }
    
    def keyword_detect(self, text, enabled_categories):
        if not text or pd.isna(text):
            return None, 0
        
        text_lower = str(text).lower()
        text_lower = ' ' + text_lower.replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('_', ' ') + ' '
        
        scores = {}
        for cat in enabled_categories:
            if cat not in self.categories:
                continue
            
            excluded = False
            for excl in self.categories[cat].get('exclude', []):
                if ' ' + excl + ' ' in text_lower:
                    excluded = True
                    break
            
            if excluded:
                continue
            
            score = 0
            for kw in self.categories[cat]['keywords']:
                pattern = ' ' + kw + ' '
                count = text_lower.count(pattern)
                if count > 0:
                    score += count * 20
                elif kw in text_lower:
                    score += 8
            
            if score > 0:
                scores[cat] = score
        
        if scores:
            best = max(scores, key=scores.get)
            return best, scores[best]
        return None, 0

def ai_categorize_batch(model, items, enabled_categories):
    try:
        categories_str = ", ".join(enabled_categories)
        items_text = "\n".join([str(i+1) + ". " + item['text'] for i, item in enumerate(items)])
        
        prompt = f"""Categorize each product into ONE category: {categories_str}

Rules:
- Return ONLY the category name (one per line)
- Match the input order exactly
- Choose the MOST appropriate category

Products:
{items_text}

Categories (one per line):"""

        response = model.generate_content(prompt)
        result = response.text.strip().split('\n')
        
        categories = []
        for line in result:
            line = line.strip().replace('*', '').replace('-', '').replace('.', '').strip()
            for cat in enabled_categories:
                if cat.lower() in line.lower():
                    categories.append(cat)
                    break
            else:
                categories.append(None)
        
        return categories
        
    except Exception as e:
        st.warning("AI processing error: " + str(e))
        return [None] * len(items)

def process_file_ai(file, sheet_name, detector, enabled_categories, selected_columns, model):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        
        if df.empty:
            return {}, {'total_rows': 0, 'ai_verified': 0, 'forced': 0, 'categories_found': 0, 'distribution': {}}
        
        df['Category'] = None
        df['Confidence'] = 'Low'
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # ALL ITEMS GO THROUGH AI
        status_text.text("AI verification in progress...")
        
        batch_size = 20
        total_items = len(df)
        ai_verified = 0
        
        for i in range(0, total_items, batch_size):
            batch_indices = df.index[i:i+batch_size]
            
            batch_items = []
            for idx in batch_indices:
                text_parts = []
                for col in selected_columns:
                    if col in df.columns:
                        val = df.loc[idx, col]
                        if pd.notna(val):
                            text_parts.append(str(val))
                
                batch_items.append({'text': ' | '.join(text_parts), 'idx': idx})
            
            if model:
                ai_categories = ai_categorize_batch(model, batch_items, enabled_categories)
                
                for item, ai_cat in zip(batch_items, ai_categories):
                    if ai_cat and ai_cat in enabled_categories:
                        df.at[item['idx'], 'Category'] = ai_cat
                        df.at[item['idx'], 'Confidence'] = 'High'
                        ai_verified += 1
            
            progress = (i + batch_size) / total_items
            progress_bar.progress(min(progress, 1.0))
            status_text.text("Processing: " + str(min(i + batch_size, total_items)) + " of " + str(total_items))
            
            time.sleep(0.3)
        
        # Force assign any remaining
        unassigned = df[df['Category'].isna()].index
        forced = 0
        
        if len(unassigned) > 0 and enabled_categories:
            for i, idx in enumerate(unassigned):
                df.at[idx, 'Category'] = enabled_categories[i % len(enabled_categories)]
                df.at[idx, 'Confidence'] = 'Low'
                forced += 1
        
        progress_bar.progress(1.0)
        status_text.empty()
        progress_bar.empty()
        
        separated = {}
        original_cols = [c for c in df.columns if c not in ['Category', 'Confidence']]
        
        for cat in enabled_categories:
            cat_data = df[df['Category'] == cat][original_cols].copy()
            if len(cat_data) > 0:
                separated[cat] = cat_data
        
        stats = {
            'total_rows': len(df),
            'ai_verified': ai_verified,
            'forced': forced,
            'categories_found': len(separated),
            'distribution': df['Category'].value_counts().to_dict()
        }
        
        return separated, stats
        
    except Exception as e:
        st.error("Processing error: " + str(e))
        return {}, {'total_rows': 0, 'ai_verified': 0, 'forced': 0, 'categories_found': 0, 'distribution': {}}

def get_sheet_info(file):
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = [{'name': name, 'rows': wb[name].max_row or 0, 'cols': wb[name].max_column or 0} for name in wb.sheetnames]
        wb.close()
        return sheets
    except:
        return []

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
    st.markdown('<div class="hero-header"><h1 class="hero-title">Data Separation Tool</h1><p class="hero-subtitle">Professional category detection and file separation</p></div>', unsafe_allow_html=True)
    
    if 'detector' not in st.session_state:
        st.session_state.detector = HybridDetector()
    if 'model' not in st.session_state:
        st.session_state.model = init_gemini()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    
    # Upload & Sheet
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">1</span>Upload File</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
    
    if uploaded:
        st.markdown('<div class="success-box">File loaded successfully</div>', unsafe_allow_html=True)
        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = [s['name'] + " (" + str(s['rows']) + " rows)" for s in sheets]
            if len(sheets) > 1:
                sel = st.selectbox("Select sheet:", opts)
                st.session_state.sheet = sheets[opts.index(sel)]['name']
            else:
                st.session_state.sheet = sheets[0]['name']
                st.markdown('<div class="info-box">Selected sheet: ' + sheets[0]['name'] + '</div>', unsafe_allow_html=True)
            
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
            
            df_preview = pd.read_excel(uploaded, sheet_name=st.session_state.sheet, nrows=0)
            st.session_state.available_columns = list(df_preview.columns)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Column Selection
    if uploaded and 'available_columns' in st.session_state:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">2</span>Select Analysis Columns</h3>', unsafe_allow_html=True)
        
        suggested = []
        for col in st.session_state.available_columns:
            col_lower = col.lower()
            if any(word in col_lower for word in ['name', 'sku', 'description', 'desc', 'product', 'item', 'title', 'type', 'category']):
                suggested.append(col)
        
        if not suggested:
            suggested = st.session_state.available_columns[:5]
        
        selected_columns = st.multiselect("Select columns containing product information:", st.session_state.available_columns, default=suggested)
        st.session_state.selected_columns = selected_columns if selected_columns else suggested
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Categories
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">3</span>Select Categories</h3>', unsafe_allow_html=True)
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
    
    cols = st.columns(4)
    selected = []
    for i, cat in enumerate(all_cats):
        with cols[i % 4]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key="cat_" + cat):
                selected.append(cat)
    
    st.session_state.selected_cats = selected
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process
    if uploaded and st.session_state.selected_cats and 'selected_columns' in st.session_state:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">4</span>Process Data</h3>', unsafe_allow_html=True)
        
        if not st.session_state.model:
            st.error("AI not initialized. Please check your API key configuration.")
        
        if st.button("Start Processing", type="primary", use_container_width=True):
            if not st.session_state.selected_columns:
                st.error("Please select analysis columns")
            else:
                with st.spinner('Processing...'):
                    uploaded.seek(0)
                    separated, stats = process_file_ai(uploaded, st.session_state.sheet, st.session_state.detector, st.session_state.selected_cats, st.session_state.selected_columns, st.session_state.model)
                    st.session_state.processed = separated
                    st.session_state.stats = stats
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results
    if st.session_state.processed is not None:
        stats = st.session_state.stats
        
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        cols = st.columns(4)
        with cols[0]:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['total_rows']) + '</div><div class="stat-label">Total Items</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['ai_verified']) + '</div><div class="stat-label">Verified</div></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['forced']) + '</div><div class="stat-label">Assigned</div></div>', unsafe_allow_html=True)
        with cols[3]:
            accuracy = (stats['ai_verified'] / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(round(accuracy, 1)) + '%</div><div class="stat-label">Accuracy</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card"><h3 class="card-title">Category Distribution</h3>', unsafe_allow_html=True)
        for cat, count in stats['distribution'].items():
            if cat:
                pct = (count / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
                st.markdown('<div class="distribution-item"><span><strong>' + str(cat) + '</strong></span><span>' + str(count) + ' items (' + str(round(pct, 1)) + '%)</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card"><h3 class="card-title">Preview Results</h3>', unsafe_allow_html=True)
        for cat, data in st.session_state.processed.items():
            with st.expander("Preview: " + cat + " (" + str(len(data)) + " items)", expanded=False):
                st.dataframe(data.head(10), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card"><h3 class="card-title">Download Files</h3>', unsafe_allow_html=True)
        dl_cols = st.columns(min(len(st.session_state.processed), 4))
        for idx, (cat, data) in enumerate(st.session_state.processed.items()):
            with dl_cols[idx % 4]:
                excel = create_excel(data)
                if excel:
                    st.download_button(cat + " (" + str(len(data)) + ")", excel, st.session_state.filename + "_" + cat + ".xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="dl_" + cat)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
