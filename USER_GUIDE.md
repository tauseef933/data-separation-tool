# User Guide - Data Separation Tool

## Quick Start Guide for End Users

This guide is designed for the people who will be using the Data Separation Tool daily. No technical knowledge required!

---

## What Does This Tool Do?

The Data Separation Tool takes your mixed Excel files (containing lighting, fans, furniture, and other items) and automatically separates them into organized, category-specific files.

**Input:** One Excel file with mixed data  
**Output:** Multiple Excel files, one for each category

---

## Step-by-Step Usage Instructions

### Step 1: Access the Tool

1. Open your web browser (Chrome, Firefox, Safari, Edge)
2. Go to the URL provided by your administrator
3. You should see a blue header saying "Data Separation Tool"

**No login required!** Just bookmark the URL for easy access.

---

### Step 2: Upload Your Excel File

1. Look for the upload section (white box with "Upload Excel File" title)
2. Click "Browse files" button
3. Select your Excel file from your computer
4. Supported file types: .xlsx, .xlsm, .xls
5. Maximum file size: 200 MB

**Tips:**
- Make sure your file contains category information (in columns like "Type", "Category", "Description", or "Item Name")
- The file can have multiple sheets
- All original columns will be preserved in output files

---

### Step 3: Select the Data Sheet

After uploading, you'll see a dropdown menu showing all sheets in your file.

**What you'll see:**
- Sheet name
- Number of rows
- Number of columns

**How to choose:**
1. Select the sheet that contains your main data
2. Avoid summary sheets or charts
3. Choose the sheet with the most rows

**Example:**
```
Main Data (5,234 rows × 15 columns)  ← SELECT THIS
Summary (5 rows × 3 columns)
Charts (0 rows × 0 columns)
```

---

### Step 4: Process Your Data

1. Click the blue "Process Data" button
2. Wait while the system analyzes your data (usually 10-30 seconds)
3. You'll see a progress indicator

**What's happening:**
- System scans all columns for category keywords
- Matches each row to a category (Lighting, Fans, Furniture, etc.)
- Organizes data by category
- Generates statistics

---

### Step 5: Review Results

After processing, you'll see:

#### Statistics Dashboard
Three colored boxes showing:
- **Total Rows**: How many rows were processed
- **Categories Found**: How many different categories detected
- **Uncategorized**: Rows that couldn't be categorized

#### Category Distribution Table
A table showing:
- Category name
- Number of items in each category
- Percentage of total

**Example:**
| Category | Count | Percentage |
|----------|-------|------------|
| Lighting | 1,234 | 35.2% |
| Fans | 856 | 24.4% |
| Furniture | 642 | 18.3% |
| Decor | 501 | 14.3% |
| Uncategorized | 267 | 7.8% |

---

### Step 6: Download Your Files

In the "Download Separated Files" section, you'll see a button for each category.

**Each button shows:**
- Category name
- Number of rows in that category

**To download:**
1. Click on the category button you want
2. File will download automatically
3. File name format: `YourFileName_CategoryName.xlsx`

**Example downloads:**
- `VendorData_Lighting.xlsx` (1,234 rows)
- `VendorData_Fans.xlsx` (856 rows)
- `VendorData_Furniture.xlsx` (642 rows)

**Download all files you need!**

---

## Understanding Categories

### Standard Categories Detected

1. **Lighting**
   - Lights, lamps, chandeliers, fixtures
   - LED lights, fluorescent lights
   - Ceiling lights, wall lights, floor lamps
   - Bulbs, sconces, pendants

2. **Fans**
   - Ceiling fans, table fans, wall fans
   - Exhaust fans, ventilators
   - Industrial fans, blowers
   - Portable fans, tower fans

3. **Furniture**
   - Chairs, tables, desks
   - Cabinets, shelves, wardrobes
   - Sofas, beds, dressers
   - Office furniture, dining furniture

4. **Decor**
   - Decorative items, ornaments
   - Vases, picture frames, mirrors
   - Wall art, sculptures
   - Cushions, rugs, curtains

5. **Electronics**
   - TVs, monitors, speakers
   - Computers, tablets
   - Printers, routers
   - Cameras, projectors

6. **Kitchen**
   - Cookware, utensils
   - Kitchen appliances
   - Dishes, cutlery
   - Kitchen furniture

7. **Bathroom**
   - Bathroom fixtures
   - Vanities, cabinets
   - Accessories
   - Bath mats, towel racks

8. **Outdoor**
   - Patio furniture
   - Garden items
   - BBQ grills
   - Outdoor decor

9. **Uncategorized**
   - Items that don't match any category
   - Need manual review

---

## Working with Uncategorized Items

### Why Are Items Uncategorized?

Items might be uncategorized if:
- The description is unclear or generic
- It's a new product type the system hasn't learned
- The category column is empty
- The item name doesn't contain recognizable keywords

### What to Do with Uncategorized Items

**Option 1: Manual Review**
1. Download the Uncategorized file
2. Review each item manually
3. Sort them into appropriate categories
4. Add them to the correct category files

**Option 2: Report to Administrator**
1. Note common patterns in uncategorized items
2. Send examples to your administrator
3. They can update the system to recognize these items

---

## Tips for Best Results

### Before Uploading

✅ **DO:**
- Use files with clear category information
- Ensure "Type", "Category", or "Description" columns exist
- Remove completely empty rows
- Use consistent naming in your data

❌ **DON'T:**
- Upload summary or report files
- Upload files with only charts
- Upload files without any category information
- Upload files larger than 200 MB

### During Processing

