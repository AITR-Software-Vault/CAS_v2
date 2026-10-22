import os
import random
import openpyxl as op
import config

def generate_load_test_file(target_rows=2000):
    raw_dir = config.RAWFOL
    # Find an existing file to copy the structure from
    existing_files = [f for f in os.listdir(raw_dir) if f.endswith('.xlsx') and not f.startswith('~')]
    
    if not existing_files:
        print(f"Could not find any existing .xlsx file in {raw_dir} to use as a template.")
        return
        
    template_file = existing_files[0]
    template_path = os.path.join(raw_dir, template_file)
    print(f"Using {template_file} as a template structure...")
    
    # Load template
    wb_template = op.load_workbook(template_path, data_only=True)
    
    # Find the data sheet
    DEFAULT_SHEET = "Raw Data"
    if DEFAULT_SHEET in wb_template.sheetnames:
        sheet_in = wb_template[DEFAULT_SHEET]
    else:
        # Check case-insensitive
        matched = False
        for s in wb_template.sheetnames:
            if s.lower() == DEFAULT_SHEET.lower():
                sheet_in = wb_template[s]
                matched = True
                break
        if not matched:
            sheet_in = wb_template.active
            
    # Extract header and first data row
    rows = list(sheet_in.iter_rows(values_only=True))
    if len(rows) < 2:
        print("Template file doesn't have enough data (needs header + 1 row of data).")
        return
        
    header = rows[0]
    sample_data = list(rows[1])  # Convert to list so we can modify it
    
    # Identify which column is the Name column (usually index 0, but let's assume index 0 based on standard schema)
    name_col_idx = 0 
    
    # Create new workbook
    wb_new = op.Workbook()
    sheet_out = wb_new.active
    sheet_out.title = "Raw Data"
    
    # Write header
    sheet_out.append(header)
    
    print(f"Generating {target_rows} rows of test data...")
    
    # Generate 2000 rows
    for i in range(1, target_rows + 1):
        new_row = sample_data.copy()
        
        # Modify the name to be unique
        new_row[name_col_idx] = f"Test_Student_{i}"
        
        # Optional: slightly randomize the scores (columns after Demographics, let's assume index 10 onwards are scores 1-5)
        # Just to make the data slightly varied
        for j in range(10, len(new_row)):
            if isinstance(new_row[j], (int, float)):
                # If it's a Likert score usually 0-4 or 1-5
                val = int(new_row[j])
                if 0 <= val <= 5:
                    # randomize it ±1 safely
                    new_val = max(0, min(5, val + random.choice([-1, 0, 1])))
                    new_row[j] = new_val
                    
        sheet_out.append(new_row)
        
    output_filename = f"Load_Test_{target_rows}_Students.xlsx"
    output_path = os.path.join(raw_dir, output_filename)
    
    wb_new.save(output_path)
    print(f"\nSUCCESS! Created load test file at:\n{output_path}")
    print("This file will now appear in your application's dropdown menu automatically.")

if __name__ == "__main__":
    generate_load_test_file(2000)
