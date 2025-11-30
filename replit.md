# XML to Excel Converter

## Overview
A flexible Python command-line script that dynamically parses any XML structure and converts it to an Excel (.xlsx) file. The script automatically adapts to varying, nested, or inconsistent tag structures.

## How to Run

```bash
python xml_to_excel.py <input.xml> [output.xlsx]
```

### Arguments
- `input.xml` - Path to the XML file to convert (required)
- `output.xlsx` - Path for the output Excel file (optional, defaults to input filename with .xlsx extension)

### Examples
```bash
python xml_to_excel.py data.xml
python xml_to_excel.py data.xml output.xlsx
```

## Features
- **Dynamic XML parsing** - Adapts to any tag structure automatically
- **Dot-notation flattening** - Nested elements become column headers (e.g., `book.author.name`)
- **Repeating elements** - Multiple rows generated for repeated XML elements
- **Attribute support** - XML attributes included with `@` prefix (e.g., `book.@id`)
- **Missing field handling** - Fills missing fields with blank/None values
- **Deep nesting support** - Handles arbitrarily deep XML structures

## Project Structure
```
/
├── xml_to_excel.py    # Main conversion script
├── sample_data.xml    # Sample XML file for testing
├── output.xlsx        # Generated Excel output (from test run)
└── replit.md          # This documentation
```

## Dependencies
- Python 3.6+
- pandas
- openpyxl

## Configuration Options (in xml_to_excel.py)
- `PATH_DELIMITER` - Change the dot notation delimiter (default: ".")
- `INCLUDE_ATTRIBUTES` - Include/exclude XML attributes (default: True)
- `ATTRIBUTE_PREFIX` - Prefix for attribute columns (default: "@")

## Recent Changes
- 2025-11-30: Initial creation of XML to Excel converter script
  - Full dynamic XML parsing with dot-notation flattening
  - Support for repeating elements, attributes, and deeply nested structures
  - Comprehensive inline documentation with usage examples
