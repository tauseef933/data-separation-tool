import streamlit as st
import pandas as pd
import openpyxl
from openpyxl import load_workbook
import io
import re
from datetime import datetime
from typing import Dict, List, Tuple, Set
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Data Separation Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        padding: 2rem;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem 3rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    
    .header-title {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        color: #b8d4f1;
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        letter-spacing: 0.2px;
    }
    
    /* Cards */
    .card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e1e8ed;
    }
    
    .card-title {
        color: #1a1a1a;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #2a5298;
    }
    
    /* Upload section */
    .upload-section {
        background: #f8f9fa;
        padding: 2.5rem;
        border-radius: 10px;
        border: 2px dashed #cbd5e0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #2a5298;
        background: #f0f4f8;
    }
    
    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #1976d2;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin: 1rem 0;
        color: #1565c0;
        font-size: 0.95rem;
    }
    
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #f57c00;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin: 1rem 0;
        color: #e65100;
        font-size: 0.95rem;
    }
    
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin: 1rem 0;
        color: #2e7d32;
        font-size: 0.95rem;
    }
    
    /* Category badges */
    .category-badge {
        display: inline-block;
        background: #2a5298;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.3rem;
    }
    
    /* Stats container */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(42, 82, 152, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(42, 82, 152, 0.4);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: #2a5298 !important;
        color: white !important;
        font-weight: 600;
        padding: 0.8rem !important;
    }
    
    .dataframe td {
        padding: 0.6rem !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #cbd5e0;
        border-radius: 8px;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: white;
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Category detection system
class CategoryDetector:
    def __init__(self):
        self.categories = {
            'Lighting': [
                'light', 'lamp', 'chandelier', 'fixture', 'bulb', 'sconce', 
                'pendant', 'lantern', 'illumination', 'luminary', 'lighting',
                'led', 'fluorescent', 'halogen', 'spotlight', 'floodlight',
                'downlight', 'uplight', 'track light', 'recessed', 'candelabra',
                'table lamp', 'floor lamp', 'desk lamp', 'wall light', 'ceiling light',
                'strip light', 'rope light', 'neon', 'tube light', 'night light'
            ],
            'Fans': [
                'fan', 'ceiling fan', 'exhaust', 'ventilator', 'blower',
                'pedestal fan', 'table fan', 'wall fan', 'tower fan',
                'stand fan', 'portable fan', 'oscillating fan', 'cooling fan',
                'air circulator', 'ventilation', 'extractor fan', 'industrial fan'
            ],
            'Furniture': [
                'chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch',
                'bed', 'dresser', 'wardrobe', 'bookcase', 'stool', 'bench',
                'ottoman', 'sectional', 'loveseat', 'recliner', 'armchair',
                'dining table', 'coffee table', 'end table', 'nightstand',
                'credenza', 'buffet', 'hutch', 'console', 'vanity', 'armoire',
                'futon', 'daybed', 'bunk bed', 'crib', 'changing table',
                'filing cabinet', 'storage unit', 'media center', 'tv stand',
                'computer desk', 'office chair', 'conference table', 'workstation'
            ],
            'Decor': [
                'decor', 'decoration', 'ornament', 'vase', 'picture frame',
                'mirror', 'wall art', 'sculpture', 'statue', 'figurine',
                'candle holder', 'plant pot', 'planter', 'centerpiece',
                'tapestry', 'wall hanging', 'clock', 'throw pillow', 'cushion',
                'rug', 'carpet', 'mat', 'curtain', 'drape', 'blind',
                'valance', 'wreath', 'garland', 'basket', 'tray', 'bowl'
            ],
            'Electronics': [
                'electronic', 'device', 'gadget', 'appliance', 'tv', 'television',
                'monitor', 'speaker', 'audio', 'video', 'phone', 'tablet',
                'computer', 'laptop', 'printer', 'scanner', 'router', 'modem',
                'camera', 'projector', 'screen', 'remote', 'control', 'charger'
            ],
            'Kitchen': [
                'kitchen', 'cookware', 'utensil', 'pot', 'pan', 'plate', 'bowl',
                'cup', 'glass', 'mug', 'cutlery', 'knife', 'fork', 'spoon',
                'microwave', 'oven', 'stove', 'refrigerator', 'dishwasher',
                'blender', 'mixer', 'toaster', 'kettle', 'coffee maker'
            ],
            'Bathroom': [
                'bathroom', 'toilet', 'sink', 'faucet', 'shower', 'bathtub',
                'vanity', 'medicine cabinet', 'towel rack', 'soap dispenser',
                'mirror cabinet', 'bath mat', 'shower curtain', 'toilet paper holder'
            ],
            'Outdoor': [
                'outdoor', 'patio', 'garden', 'lawn', 'deck', 'balcony',
                'gazebo', 'pergola', 'umbrella', 'grill', 'bbq', 'planter',
                'outdoor furniture', 'hammock', 'swing', 'fire pit'
            ]
        }
        
        self.learned_categories = {}
    
    def detect_category(self, text: str) -> str:
        """Detect category from text using keyword matching"""
        if pd.isna(text):
            return 'Uncategorized'
        
        text_lower = str(text).lower()
        
        # Check predefined categories
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Check learned categories
        for category, keywords in self.learned_categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = category_scores.get(category, 0) + score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'Uncategorized'
    
    def learn_new_category(self, category_name: str, sample_texts: List[str]):
        """Learn a new category from sample texts"""
        # Extract common words
        words = set()
        for text in sample_texts:
            if pd.notna(text):
                text_words = re.findall(r'\b\w+\b', str(text).lower())
                words.update(text_words)
        
        # Filter common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        self.learned_categories[category_name] = keywords[:20]  # Limit to 20 keywords

def analyze_excel_structure(file) -> Dict:
    """Analyze Excel file structure"""
    wb = load_workbook(file, read_only=True, data_only=True)
    
    structure = {
        'sheets': [],
        'total_sheets': len(wb.sheetnames)
    }
    
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        
        # Get max row and column with data
        max_row = sheet.max_row
        max_col = sheet.max_column
        
        # Count non-empty cells
        non_empty = 0
        for row in sheet.iter_rows(max_row=min(max_row, 100)):  # Sample first 100 rows
            for cell in row:
                if cell.value is not None:
                    non_empty += 1
        
        structure['sheets'].append({
            'name': sheet_name,
            'rows': max_row,
            'columns': max_col,
            'non_empty_cells': non_empty,
            'estimated_size': non_empty
        })
    
    wb.close()
    return structure

def find_category_columns(df: pd.DataFrame) -> List[str]:
    """Find columns that might contain category information"""
    category_keywords = ['type', 'category', 'description', 'item', 'product', 'name', 'title']
    potential_columns = []
    
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in category_keywords):
            potential_columns.append(col)
    
    return potential_columns

