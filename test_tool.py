"""
Test script for Data Separation Tool
Run this to verify everything works before deployment
"""

import pandas as pd
import openpyxl
from openpyxl import Workbook
import os

def create_sample_data():
    """Create sample Excel file for testing"""
    print("Creating sample test data...")
    
    # Sample data with mixed categories
    data = {
        'Item ID': range(1, 51),
        'Item Name': [
            'LED Ceiling Light', 'Office Chair', 'Ceiling Fan', 'Table Lamp',
            'Desk', 'Wall Fan', 'Floor Lamp', 'Sofa Set', 'Exhaust Fan',
            'Decorative Vase', 'Pendant Light', 'Dining Table', 'Tower Fan',
            'Wall Mirror', 'Chandelier', 'Bookshelf', 'Pedestal Fan',
            'Throw Pillow', 'Downlight', 'Coffee Table', 'Industrial Fan',
            'Picture Frame', 'Spotlight', 'Filing Cabinet', 'Table Fan',
            'Area Rug', 'Track Light', 'Office Desk', 'Oscillating Fan',
            'Wall Art', 'Fluorescent Light', 'Wardrobe', 'Ceiling Fan Pro',
            'Curtains', 'LED Strip Light', 'Computer Chair', 'Stand Fan',
            'Decorative Bowl', 'Recessed Light', 'Nightstand', 'Ventilation Fan',
            'Cushion Set', 'Tube Light', 'Dresser', 'Exhaust Blower',
            'Candle Holder', 'Halogen Light', 'Armchair', 'Cooling Fan',
            'Plant Pot', 'Rope Light'
        ],
        'Category': [
            'Lighting', 'Furniture', 'Fans', 'Lighting', 'Furniture',
            'Fans', 'Lighting', 'Furniture', 'Fans', 'Decor',
            'Lighting', 'Furniture', 'Fans', 'Decor', 'Lighting',
            'Furniture', 'Fans', 'Decor', 'Lighting', 'Furniture',
            'Fans', 'Decor', 'Lighting', 'Furniture', 'Fans',
            'Decor', 'Lighting', 'Furniture', 'Fans', 'Decor',
            'Lighting', 'Furniture', 'Fans', 'Decor', 'Lighting',
            'Furniture', 'Fans', 'Decor', 'Lighting', 'Furniture',
            'Fans', 'Decor', 'Lighting', 'Furniture', 'Fans',
            'Decor', 'Lighting', 'Furniture', 'Fans', 'Decor'
        ],
        'Description': [
            'Modern LED ceiling light fixture', 'Ergonomic office chair with lumbar support',
            'Energy efficient ceiling fan', 'Adjustable desk lamp', 'Wooden office desk',
        ] * 10,
        'Price': [99.99, 299.99, 199.99, 49.99, 399.99] * 10,
        'Quantity': [10, 5, 8, 15, 3] * 10,
        'Vendor': ['Vendor A', 'Vendor B', 'Vendor C', 'Vendor A', 'Vendor B'] * 10
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file with multiple sheets
    with pd.ExcelWriter('sample_data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Main Data', index=False)
        
        # Add a summary sheet
        summary = pd.DataFrame({
            'Category': ['Lighting', 'Furniture', 'Fans', 'Decor'],
            'Count': [13, 13, 13, 11]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add an empty sheet
        pd.DataFrame().to_excel(writer, sheet_name='Empty Sheet', index=False)
    
    print("✓ Sample data created: sample_data.xlsx")
    print(f"  - Main Data: {len(df)} rows")
    print(f"  - Categories: {df['Category'].nunique()} unique")
    return 'sample_data.xlsx'

def test_imports():
    """Test if all required packages are installed"""
    print("\nTesting imports...")
    try:
        import streamlit
        print("✓ streamlit installed")
    except ImportError:
        print("✗ streamlit NOT installed - run: pip install streamlit")
        return False
    
    try:
        import pandas
        print("✓ pandas installed")
    except ImportError:
        print("✗ pandas NOT installed - run: pip install pandas")
        return False
    
    try:
        import openpyxl
        print("✓ openpyxl installed")
    except ImportError:
        print("✗ openpyxl NOT installed - run: pip install openpyxl")
        return False
    
    return True

def test_category_detector():
    """Test the category detection logic"""
    print("\nTesting category detection...")
    
    from app import CategoryDetector
    
    detector = CategoryDetector()
    
    test_cases = {
        'LED Ceiling Light': 'Lighting',
        'Modern Ceiling Fan': 'Fans',
        'Office Chair': 'Furniture',
        'Decorative Vase': 'Decor',
        'Unknown Item': 'Uncategorized'
    }
    
    all_passed = True
    for text, expected in test_cases.items():
        result = detector.detect_category(text)
        if result == expected:
            print(f"✓ '{text}' → {result}")
        else:
            print(f"✗ '{text}' → {result} (expected {expected})")
            all_passed = False
    
    return all_passed

def test_file_processing():
    """Test basic file processing"""
    print("\nTesting file processing...")
    
    try:
        # Create sample file
        sample_file = create_sample_data()
        
        # Test reading
        df = pd.read_excel(sample_file, sheet_name='Main Data')
        print(f"✓ File read successfully: {len(df)} rows")
        
        # Test category detection on sample
        from app import CategoryDetector
        detector = CategoryDetector()
        
        categories_found = set()
        for idx, row in df.head(10).iterrows():  # Test first 10 rows
            category = detector.detect_category(row['Item Name'])
            categories_found.add(category)
        
        print(f"✓ Categories detected: {categories_found}")
        
        # Cleanup
        os.remove(sample_file)
        print("✓ Test file cleaned up")
        
        return True
    except Exception as e:
        print(f"✗ Error during file processing: {e}")
        return False

def test_excel_creation():
    """Test Excel file creation with formatting"""
    print("\nTesting Excel file creation...")
    
    try:
        from app import create_excel_file
        
        # Create sample dataframe
        df = pd.DataFrame({
            'Item': ['Light 1', 'Light 2', 'Light 3'],
            'Price': [99.99, 149.99, 199.99],
            'Quantity': [5, 10, 3]
        })
        
        # Create Excel file
        excel_bytes = create_excel_file(df, 'test_output.xlsx')
        
        print(f"✓ Excel file created: {len(excel_bytes)} bytes")
        
        # Verify it can be read
        import io
        test_df = pd.read_excel(io.BytesIO(excel_bytes))
        
        if len(test_df) == len(df):
            print(f"✓ Excel file verified: {len(test_df)} rows")
            return True
        else:
            print(f"✗ Row count mismatch: {len(test_df)} vs {len(df)}")
            return False
            
    except Exception as e:
        print(f"✗ Error during Excel creation: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("DATA SEPARATION TOOL - TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    
    if not results['imports']:
        print("\n" + "=" * 60)
        print("CRITICAL: Install missing packages before proceeding!")
        print("Run: pip install -r requirements.txt")
        print("=" * 60)
        return
    
    # Test 2: Category Detection
    results['detection'] = test_category_detector()
    
    # Test 3: File Processing
    results['processing'] = test_file_processing()
    
    # Test 4: Excel Creation
    results['excel'] = test_excel_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nYour tool is ready to deploy!")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Test in browser")
        print("3. Deploy to Streamlit Cloud or Hugging Face")
        print("4. Share URL with users")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease fix the issues above before deploying.")
    
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
