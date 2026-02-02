import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); padding: 1rem;}
    .header-box {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1.2rem 1.5rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 8px 30px rgba(0,0,0,0.12);}
    .header-title {color: #ffffff; font-size: 1.5rem; font-weight: 700; margin: 0; line-height: 1.3;}
    .header-subtitle {color: #b8d4f1; font-size: 0.8rem; margin-top: 0.3rem;}
    .card {background: #ffffff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 0.8rem;}
    .card-title {color: #1a1a1a; font-size: 1rem; font-weight: 600; margin-bottom: 0.6rem; border-bottom: 2px solid #2a5298; padding-bottom: 0.4rem;}
    .info-box {background: #e3f2fd; border-left: 3px solid #1976d2; padding: 0.6rem; border-radius: 5px; margin: 0.5rem 0; font-size: 0.85rem;}
    .success-box {background: #e8f5e9; border-left: 3px solid #4caf50; padding: 0.6rem; border-radius: 5px; margin: 0.5rem 0; font-size: 0.85rem;}
    .warning-box {background: #fff3e0; border-left: 3px solid #f57c00; padding: 0.6rem; border-radius: 5px; margin: 0.5rem 0; font-size: 0.85rem;}
    .stat-box {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.8rem; border-radius: 8px; color: white; text-align: center; margin-bottom: 0.5rem;}
    .stat-number {font-size: 1.5rem; font-weight: 700;}
    .stat-label {font-size: 0.75rem; opacity: 0.9; margin-top: 0.2rem;}
    .stButton>button {background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%); color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 7px; font-weight: 600; font-size: 0.9rem;}
    @media only screen and (max-width: 768px) {
        .main {padding: 0.5rem;}
        .header-title {font-size: 1.2rem;}
        .stat-number {font-size: 1.2rem;}
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
    st.markdown('<div class="header-box"><h1 class="header-title">Data Separation Tool</h1><p class="header-subtitle">Multi-column smart detection - iOS compatible</p></div>', unsafe_allow_html=True)
    
    if 'detector' not in st.session_state:
        st.session_state.detector = MultiColumnDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    
    st.markdown('<div class="card"><h3 class="card-title">Upload File</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
    
    if uploaded:
        st.markdown('<div class="info-box">File loaded successfully</div>', unsafe_allow_html=True)
        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = []
            for s in sheets:
                opts.append(str(s['name']) + " (" + str(s['rows']) + " rows)")
            
            sel = st.selectbox("Sheet", opts, label_visibility="collapsed")
            st.session_state.sheet = sheets[opts.index(sel)]['name']
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card"><h3 class="card-title">Select Categories</h3>', unsafe_allow_html=True)
    
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
    
    selected = []
    for cat in all_cats:
        if st.checkbox(cat, value=cat in st.session_state.selected_cats, key="c_" + cat):
            selected.append(cat)
    st.session_state.selected_cats = selected
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="card"><h3 class="card-title">Process Data</h3>', unsafe_allow_html=True)
        
        if st.button("Process Data", type="primary", use_container_width=True):
            try:
                with st.spinner('Processing...'):
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
                st.error("Error: " + str(e))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.processed and st.session_state.stats:
        st.markdown("---")
        
        stats = st.session_state.stats
        
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["total_rows"]) + '</div><div class="stat-label">Total</div></div>', unsafe_allow_html=True)
        with r1c2:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["well_matched"]) + '</div><div class="stat-label">Matched</div></div>', unsafe_allow_html=True)
        
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["forced_matched"]) + '</div><div class="stat-label">Forced</div></div>', unsafe_allow_html=True)
        with r2c2:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats["categories_found"]) + '</div><div class="stat-label">Files</div></div>', unsafe_allow_html=True)
        
        if stats.get('priority_cols'):
            priority_cols_text = ", ".join(stats["priority_cols"][:3])
            st.markdown('<div class="info-box">Priority columns: ' + priority_cols_text + '</div>', unsafe_allow_html=True)
        
        st.markdown("### Distribution")
        for cat, count in stats.get('distribution', {}).items():
            if cat:
                pct = (count / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
                pct_text = str(round(pct, 1))
                st.write("**" + str(cat) + "**: " + str(count) + " items (" + pct_text + "%)")
        
        st.markdown("### Download Files")
        
        for cat, data in st.session_state.processed.items():
            fname = st.session_state.filename + "_" + cat + ".xlsx"
            excel = create_excel(data)
            if excel:
                btn_label = cat + " (" + str(len(data)) + " rows)"
                st.download_button(
                    btn_label, 
                    excel, 
                    fname, 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    use_container_width=True,
                    key="dl_" + cat
                )

if __name__ == "__main__":
    main()