def process_excel_file(file, sheet_name: str, detector: CategoryDetector) -> Tuple[Dict[str, pd.DataFrame], Dict]:
    """Process Excel file and separate data by category"""
    
    # Read the specified sheet
    df = pd.read_excel(file, sheet_name=sheet_name)
    
    # Find potential category columns
    category_columns = find_category_columns(df)
    
    # Add category column
    df['Detected_Category'] = 'Uncategorized'
    
    # Detect categories from multiple columns
    for idx, row in df.iterrows():
        categories_found = []
        
        # Check all potential category columns
        for col in category_columns:
            if col in df.columns:
                category = detector.detect_category(row[col])
                if category != 'Uncategorized':
                    categories_found.append(category)
        
        # If no category found in specific columns, check all text columns
        if not categories_found:
            for col in df.columns:
                if df[col].dtype == 'object':
                    category = detector.detect_category(row[col])
                    if category != 'Uncategorized':
                        categories_found.append(category)
                        break
        
        # Assign the most common category found
        if categories_found:
            df.at[idx, 'Detected_Category'] = max(set(categories_found), key=categories_found.count)
    
    # Separate data by category
    separated_data = {}
    for category in df['Detected_Category'].unique():
        category_df = df[df['Detected_Category'] == category].copy()
        category_df = category_df.drop('Detected_Category', axis=1)
        separated_data[category] = category_df
    
    # Statistics
    stats = {
        'total_rows': len(df),
        'categories_found': len(separated_data),
        'category_distribution': df['Detected_Category'].value_counts().to_dict(),
        'uncategorized_count': len(df[df['Detected_Category'] == 'Uncategorized'])
    }
    
    return separated_data, stats

