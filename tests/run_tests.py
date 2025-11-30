#!/usr/bin/env python3
"""
Comprehensive Test Suite for XML to Excel Converter
====================================================

This script runs extensive tests to verify:
1. Correct row counts for all XML structures
2. Proper column generation with dot-notation
3. Accurate data extraction and type conversion
4. Handling of edge cases (missing fields, empty elements, etc.)
5. Cartesian product for repeating elements
6. Attribute extraction with @ prefix
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xml_to_excel import parse_xml_to_rows, collect_all_columns, normalize_rows, xml_to_excel
import pandas as pd
import tempfile

class TestResult:
    def __init__(self, name, passed, message, details=None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or []

def run_test(name, test_func):
    """Run a single test and return the result."""
    try:
        result = test_func()
        return result
    except Exception as e:
        return TestResult(name, False, f"Exception: {str(e)}")

def test_simple():
    """Test simple XML with two items."""
    rows = parse_xml_to_rows("tests/test_simple.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 2:
        checks.append("Row count: 2 (PASS)")
    else:
        return TestResult("Simple XML", False, f"Expected 2 rows, got {len(normalized)}")
    
    expected_cols = ['item.name', 'item.value']
    if all(col in columns for col in expected_cols):
        checks.append(f"Columns: {columns} (PASS)")
    else:
        return TestResult("Simple XML", False, f"Missing columns. Got: {columns}")
    
    if normalized[0].get('item.name') == 'Simple Item 1':
        checks.append("Data value 1: PASS")
    else:
        return TestResult("Simple XML", False, f"Wrong data: {normalized[0]}")
    
    if normalized[0].get('item.value') == 100:
        checks.append("Integer conversion: PASS")
    else:
        checks.append(f"Integer conversion: got {normalized[0].get('item.value')} (type: {type(normalized[0].get('item.value'))})")
    
    return TestResult("Simple XML", True, "All checks passed", checks)

def test_nested():
    """Test deeply nested XML structure."""
    rows = parse_xml_to_rows("tests/test_nested.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 2:
        checks.append("Row count: 2 employees (PASS)")
    else:
        return TestResult("Nested XML", False, f"Expected 2 rows, got {len(normalized)}")
    
    expected_cols = [
        'employee.personal.name',
        'employee.personal.contact.email',
        'employee.personal.contact.phone',
        'employee.job.title',
        'employee.job.department'
    ]
    missing = [c for c in expected_cols if c not in columns]
    if not missing:
        checks.append(f"Nested columns generated: PASS")
    else:
        return TestResult("Nested XML", False, f"Missing columns: {missing}")
    
    if normalized[0].get('employee.personal.contact.email') == 'john@example.com':
        checks.append("Deep nested value extraction: PASS")
    else:
        return TestResult("Nested XML", False, "Deep value extraction failed")
    
    return TestResult("Nested XML", True, "All checks passed", checks)

def test_attributes():
    """Test XML attribute extraction."""
    rows = parse_xml_to_rows("tests/test_attributes.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 2:
        checks.append("Row count: 2 products (PASS)")
    else:
        return TestResult("Attributes XML", False, f"Expected 2 rows, got {len(normalized)}")
    
    attr_cols = [c for c in columns if '@' in c]
    expected_attrs = ['product.@id', 'product.@category', 'product.@active', 'product.price.@currency', 'product.stock.@warehouse']
    missing = [a for a in expected_attrs if a not in attr_cols]
    if not missing:
        checks.append(f"Attribute columns with @ prefix: PASS ({len(attr_cols)} attrs)")
    else:
        return TestResult("Attributes XML", False, f"Missing attribute columns: {missing}")
    
    if normalized[0].get('product.@id') == 'P001':
        checks.append("Attribute value extraction: PASS")
    else:
        return TestResult("Attributes XML", False, "Attribute value extraction failed")
    
    if normalized[0].get('product.price.@currency') == 'USD':
        checks.append("Nested attribute extraction: PASS")
    else:
        return TestResult("Attributes XML", False, "Nested attribute extraction failed")
    
    return TestResult("Attributes XML", True, "All checks passed", checks)

def test_repeating():
    """Test repeating elements generate multiple rows."""
    rows = parse_xml_to_rows("tests/test_repeating.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 5:
        checks.append("Row count: 5 (3 items in order1 + 2 items in order2) (PASS)")
    else:
        return TestResult("Repeating XML", False, f"Expected 5 rows, got {len(normalized)}")
    
    order1_rows = [r for r in normalized if r.get('order.@id') == 'ORD001']
    if len(order1_rows) == 3:
        checks.append("Order 1 expanded to 3 rows: PASS")
    else:
        return TestResult("Repeating XML", False, f"Order 1 should have 3 rows, got {len(order1_rows)}")
    
    items = [r.get('order.items.item') for r in order1_rows]
    if set(items) == {'Product A', 'Product B', 'Product C'}:
        checks.append("All items preserved in separate rows: PASS")
    else:
        return TestResult("Repeating XML", False, f"Items not correctly split: {items}")
    
    for r in order1_rows:
        if r.get('order.customer') != 'Alice':
            return TestResult("Repeating XML", False, "Customer not duplicated across item rows")
    checks.append("Parent data duplicated across child rows: PASS")
    
    return TestResult("Repeating XML", True, "All checks passed", checks)

def test_mixed_repeating():
    """Test Cartesian product of multiple repeating element groups."""
    rows = parse_xml_to_rows("tests/test_mixed_repeating.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 4:
        checks.append("Row count: 4 (2 authors x 2 categories = Cartesian product) (PASS)")
    else:
        return TestResult("Mixed Repeating XML", False, f"Expected 4 rows (2x2 Cartesian), got {len(normalized)}")
    
    authors = set(r.get('book.author') for r in normalized)
    categories = set(r.get('book.categories.category') for r in normalized)
    
    if authors == {'Smith', 'Jones'}:
        checks.append("Both authors present: PASS")
    else:
        return TestResult("Mixed Repeating XML", False, f"Authors incorrect: {authors}")
    
    if categories == {'Programming', 'Python'}:
        checks.append("Both categories present: PASS")
    else:
        return TestResult("Mixed Repeating XML", False, f"Categories incorrect: {categories}")
    
    combos = set((r.get('book.author'), r.get('book.categories.category')) for r in normalized)
    expected_combos = {('Smith', 'Programming'), ('Smith', 'Python'), ('Jones', 'Programming'), ('Jones', 'Python')}
    if combos == expected_combos:
        checks.append("All 4 Cartesian combinations present: PASS")
    else:
        return TestResult("Mixed Repeating XML", False, f"Cartesian product incomplete: {combos}")
    
    return TestResult("Mixed Repeating XML", True, "All checks passed", checks)

def test_missing_fields():
    """Test handling of missing/optional fields."""
    rows = parse_xml_to_rows("tests/test_missing_fields.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 3:
        checks.append("Row count: 3 users (PASS)")
    else:
        return TestResult("Missing Fields XML", False, f"Expected 3 rows, got {len(normalized)}")
    
    expected_cols = ['user.name', 'user.email', 'user.phone', 'user.address']
    if all(c in columns for c in expected_cols):
        checks.append("All possible columns present: PASS")
    else:
        return TestResult("Missing Fields XML", False, f"Columns: {columns}")
    
    complete_user = normalized[0]
    if all(complete_user.get(c) is not None for c in expected_cols):
        checks.append("Complete user has all fields: PASS")
    else:
        return TestResult("Missing Fields XML", False, "Complete user missing fields")
    
    minimal_user = normalized[2]
    if minimal_user.get('user.name') == 'Minimal User':
        checks.append("Minimal user has name: PASS")
    else:
        return TestResult("Missing Fields XML", False, "Minimal user name missing")
    
    if minimal_user.get('user.phone') is None and minimal_user.get('user.address') is None:
        checks.append("Missing fields filled with None: PASS")
    else:
        return TestResult("Missing Fields XML", False, "Missing fields not None")
    
    return TestResult("Missing Fields XML", True, "All checks passed", checks)

def test_deep_nesting():
    """Test very deep nesting (5+ levels)."""
    rows = parse_xml_to_rows("tests/test_deep_nesting.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 2:
        checks.append("Row count: 2 (PASS)")
    else:
        return TestResult("Deep Nesting XML", False, f"Expected 2 rows, got {len(normalized)}")
    
    deep_col = 'level1.level2.level3.level4.level5.data'
    if deep_col in columns:
        checks.append(f"Deep column path generated: {deep_col} (PASS)")
    else:
        return TestResult("Deep Nesting XML", False, f"Deep column not found. Columns: {columns}")
    
    values = [r.get(deep_col) for r in normalized]
    if 'Deep Value 1' in values and 'Deep Value 2' in values:
        checks.append("Deep nested values extracted: PASS")
    else:
        return TestResult("Deep Nesting XML", False, f"Values: {values}")
    
    return TestResult("Deep Nesting XML", True, "All checks passed", checks)

def test_empty_elements():
    """Test handling of empty XML elements."""
    rows = parse_xml_to_rows("tests/test_empty_elements.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 2:
        checks.append("Row count: 2 (PASS)")
    else:
        return TestResult("Empty Elements XML", False, f"Expected 2 rows, got {len(normalized)}")
    
    record1 = normalized[0]
    if record1.get('record.field1') == 'Value 1':
        checks.append("Non-empty field preserved: PASS")
    else:
        return TestResult("Empty Elements XML", False, "Non-empty field incorrect")
    
    if record1.get('record.field2') is None:
        checks.append("Empty element becomes None: PASS")
    else:
        checks.append(f"Empty element value: {record1.get('record.field2')} (may be empty string)")
    
    return TestResult("Empty Elements XML", True, "All checks passed", checks)

def test_special_chars():
    """Test handling of XML special characters."""
    rows = parse_xml_to_rows("tests/test_special_chars.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 2:
        checks.append("Row count: 2 (PASS)")
    else:
        return TestResult("Special Chars XML", False, f"Expected 2 rows, got {len(normalized)}")
    
    entry1 = normalized[0]
    if '&' in str(entry1.get('entry.text', '')):
        checks.append("Ampersand decoded: PASS")
    else:
        return TestResult("Special Chars XML", False, f"Ampersand not decoded: {entry1.get('entry.text')}")
    
    if '<' in str(entry1.get('entry.symbols', '')) and '>' in str(entry1.get('entry.symbols', '')):
        checks.append("Less/greater than decoded: PASS")
    else:
        checks.append(f"Symbols: {entry1.get('entry.symbols')}")
    
    return TestResult("Special Chars XML", True, "All checks passed", checks)

def test_data_types():
    """Test automatic data type conversion."""
    rows = parse_xml_to_rows("tests/test_data_types.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 6:
        checks.append("Row count: 6 metrics (PASS)")
    else:
        return TestResult("Data Types XML", False, f"Expected 6 rows, got {len(normalized)}")
    
    int_row = next((r for r in normalized if r.get('metric.name') == 'Integer'), None)
    if int_row and int_row.get('metric.value') == 42:
        checks.append(f"Integer conversion: 42 (type: {type(int_row.get('metric.value')).__name__}) (PASS)")
    else:
        checks.append(f"Integer: {int_row.get('metric.value') if int_row else 'not found'}")
    
    float_row = next((r for r in normalized if r.get('metric.name') == 'Float'), None)
    if float_row and abs(float_row.get('metric.value') - 3.14159) < 0.0001:
        checks.append(f"Float conversion: {float_row.get('metric.value')} (PASS)")
    else:
        checks.append(f"Float: {float_row.get('metric.value') if float_row else 'not found'}")
    
    bool_true_row = next((r for r in normalized if r.get('metric.name') == 'Boolean True'), None)
    if bool_true_row and bool_true_row.get('metric.value') == True:
        checks.append(f"Boolean True conversion: PASS")
    else:
        checks.append(f"Boolean True: {bool_true_row.get('metric.value') if bool_true_row else 'not found'}")
    
    bool_false_row = next((r for r in normalized if r.get('metric.name') == 'Boolean False'), None)
    if bool_false_row and bool_false_row.get('metric.value') == False:
        checks.append(f"Boolean False conversion: PASS")
    else:
        checks.append(f"Boolean False: {bool_false_row.get('metric.value') if bool_false_row else 'not found'}")
    
    return TestResult("Data Types XML", True, "All checks passed", checks)

def test_excel_output():
    """Test that Excel file is properly generated and readable."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        output_file = f.name
    
    try:
        xml_to_excel("tests/test_simple.xml", output_file)
        
        checks = []
        
        if os.path.exists(output_file):
            checks.append("Excel file created: PASS")
        else:
            return TestResult("Excel Output", False, "Excel file not created")
        
        df = pd.read_excel(output_file)
        if len(df) == 2:
            checks.append(f"Excel has 2 rows: PASS")
        else:
            return TestResult("Excel Output", False, f"Excel has {len(df)} rows, expected 2")
        
        if 'item.name' in df.columns and 'item.value' in df.columns:
            checks.append("Excel has correct columns: PASS")
        else:
            return TestResult("Excel Output", False, f"Columns: {list(df.columns)}")
        
        if df.iloc[0]['item.name'] == 'Simple Item 1':
            checks.append("Excel data is correct: PASS")
        else:
            return TestResult("Excel Output", False, f"Data incorrect: {df.iloc[0].to_dict()}")
        
        return TestResult("Excel Output", True, "All checks passed", checks)
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

