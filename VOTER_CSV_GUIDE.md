# 📊 Voter CSV Import Guide

This guide explains how to prepare voter data for bulk import into the Django Election Voting System.

## 📋 Required CSV Format

### Basic Format (Required Columns)
```csv
name,reg_no
John Smith,2021001
Sarah Johnson,2021002
```

### Required Columns:
- **name**: Full name of the voter (text)
- **reg_no**: Unique registration number or student ID (text/number)

## 📁 Sample Files Included

### `sample_voters.csv`
- **Purpose**: Basic voter import with required fields only
- **Columns**: name, reg_no
- **Records**: 5 sample voters
- **Use Case**: All elections - simple and clean format

## 🔧 How to Use

### Step 1: Prepare Your Data
1. **Open Excel or Google Sheets**
2. **Use the provided `sample_voters.csv` as a template**
3. **Replace sample data with your actual voter information**
4. **Ensure each reg_no is unique**

### Step 2: Save as CSV
1. **File → Save As**
2. **Choose CSV (Comma delimited) format**
3. **Save with .csv extension**

### Step 3: Import into System
```bash
# Via Django management command
python manage.py import_voters your_voters.csv

# Via admin interface
# Go to http://localhost:8000/admin/ → Import Voters
```

## ✅ Data Validation Rules

### Required Fields:
- ✅ **name**: Cannot be empty, maximum 100 characters
- ✅ **reg_no**: Cannot be empty, must be unique, maximum 20 characters

**Note**: The system only requires these two fields. Additional fields like email, class, etc. can be managed separately in the admin interface if needed.

## 🚫 Common Mistakes to Avoid

### ❌ Invalid Data:
```csv
name,reg_no
,2021001          # Empty name
John Smith,       # Empty reg_no
John Smith,2021001
Jane Doe,2021001  # Duplicate reg_no
```

### ✅ Correct Data:
```csv
name,reg_no
John Smith,2021001
Jane Doe,2021002
Bob Johnson,2021003
```

## 🔒 Security Notes

- **Tokens are auto-generated** during import (UUID format)
- **Keep voter files secure** - they contain sensitive information
- **Don't share tokens publicly** - distribute individually to voters
- **Backup your voter data** before importing

## 📤 Export Options

After import, you can export voter data with tokens:

```bash
# Export with tokens for distribution
python manage.py export_voters voter_tokens.csv --tokens-only

# Export complete voter data
python manage.py export_voters full_export.csv --include-voted
```

## 🛠️ Troubleshooting

### Import Errors:
1. **"Duplicate reg_no"**: Ensure all registration numbers are unique
2. **"Missing required field"**: Check that name and reg_no columns exist
3. **"Invalid format"**: Ensure file is saved as CSV with comma delimiters

### Excel Tips:
- **Remove extra spaces** from data
- **Use Text format** for reg_no to preserve leading zeros
- **Check encoding** - save as UTF-8 if special characters are used

## 📞 Support

If you encounter issues:
1. Check the Django admin logs
2. Verify CSV format matches the examples
3. Ensure all required fields have values
4. Contact the system administrator

---

**Happy Voting! 🗳️**