def create_excel_file(df: pd.DataFrame, filename: str) -> bytes:
    """Create Excel file from DataFrame"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        
        # Get the workbook and sheet
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        # Style the header
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_fill = PatternFill(start_color='2a5298', end_color='2a5298', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True, size=11)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output.getvalue()

def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Data Separation Tool</h1>
        <p class="header-subtitle">Intelligent Excel data categorization and separation system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = CategoryDetector()
    
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    
    if 'original_filename' not in st.session_state:
        st.session_state.original_filename = None
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Upload Excel File</h3>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Select your Excel file",
            type=['xlsx', 'xlsm', 'xls'],
            help="Maximum file size: 200MB"
        )
        
        if uploaded_file:
            st.session_state.original_filename = uploaded_file.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
            
            # Analyze file structure
            with st.spinner('Analyzing file structure...'):
                structure = analyze_excel_structure(uploaded_file)
            
            st.markdown('<div class="info-box">File analysis complete</div>', unsafe_allow_html=True)
            
            # Sheet selection
            st.markdown("### Select Sheet to Process")
            
            sheet_options = []
            for sheet in structure['sheets']:
                sheet_options.append(
                    f"{sheet['name']} ({sheet['rows']:,} rows × {sheet['columns']} columns)"
                )
            
            selected_sheet_display = st.selectbox(
                "Choose the sheet containing your data",
                sheet_options,
                help="Select the sheet with the main data to be categorized"
            )
            
            selected_sheet = structure['sheets'][sheet_options.index(selected_sheet_display)]['name']
            
            # Process button
            if st.button("Process Data", type="primary", use_container_width=True):
                with st.spinner('Processing data... This may take a moment for large files.'):
                    progress_bar = st.progress(0)
                    
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Process
                    progress_bar.progress(30)
                    separated_data, stats = process_excel_file(
                        uploaded_file,
                        selected_sheet,
                        st.session_state.detector
                    )
                    progress_bar.progress(70)
                    
                    st.session_state.processed_data = separated_data
                    st.session_state.stats = stats
                    progress_bar.progress(100)
                    
                st.markdown('<div class="success-box">Processing complete!</div>', unsafe_allow_html=True)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">System Information</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="padding: 1rem 0;">
            <p style="margin-bottom: 1rem; color: #4a5568; line-height: 1.6;">
                <strong>Supported Categories:</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        categories_html = ""
        for category in st.session_state.detector.categories.keys():
            categories_html += f'<span class="category-badge">{category}</span>'
        
        st.markdown(categories_html, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: #f7fafc; border-radius: 8px;">
            <p style="font-size: 0.85rem; color: #4a5568; margin: 0; line-height: 1.5;">
                The system automatically detects categories from multiple columns including item type, 
                description, and product names. Uncategorized items will be flagged for review.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.processed_data:
        st.markdown("---")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="card-title">Processing Results</h3>', unsafe_allow_html=True)
        
        stats = st.session_state.stats
        
        # Statistics display
        stats_html = f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-number">{stats['total_rows']:,}</div>
                <div class="stat-label">Total Rows</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{stats['categories_found']}</div>
                <div class="stat-label">Categories Found</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{stats['uncategorized_count']:,}</div>
                <div class="stat-label">Uncategorized</div>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)
        
        # Warning for uncategorized items
        if stats['uncategorized_count'] > 0:
            st.markdown(f"""
            <div class="warning-box">
                <strong>Note:</strong> {stats['uncategorized_count']} rows could not be automatically categorized. 
                These have been saved in a separate "Uncategorized" file for manual review.
            </div>
            """, unsafe_allow_html=True)
        
        # Category distribution
        st.markdown("### Category Distribution")
        
        dist_data = []
        for category, count in stats['category_distribution'].items():
            percentage = (count / stats['total_rows']) * 100
            dist_data.append({
                'Category': category,
                'Count': count,
                'Percentage': f"{percentage:.1f}%"
            })
        
        dist_df = pd.DataFrame(dist_data)
        st.dataframe(dist_df, use_container_width=True, hide_index=True)
        
        # Download section
        st.markdown("### Download Separated Files")
        
        download_cols = st.columns(min(len(st.session_state.processed_data), 3))
        
        for idx, (category, data) in enumerate(st.session_state.processed_data.items()):
            col_idx = idx % 3
            with download_cols[col_idx]:
                filename = f"{st.session_state.original_filename}_{category}.xlsx"
                excel_data = create_excel_file(data, filename)
                
                st.download_button(
                    label=f"{category} ({len(data)} rows)",
                    data=excel_data,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #718096;">
        <p style="margin: 0; font-size: 0.9rem;">Data Separation Tool v1.0</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem;">Intelligent categorization system for enterprise data management</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
