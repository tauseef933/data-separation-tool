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
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); padding: 1.5rem;}
    .header-box {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem 2rem; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 8px 30px rgba(0,0,0,0.12);}
    .header-title {color: #ffffff; font-size: 2rem; font-weight: 700; margin: 0;}
    .header-subtitle {color: #b8d4f1; font-size: 0.9rem; margin-top: 0.3rem;}
    .card {background: #ffffff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 1rem;}
    .card-title {color: #1a1a1a; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.8rem; border-bottom: 2px solid #2a5298; padding-bottom: 0.5rem;}
    .info-box {background: #e3f2fd; border-left: 3px solid #1976d2; padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0; font-size: 0.9rem;}
    .success-box {background: #e8f5e9; border-left: 3px solid #4caf50; padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0; font-size: 0.9rem;}
    .warning-box {background: #fff3e0; border-left: 3px solid #f57c00; padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0; font-size: 0.9rem;}
    .stat-box {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; text-align: center;}
    .stat-number {font-size: 1.8rem; font-weight: 700;}
    .stat-label {font-size: 0.85rem; opacity: 0.9; margin-top: 0.2rem;}
    .stButton>button {background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%); color: white; border: none; padding: 0.7rem 1.5rem; border-radius: 7px; font-weight: 600; font-size: 0.95rem;}
</style>
""", unsafe_allow_html=True)

class SmartCategoryDetector:
    def __init__(self):
        self.categories = {
            'Lighting': {
                'primary': ['ceiling light', 'pendant light', 'chandelier', 'wall light', 'floor lamp', 'table lamp', 'desk lamp', 'led light', 'light fixture', 'downlight', 'spotlight', 'track light', 'recessed light', 'strip light', 'tube light'],
                'secondary': ['light', 'lamp', 'bulb', 'lighting', 'luminaire', 'sconce', 'lantern', 'led', 'fluorescent', 'halogen', 'illumination']
            },
            'Fans': {
                'primary': ['ceiling fan', 'exhaust fan', 'pedestal fan', 'table fan', 'wall fan', 'tower fan', 'stand fan', 'industrial fan', 'ventilation fan', 'oscillating fan', 'cooling fan'],
                'secondary': ['fan', 'ventilator', 'blower', 'air circulator', 'extractor', 'exhaust']
            },
            'Furniture': {
                'primary': ['office chair', 'dining table', 'coffee table', 'office desk', 'computer desk', 'filing cabinet', 'book shelf', 'sofa set', 'bed frame', 'wardrobe', 'dresser', 'conference table'],
                'secondary': ['chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch', 'bed', 'bookcase', 'stool', 'bench', 'ottoman', 'furniture']
            },
            'Decor': {
                'primary': ['wall art', 'picture frame', 'decorative vase', 'throw pillow', 'area rug', 'wall mirror', 'wall hanging', 'centerpiece', 'wall decor'],
                'secondary': ['decor', 'decoration', 'ornament', 'vase', 'mirror', 'sculpture', 'cushion', 'rug', 'carpet', 'curtain', 'decorative']
            },
            'Electronics': {
                'primary': ['television', 'smart tv', 'computer monitor', 'laptop', 'desktop computer', 'wifi router', 'smart device'],
                'secondary': ['tv', 'monitor', 'speaker', 'computer', 'printer', 'scanner', 'router', 'projector', 'electronic']
            },
            'Kitchen': {
                'primary': ['kitchen cabinet', 'dining table', 'kitchen appliance', 'cookware set', 'kitchen utensil'],
                'secondary': ['kitchen', 'cookware', 'utensil', 'microwave', 'oven', 'refrigerator', 'blender', 'toaster']
            },
            'Bathroom': {
                'primary': ['bathroom vanity', 'shower head', 'bathroom cabinet', 'toilet seat', 'bathroom fixture'],
                'secondary': ['bathroom', 'toilet', 'sink', 'faucet', 'shower', 'bathtub', 'vanity']
            },
            'Outdoor': {
                'primary': ['patio furniture', 'garden furniture', 'outdoor light', 'bbq grill', 'outdoor decor'],
                'secondary': ['outdoor', 'patio', 'garden', 'lawn', 'deck', 'balcony']
            }
        }
    
    def detect_category_with_score(self, text, enabled_categories):
        """Safely detect category and return score"""
        try:
            if pd.isna(text) or text is None:
                return None, 0
            
            text_lower = str(text).lower().strip()
            if not text_lower:
                return None, 0
            
            scores = {}
            
            for category in enabled_categories:
                if category not in self.categories:
                    continue
                
                keywords = self.categories[category]
                score = 0
                
                for keyword in keywords.get('primary', []):
                    if keyword in text_lower:
                        score += 10
                
                for keyword in keywords.get('secondary', []):
                    if keyword in text_lower:
                        score += 2
                
                if score > 0:
                    scores[category] = score
            
            if scores:
                best_cat = max(scores, key=scores.get)
                return best_cat, scores[best_cat]
            
            return None, 0
            
        except Exception as e:
            return None, 0

def get_sheet_info(file):
    """Safely get sheet information"""
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = []
        for name in wb.sheetnames:
            try:
                sheet = wb[name]
                sheets.append({
                    'name': name, 
                    'rows': sheet.max_row if sheet.max_row else 0, 
                    'cols': sheet.max_column if sheet.max_column else 0
                })
            except:
                continue
        wb.close()
        return sheets
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return []

def process_file_with_forced_matching(file, sheet_name, detector, enabled_categories):
    """Process file - force all rows into enabled categories with full error handling"""
    try:
        # Read file
        df = pd.read_excel(file, sheet_name=sheet_name)
        
        if df.empty:
            return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': []}
        
        # Add helper columns
        df['Detected_Category'] = None
        df['Match_Score'] = 0
        df['Was_Forced'] = False
        
        # Find category columns
        category_cols = []
        for col in df.columns:
            try:
                col_lower = str(col).lower()
                if any(kw in col_lower for kw in ['type', 'category', 'description', 'item', 'product', 'name', 'title']):
                    category_cols.append(col)
            except:
                continue
        
        # If no specific columns found, use all object columns
        if not category_cols:
            category_cols = [col for col in df.columns if df[col].dtype == 'object']
        
        # Detect categories for each row
        for idx in df.index:
            try:
                row = df.loc[idx]
                best_category = None
                best_score = 0
                
                for col in category_cols:
                    try:
                        cell_value = row[col]
                        cat, score = detector.detect_category_with_score(cell_value, enabled_categories)
                        if score > best_score:
                            best_score = score
                            best_category = cat
                    except:
                        continue
                
                df.at[idx, 'Detected_Category'] = best_category
                df.at[idx, 'Match_Score'] = best_score
                
            except Exception as e:
                continue
        
        # Force unmatched rows into closest category
        forced_assignments = []
        unmatched_indices = df[df['Detected_Category'].isna()].index
        
        for idx in unmatched_indices:
            try:
                row = df.loc[idx]
                
                # Collect all text from the row
                all_text = []
                for col in category_cols:
                    try:
                        val = row[col]
                        if pd.notna(val) and val is not None:
                            all_text.append(str(val))
                    except:
                        continue
                
                combined_text = ' '.join(all_text).lower()
                
                # Calculate partial scores for all enabled categories
                scores = {}
                for category in enabled_categories:
                    try:
                        score = 0
                        for keyword in detector.categories[category]['primary'] + detector.categories[category]['secondary']:
                            if keyword in combined_text:
                                score += 1
                        scores[category] = score
                    except:
                        scores[category] = 0
                
                # Assign to category with highest partial match
                if any(s > 0 for s in scores.values()):
                    forced_cat = max(scores, key=scores.get)
                else:
                    # If no match at all, use first selected category
                    forced_cat = enabled_categories[0] if enabled_categories else None
                
                if forced_cat:
                    df.at[idx, 'Detected_Category'] = forced_cat
                    df.at[idx, 'Was_Forced'] = True
                    
                    # Get item identifier
                    item_name = "Unknown"
                    if category_cols:
                        try:
                            item_name = str(row[category_cols[0]])[:50]
                        except:
                            item_name = f"Row {idx+2}"
                    
                    forced_assignments.append({
                        'item': item_name,
                        'assigned_to': forced_cat
                    })
            except Exception as e:
                # If forcing fails, assign to first category
                if enabled_categories:
                    df.at[idx, 'Detected_Category'] = enabled_categories[0]
                    df.at[idx, 'Was_Forced'] = True
        
        # Separate by category
        separated = {}
        original_cols = [col for col in df.columns if col not in ['Detected_Category', 'Match_Score', 'Was_Forced']]
        
        for category in enabled_categories:
            try:
                cat_data = df[df['Detected_Category'] == category][original_cols].copy()
                if len(cat_data) > 0:
                    separated[category] = cat_data
            except:
                continue
        
        # Calculate statistics
        stats = {
            'total_rows': len(df),
            'well_matched': len(df[df['Match_Score'] >= 10]),
            'forced_matched': len(forced_assignments),
            'categories_found': len(separated),
            'distribution': df['Detected_Category'].value_counts().to_dict(),
            'forced_assignments': forced_assignments
        }
        
        return separated, stats
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': []}

def create_excel(df):
    """Safely create Excel file"""
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
                col_letter = col[0].column_letter
                for cell in col:
                    try:
                        cell_len = len(str(cell.value))
                        if cell_len > max_len:
                            max_len = cell_len
                    except:
                        pass
                ws.column_dimensions[col_letter].width = min(max_len + 2, 50)
        
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error creating Excel: {str(e)}")
        return None

def main():
    st.markdown('<div class="header-box"><h1 class="header-title">Data Separation Tool</h1><p class="header-subtitle">Smart categorization - all items assigned to selected categories</p></div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = SmartCategoryDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    if 'sheet' not in st.session_state:
        st.session_state.sheet = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    
    # Main layout - 3 columns
    col1, col2, col3 = st.columns([1.2, 1, 1.5])
    
    with col1:
        st.markdown('<div class="card"><h3 class="card-title">1. Upload File</h3>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
        
        if uploaded:
            st.markdown('<div class="info-box">✓ File loaded</div>', unsafe_allow_html=True)
            sheets = get_sheet_info(uploaded)
            if sheets:
                opts = [f"{s['name']} ({s['rows']} rows)" for s in sheets]
                sel = st.selectbox("Sheet", opts, label_visibility="collapsed")
                st.session_state.sheet = sheets[opts.index(sel)]['name']
                st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><h3 class="card-title">2. Select Categories</h3>', unsafe_allow_html=True)
        
        all_cats = list(st.session_state.detector.categories.keys())
        
        # Quick buttons
        c1, c2 = st.columns(2)
        with c1:
            if st.button("All", use_container_width=True, key="sel_all"):
                st.session_state.selected_cats = all_cats.copy()
                st.rerun()
        with c2:
            if st.button("Clear", use_container_width=True, key="clr_all"):
                st.session_state.selected_cats = []
                st.rerun()
        
        # Checkboxes
        selected = []
        for cat in all_cats:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"c_{cat}"):
                selected.append(cat)
        
        st.session_state.selected_cats = selected
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card"><h3 class="card-title">3. Process</h3>', unsafe_allow_html=True)
        
        if uploaded and st.session_state.selected_cats:
            st.markdown(f'<div class="info-box">Ready: {len(st.session_state.selected_cats)} categories</div>', unsafe_allow_html=True)
            
            if st.button("🚀 Process Data", type="primary", use_container_width=True):
                if len(st.session_state.selected_cats) == 0:
                    st.error("Select at least one category")
                else:
                    try:
                        with st.spinner('Processing...'):
                            uploaded.seek(0)
                            separated, stats = process_file_with_forced_matching(
                                uploaded, 
                                st.session_state.sheet, 
                                st.session_state.detector,
                                st.session_state.selected_cats
                            )
                            st.session_state.processed = separated
                            st.session_state.stats = stats
                        st.rerun()
                    except Exception as e:
                        st.error(f"Processing error: {str(e)}")
        else:
            if not uploaded:
                st.info("Upload file first")
            elif not st.session_state.selected_cats:
                st.warning("Select categories")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.processed and st.session_state.stats:
        st.markdown("---")
        
        # Stats row
        stats = st.session_state.stats
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with stat_cols[1]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["well_matched"]}</div><div class="stat-label">Good Match</div></div>', unsafe_allow_html=True)
        with stat_cols[2]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["forced_matched"]}</div><div class="stat-label">Force Assigned</div></div>', unsafe_allow_html=True)
        with stat_cols[3]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["categories_found"]}</div><div class="stat-label">Files Created</div></div>', unsafe_allow_html=True)
        
        # Forced assignments warning
        if stats['forced_matched'] > 0:
            with st.expander(f"⚠️ {stats['forced_matched']} items were force-assigned (click to see details)", expanded=False):
                forced_by_cat = {}
                for item in stats.get('forced_assignments', []):
                    cat = item.get('assigned_to', 'Unknown')
                    if cat not in forced_by_cat:
                        forced_by_cat[cat] = []
                    forced_by_cat[cat].append(item.get('item', 'Unknown'))
                
                for cat, items in forced_by_cat.items():
                    st.markdown(f"**{cat}** ({len(items)} items):")
                    display_items = items[:10]
                    st.markdown(", ".join(display_items) + ("..." if len(items) > 10 else ""))
        
        # Downloads
        st.markdown("### Download Files")
        
        if st.session_state.processed:
            dl_cols = st.columns(min(len(st.session_state.processed), 4))
            
            for idx, (cat, data) in enumerate(st.session_state.processed.items()):
                with dl_cols[idx % 4]:
                    fname = f"{st.session_state.filename}_{cat}.xlsx"
                    excel = create_excel(data)
                    if excel:
                        st.download_button(
                            f"{cat}\n({len(data)} rows)", 
                            excel, 
                            fname, 
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                            use_container_width=True,
                            key=f"dl_{cat}"
                        )

if __name__ == "__main__":
    main()
