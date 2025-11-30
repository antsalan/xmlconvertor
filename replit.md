# XML to Excel Converter

## Overview
A flexible Python application that dynamically parses any XML structure and converts it to an Excel (.xlsx) file. Features both a command-line interface and a professional web UI with drag-and-drop upload, data preview, and instant download.

## Web Interface

Start the web app:
```bash
python app.py
```

Then open your browser to view the application. The web interface provides:
- Drag & drop file upload
- Real-time conversion with progress indicator
- Data preview table before download
- One-click Excel file download

## Command Line Usage

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
- **Repeating elements** - Multiple rows generated for repeated XML elements (Cartesian product)
- **Attribute support** - XML attributes included with `@` prefix (e.g., `book.@id`)
- **Missing field handling** - Fills missing fields with blank/None values
- **Deep nesting support** - Handles arbitrarily deep XML structures (5+ levels)
- **Data type conversion** - Automatically converts integers, floats, booleans
- **Special character handling** - Properly decodes XML entities

## Project Structure
```
/
├── app.py              # Flask web application
├── xml_to_excel.py     # Core conversion script (CLI + library)
├── requirements.txt    # Python dependencies
├── README.md           # Complete documentation with local usage instructions
├── templates/
│   └── index.html      # Web UI template
├── static/
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── app.js      # Frontend JavaScript
├── tests/
│   ├── run_tests.py    # Comprehensive test suite (12 tests)
│   └── test_*.xml      # Test XML files for various edge cases
├── sample_data.xml     # Sample XML file for testing
└── replit.md           # This documentation
```

## Test Suite
Run the comprehensive test suite:
```bash
python tests/run_tests.py
```

Tests cover:
- Simple XML structures
- Nested elements (multi-level)
- XML attributes with @ prefix
- Repeating elements (row expansion)
- Cartesian product (mixed repeating)
- Missing/optional fields
- Deep nesting (5+ levels)
- Empty elements
- Special characters (&, <, >)
- Data type conversion
- Excel file generation
- Sample data validation

## Dependencies
- Python 3.6+
- Flask (web interface)
- pandas
- openpyxl

## Configuration Options (in xml_to_excel.py)
- `PATH_DELIMITER` - Change the dot notation delimiter (default: ".")
- `INCLUDE_ATTRIBUTES` - Include/exclude XML attributes (default: True)
- `ATTRIBUTE_PREFIX` - Prefix for attribute columns (default: "@")

## Recent Changes
- 2025-11-30: Added comprehensive test suite with 12 automated tests
  - Created test XML files covering all edge cases
  - Verified Cartesian product logic for mixed repeating elements
  - Added README.md with local usage instructions
- 2025-11-30: Added professional web frontend with Flask
  - Drag-and-drop file upload with visual feedback
  - Data preview table with scrolling and column headers
  - Download button for converted Excel files
  - Responsive design with Bootstrap 5
- 2025-11-30: Initial creation of XML to Excel converter script
  - Full dynamic XML parsing with dot-notation flattening
  - Cartesian product for repeating elements at any nesting level
  - Support for attributes and deeply nested structures
