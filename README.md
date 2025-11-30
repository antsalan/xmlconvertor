# XML to Excel Converter

A powerful, flexible Python tool that converts any XML file to Excel format. Features automatic structure detection, nested element flattening, and a professional web interface.

## Features

- **Dynamic XML Parsing** - Automatically adapts to any XML structure
- **Dot-Notation Flattening** - Nested elements become readable column headers (e.g., `book.author.name`)
- **Repeating Element Expansion** - Creates separate rows for repeated elements with Cartesian product logic
- **Attribute Support** - XML attributes included with `@` prefix (e.g., `book.@id`)
- **Data Type Conversion** - Automatically converts integers, floats, and booleans
- **Missing Field Handling** - Gracefully fills missing fields with blank values
- **Deep Nesting Support** - Handles arbitrarily deep XML structures (5+ levels tested)
- **Special Character Support** - Properly decodes XML entities (`&amp;`, `&lt;`, etc.)
- **Web Interface** - Professional drag-and-drop UI with preview and download

## Quick Start

### Option 1: Command Line

```bash
# Basic usage
python xml_to_excel.py input.xml

# Specify output filename
python xml_to_excel.py input.xml output.xlsx
```

### Option 2: Web Interface

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone or download this repository**

```bash
git clone <repository-url>
cd xml-to-excel-converter
```

2. **Create a virtual environment (recommended)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Verify installation**

```bash
python xml_to_excel.py sample_data.xml
```

## Usage Examples

### Command Line Interface

```bash
# Convert XML to Excel (output filename auto-generated)
python xml_to_excel.py data.xml
# Creates: data.xlsx

# Specify custom output filename
python xml_to_excel.py data.xml my_output.xlsx

# Convert multiple files (using shell)
for file in *.xml; do python xml_to_excel.py "$file"; done
```

### Web Interface

1. Start the web server:
```bash
python app.py
```

2. Open http://localhost:5000 in your browser

3. Drag and drop an XML file or click "Choose File"

4. Review the data preview

5. Click "Download Excel File"

### As a Python Library

```python
from xml_to_excel import parse_xml_to_rows, collect_all_columns, normalize_rows, xml_to_excel
import pandas as pd

# Method 1: Direct conversion to Excel
xml_to_excel("input.xml", "output.xlsx")

# Method 2: Get data as list of dictionaries
rows = parse_xml_to_rows("input.xml")
columns = collect_all_columns(rows)
normalized = normalize_rows(rows, columns)

# Method 3: Convert to pandas DataFrame
df = pd.DataFrame(normalized)
print(df.head())
```

## Sample XML and Expected Output

### Input XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <book id="1">
        <title>Python Programming</title>
        <author>
            <name>John Smith</name>
            <email>john@example.com</email>
        </author>
        <tags>
            <tag>programming</tag>
            <tag>python</tag>
        </tags>
    </book>
    <book id="2">
        <title>Data Science</title>
        <author>
            <name>Jane Doe</name>
        </author>
    </book>
</catalog>
```

### Output Excel

| book.@id | book.title | book.author.name | book.author.email | book.tags.tag |
|----------|------------|------------------|-------------------|---------------|
| 1 | Python Programming | John Smith | john@example.com | programming |
| 1 | Python Programming | John Smith | john@example.com | python |
| 2 | Data Science | Jane Doe | | |

**Note:** Book 1 generates 2 rows because it has 2 `<tag>` elements.

## Configuration

Edit these constants in `xml_to_excel.py` to customize behavior:

```python
# Change the column path separator (default: ".")
PATH_DELIMITER = "."

# Include/exclude XML attributes (default: True)
INCLUDE_ATTRIBUTES = True

# Prefix for attribute columns (default: "@")
ATTRIBUTE_PREFIX = "@"
```

## Project Structure

```
xml-to-excel-converter/
├── xml_to_excel.py      # Core conversion engine (CLI + library)
├── app.py               # Flask web application
├── requirements.txt     # Python dependencies
├── sample_data.xml      # Sample XML for testing
├── templates/
│   └── index.html       # Web UI template
├── static/
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend JavaScript
├── tests/
│   ├── run_tests.py     # Comprehensive test suite
│   ├── test_simple.xml
│   ├── test_nested.xml
│   ├── test_attributes.xml
│   ├── test_repeating.xml
│   ├── test_mixed_repeating.xml
│   ├── test_missing_fields.xml
│   ├── test_deep_nesting.xml
│   ├── test_empty_elements.xml
│   ├── test_special_chars.xml
│   └── test_data_types.xml
└── README.md            # This file
```

## Running Tests

The project includes a comprehensive test suite covering all edge cases:

```bash
python tests/run_tests.py
```

### Test Coverage

| Test | Description | Status |
|------|-------------|--------|
| Simple XML | Basic two-element structure | PASS |
| Nested XML | Multi-level nesting | PASS |
| Attributes | XML attribute extraction with @ prefix | PASS |
| Repeating Elements | Multiple rows from repeated tags | PASS |
| Mixed Repeating | Cartesian product (2x2 = 4 rows) | PASS |
| Missing Fields | Optional fields filled with None | PASS |
| Deep Nesting | 5+ levels of nesting | PASS |
| Empty Elements | Empty tag handling | PASS |
| Special Characters | &amp;, &lt;, &gt; decoding | PASS |
| Data Types | Integer, float, boolean conversion | PASS |
| Excel Output | File creation and readability | PASS |
| Sample Data | Real-world complex example | PASS |
| Web API Convert | Flask /convert endpoint | PASS |
| Web API Errors | Error handling (400 responses) | PASS |

## How It Works

### 1. XML Parsing
The script uses Python's built-in `xml.etree.ElementTree` for efficient parsing.

### 2. Structure Detection
Automatically identifies repeating elements at the root level (e.g., multiple `<book>` elements).

### 3. Flattening
Nested elements are flattened using dot-notation:
- `<book><author><name>` becomes `book.author.name`
- Attributes use @ prefix: `<book id="1">` becomes `book.@id`

### 4. Cartesian Product
When multiple groups of repeating elements exist, all combinations are generated:
- 2 authors + 2 categories = 4 rows

### 5. Normalization
Missing fields are filled with `None` to ensure consistent row structure.

### 6. Excel Output
Uses `pandas` and `openpyxl` to create properly formatted Excel files.

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas openpyxl
```

### "Invalid XML format" error
- Check that your XML is well-formed
- Ensure proper encoding (UTF-8 recommended)
- Validate with an XML validator

### Large files are slow
- The script uses iterative parsing for efficiency
- For very large files (>100MB), consider splitting the XML

### Web interface not loading
- Ensure port 5000 is available
- Check firewall settings
- Try: `python app.py` and look for error messages

## License

MIT License - Free for personal and commercial use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python tests/run_tests.py`
4. Submit a pull request

## Support

For issues and feature requests, please open an issue on the repository.