✅ **DO:**
- Wait for processing to complete
- Keep your browser window open
- Review all statistics before downloading

❌ **DON'T:**
- Refresh the page during processing
- Close the browser window
- Click Process button multiple times

### After Processing

✅ **DO:**
- Download all category files immediately
- Check the uncategorized file
- Verify file counts match your expectations
- Keep original file as backup

❌ **DON'T:**
- Delete files before verifying contents
- Skip reviewing uncategorized items
- Forget to check category distribution

---

## Common Questions

### Q: How long does processing take?
**A:** Usually 10-30 seconds for normal files. Large files (10,000+ rows) may take up to 1 minute.

### Q: Can I process multiple files at once?
**A:** No, process one file at a time. After downloading results, you can upload the next file.

### Q: What if I upload the wrong file?
**A:** Simply upload the correct file. The previous upload will be replaced.

### Q: Can I go back and change sheet selection?
**A:** Yes, just select a different sheet from the dropdown and click Process Data again.

### Q: Will my data be saved on the server?
**A:** No, all processing happens in real-time. Files are deleted after your session ends.

### Q: What if the tool shows many uncategorized items?
**A:** This is normal for new data types. Report common patterns to your administrator so they can improve the system.

### Q: Can I download files again later?
**A:** No, download all files before closing the browser. Processing results are temporary.

### Q: What if download doesn't work?
**A:** Check your browser's download settings. Try a different browser if issues persist.

### Q: Can other people see my data?
**A:** No, each user's session is completely separate and private.

### Q: What if the tool is not loading?
**A:** Check your internet connection. Try refreshing the page. Contact your administrator if problem persists.

---

## File Naming Convention

Output files follow this format:
```
[OriginalFileName]_[Category].xlsx
```

**Examples:**
- Original: `Vendor_Q1_2024.xlsx`
- Outputs:
  - `Vendor_Q1_2024_Lighting.xlsx`
  - `Vendor_Q1_2024_Fans.xlsx`
  - `Vendor_Q1_2024_Furniture.xlsx`

This makes it easy to:
- Track which original file the data came from
- Organize files by category
- Maintain clear file history

---

## Workflow Example

**Scenario:** You receive a vendor file with 5,000 mixed items.

1. **9:00 AM** - Upload file to tool
2. **9:01 AM** - Select "Main Data" sheet
3. **9:01 AM** - Click Process Data
4. **9:02 AM** - Review results: 7 categories found, 200 uncategorized
5. **9:03 AM** - Download all 8 files (7 categories + uncategorized)
6. **9:05 AM** - Review uncategorized file
7. **9:15 AM** - Manually sort uncategorized items
8. **9:20 AM** - Send uncategorized patterns to administrator

**Total time:** 20 minutes (vs. 4+ hours manually!)

---

## What to Do If...

### The tool shows an error
1. Check file size (must be under 200 MB)
2. Verify file format (.xlsx, .xlsm, .xls)
3. Make sure file is not corrupted
4. Try a different browser
5. Contact administrator

### Processing is very slow
1. Check your internet connection
2. Large files take longer (this is normal)
3. Try during off-peak hours
4. Contact administrator if consistently slow

### Category distribution looks wrong
1. Review a sample of each category file
2. Check if keywords in your data match standard categories
3. Report patterns to administrator
4. They may need to add custom keywords

### Downloaded files won't open
1. Make sure you have Excel or compatible software
2. Check file wasn't corrupted during download
3. Try downloading again
4. Contact IT support

---

## Getting Help

### For Technical Issues
- Contact your IT administrator
- Provide error message (if any)
- Mention what step you were on
- Note the file size and number of rows

### For Category Issues
- Download uncategorized file
- Identify common patterns
- Send examples to administrator
- Request new categories if needed

### For Training
- Request a demo session
- Ask for practice files
- Review this guide periodically
- Share tips with colleagues

---

## Keyboard Shortcuts

Speed up your workflow:

- `Ctrl + Click` on upload → Select file quickly
- `Enter` after sheet selection → Start processing
- `Ctrl + S` on results → Save page (not needed, use download buttons)
- `F5` → Refresh page (start over)

---

## Best Practices Summary

### Daily Use
1. Process files as soon as you receive them
2. Download all results immediately
3. Review uncategorized items weekly
4. Keep original files organized
5. Report patterns to administrator monthly

### Quality Control
1. Spot-check 5-10 items from each category
2. Verify counts match your expectations
3. Flag any misclassifications
4. Build feedback into your workflow

### File Management
1. Create folder structure:
   ```
   Data Separation/
   ├── Original Files/
   ├── Processed - Lighting/
   ├── Processed - Fans/
   ├── Processed - Furniture/
   └── Uncategorized - To Review/
   ```
2. Date stamp folder names
3. Archive processed files monthly
4. Back up critical data

---

## Success Tips

**From experienced users:**

1. **Batch similar files** - Process all files from the same vendor together
2. **Morning processing** - Tool is fastest in early hours
3. **Double-check sheet** - Verify you selected the right sheet
4. **Download everything** - Even if category shows 0 rows
5. **Review weekly** - Check uncategorized patterns once a week
6. **Share feedback** - Help improve the tool for everyone

---

## Contact Information

**Administrator:** [Your Administrator Name]  
**Email:** [admin@yourcompany.com]  
**Support Hours:** [Your hours]  
**Tool URL:** [Your tool URL]

---

**Remember:** This tool saves hours of manual work. The more you use it, the better it gets!

**Version:** 1.0  
**Last Updated:** January 2024