def test_sample_data():
    """Test the provided sample_data.xml file."""
    rows = parse_xml_to_rows("sample_data.xml")
    columns = collect_all_columns(rows)
    normalized = normalize_rows(rows, columns)
    
    checks = []
    
    if len(normalized) == 8:
        checks.append("Row count: 8 (expected from 3 books with repeating tags/reviews) (PASS)")
    else:
        return TestResult("Sample Data", False, f"Expected 8 rows, got {len(normalized)}")
    
    book1_rows = [r for r in normalized if r.get('book.@id') == '1' or r.get('book.@id') == 1]
    if len(book1_rows) == 3:
        checks.append("Book 1: 3 rows (3 tags) (PASS)")
    else:
        checks.append(f"Book 1: {len(book1_rows)} rows")
    
    book2_rows = [r for r in normalized if r.get('book.@id') == '2' or r.get('book.@id') == 2]
    if len(book2_rows) == 4:
        checks.append("Book 2: 4 rows (2 tags x 2 reviews) (PASS)")
    else:
        checks.append(f"Book 2: {len(book2_rows)} rows")
    
    book3_rows = [r for r in normalized if r.get('book.@id') == '3' or r.get('book.@id') == 3]
    if len(book3_rows) == 1:
        checks.append("Book 3: 1 row (no repeating elements) (PASS)")
    else:
        checks.append(f"Book 3: {len(book3_rows)} rows")
    
    return TestResult("Sample Data", True, "All checks passed", checks)


def test_web_api_convert():
    """Test the Flask /convert API endpoint."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import app
        
        checks = []
        
        with app.test_client() as client:
            with open("sample_data.xml", "rb") as f:
                response = client.post(
                    "/convert",
                    data={"file": (f, "sample_data.xml")},
                    content_type="multipart/form-data"
                )
            
            if response.status_code == 200:
                checks.append("POST /convert returns 200: PASS")
            else:
                return TestResult("Web API Convert", False, f"Expected 200, got {response.status_code}")
            
            data = response.get_json()
            
            if data.get("success") == True:
                checks.append("Response indicates success: PASS")
            else:
                return TestResult("Web API Convert", False, f"Response not successful: {data}")
            
            if data.get("total_rows") == 8:
                checks.append("Total rows = 8: PASS")
            else:
                return TestResult("Web API Convert", False, f"Expected 8 rows, got {data.get('total_rows')}")
            
            if data.get("total_columns") == 12:
                checks.append("Total columns = 12: PASS")
            else:
                checks.append(f"Columns = {data.get('total_columns')}")
            
            if data.get("file_id"):
                checks.append(f"File ID generated: PASS")
            else:
                return TestResult("Web API Convert", False, "No file_id in response")
            
            if len(data.get("preview", [])) > 0:
                checks.append(f"Preview data returned ({len(data.get('preview', []))} rows): PASS")
            else:
                return TestResult("Web API Convert", False, "No preview data")
        
        return TestResult("Web API Convert", True, "All checks passed", checks)
    except Exception as e:
        return TestResult("Web API Convert", False, f"Exception: {str(e)}")


def test_web_api_errors():
    """Test the Flask API error handling."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import app
        
        checks = []
        
        with app.test_client() as client:
            response = client.post("/convert", data={})
            if response.status_code == 400:
                checks.append("Missing file returns 400: PASS")
            else:
                return TestResult("Web API Errors", False, f"Expected 400 for missing file, got {response.status_code}")
            
            from io import BytesIO
            response = client.post(
                "/convert",
                data={"file": (BytesIO(b"not valid xml"), "test.xml")},
                content_type="multipart/form-data"
            )
            if response.status_code == 400:
                checks.append("Invalid XML returns 400: PASS")
            else:
                checks.append(f"Invalid XML status: {response.status_code}")
            
            response = client.post(
                "/convert",
                data={"file": (BytesIO(b"text content"), "test.txt")},
                content_type="multipart/form-data"
            )
            if response.status_code == 400:
                checks.append("Non-XML file returns 400: PASS")
            else:
                return TestResult("Web API Errors", False, f"Expected 400 for .txt file, got {response.status_code}")
        
        return TestResult("Web API Errors", True, "All checks passed", checks)
    except Exception as e:
        return TestResult("Web API Errors", False, f"Exception: {str(e)}")

def main():
    """Run all tests and print results."""
    print("=" * 70)
    print("XML to Excel Converter - Comprehensive Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        ("Simple XML", test_simple),
        ("Nested XML", test_nested),
        ("Attributes XML", test_attributes),
        ("Repeating Elements", test_repeating),
        ("Mixed Repeating (Cartesian)", test_mixed_repeating),
        ("Missing Fields", test_missing_fields),
        ("Deep Nesting (5+ levels)", test_deep_nesting),
        ("Empty Elements", test_empty_elements),
        ("Special Characters", test_special_chars),
        ("Data Type Conversion", test_data_types),
        ("Excel Output", test_excel_output),
        ("Sample Data File", test_sample_data),
        ("Web API Convert", test_web_api_convert),
        ("Web API Error Handling", test_web_api_errors),
    ]
    
    results = []
    for name, test_func in tests:
        result = run_test(name, test_func)
        results.append(result)
        
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}")
        print(f"       {result.message}")
        for detail in result.details:
            print(f"       - {detail}")
        print()
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    
    print("=" * 70)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 70)
    
    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r.passed:
                print(f"  - {r.name}: {r.message}")
        return 1
    else:
        print("\nAll tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
