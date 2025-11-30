#!/usr/bin/env python3
"""
XML to Excel Converter
======================

A flexible Python script that dynamically parses any XML structure and converts
it to an Excel (.xlsx) file. The script automatically adapts to varying, nested,
or inconsistent tag structures.

Features:
---------
- Dynamic XML parsing that adapts to any tag structure
- Automatic flattening with dot-notation paths (e.g., book.author.name)
- Handles repeated elements by generating separate rows
- Graceful handling of missing fields (fills with None/blank)
- Supports deeply nested structures
- Includes XML attributes as separate columns

Requirements:
-------------
- Python 3.6+
- pandas
- openpyxl

Installation:
-------------
    pip install pandas openpyxl

Usage:
------
    python xml_to_excel.py <input.xml> [output.xlsx]

    Arguments:
        input.xml   - Path to the XML file to convert
        output.xlsx - (Optional) Path for the output Excel file
                      Defaults to input filename with .xlsx extension

Examples:
---------
    python xml_to_excel.py data.xml
    python xml_to_excel.py data.xml output.xlsx

Sample XML Input:
-----------------
    <?xml version="1.0" encoding="UTF-8"?>
    <catalog>
        <book id="1">
            <title>Python Programming</title>
            <author>
                <name>John Smith</name>
                <email>john@example.com</email>
            </author>
            <price>29.99</price>
            <tags>
                <tag>programming</tag>
                <tag>python</tag>
            </tags>
        </book>
        <book id="2">
            <title>Data Science Basics</title>
            <author>
                <name>Jane Doe</name>
            </author>
            <price>39.99</price>
        </book>
    </catalog>

Expected Excel Output:
----------------------
    | book.@id | book.title           | book.author.name | book.author.email  | book.price | book.tags.tag |
    |----------|----------------------|------------------|--------------------| -----------|---------------|
    | 1        | Python Programming   | John Smith       | john@example.com   | 29.99      | programming   |
    | 1        | Python Programming   | John Smith       | john@example.com   | 29.99      | python        |
    | 2        | Data Science Basics  | Jane Doe         | None               | 39.99      | None          |

Note: Repeated elements (like multiple <tag> entries) create separate rows.
      Attributes are prefixed with '@' (e.g., book.@id).

How to Extend:
--------------
1. To change the path delimiter from '.' to something else:
   - Modify the PATH_DELIMITER constant below

2. To exclude attributes from output:
   - Set INCLUDE_ATTRIBUTES = False

3. To add custom data type conversion:
   - Modify the convert_value() function

4. To handle specific XML namespaces:
   - Modify the strip_namespace() function

Author: XML to Excel Converter
License: MIT
"""

import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import sys
import os
from collections import OrderedDict
from typing import List, Dict, Any, Iterator, Tuple, Optional

PATH_DELIMITER = "."
INCLUDE_ATTRIBUTES = True
ATTRIBUTE_PREFIX = "@"


def strip_namespace(tag: str) -> str:
    """
    Remove XML namespace prefix from a tag.
    
    Args:
        tag: The XML tag potentially containing a namespace
        
    Returns:
        The tag name without namespace
        
    Example:
        '{http://example.com}book' -> 'book'
    """
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def convert_value(value: Optional[str]) -> Any:
    """
    Convert string values to appropriate Python types.
    
    Args:
        value: String value from XML
        
    Returns:
        Converted value (int, float, bool, or original string)
    """
    if value is None:
        return None
    
    value = value.strip()
    if not value:
        return None
    
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    return value


def get_element_paths(element: ET.Element, parent_path: str = "") -> Dict[str, Any]:
    """
    Recursively extract all paths and values from an XML element.
    
    Args:
        element: The XML element to process
        parent_path: The dot-notation path to this element
        
    Returns:
        Dictionary mapping paths to values
    """
    result = OrderedDict()
    tag = strip_namespace(element.tag)
    current_path = f"{parent_path}{PATH_DELIMITER}{tag}" if parent_path else tag
    
    if INCLUDE_ATTRIBUTES and element.attrib:
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{current_path}{PATH_DELIMITER}{ATTRIBUTE_PREFIX}{attr_name}"
            result[attr_path] = convert_value(attr_value)
    
    children = list(element)
    
    if not children:
        text = element.text
        if text and text.strip():
            result[current_path] = convert_value(text)
        elif current_path not in result:
            result[current_path] = None
    else:
        if element.text and element.text.strip():
            result[current_path] = convert_value(element.text)
        
        for child in children:
            child_data = get_element_paths(child, current_path)
            result.update(child_data)
    
    return result


def cartesian_product_rows(row_groups: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Compute the Cartesian product of multiple row groups.
    
    Args:
        row_groups: List of row group lists to combine
        
    Returns:
        List of combined row dictionaries
    """
    if not row_groups:
        return [OrderedDict()]
    
    if len(row_groups) == 1:
        return row_groups[0]
    
    result = row_groups[0]
    for next_group in row_groups[1:]:
        new_result = []
        for existing_row in result:
            for new_row in next_group:
                combined = OrderedDict(existing_row)
                combined.update(new_row)
                new_result.append(combined)
        result = new_result
    
    return result if result else [OrderedDict()]


def flatten_element(element: ET.Element, parent_path: str = "") -> List[Dict[str, Any]]:
    """
    Flatten an XML element into a list of row dictionaries.
    Handles repeating elements by creating multiple rows using Cartesian product.
    All child groups (both directly repeating and non-repeating containers with
    repeating descendants) are combined uniformly via Cartesian product.
    
    Args:
        element: The XML element to flatten
        parent_path: The dot-notation path to this element
        
    Returns:
        List of dictionaries, each representing a row
    """
    tag = strip_namespace(element.tag)
    current_path = f"{parent_path}{PATH_DELIMITER}{tag}" if parent_path else tag
    
    base_data = OrderedDict()
    
    if INCLUDE_ATTRIBUTES and element.attrib:
        for attr_name, attr_value in element.attrib.items():
            attr_path = f"{current_path}{PATH_DELIMITER}{ATTRIBUTE_PREFIX}{attr_name}"
            base_data[attr_path] = convert_value(attr_value)
    
    if element.text and element.text.strip():
        base_data[current_path] = convert_value(element.text)
    
    children = list(element)
    
    if not children:
        if not base_data:
            base_data[current_path] = None
        return [base_data]
    
    child_groups = {}
    for child in children:
        child_tag = strip_namespace(child.tag)
        child_path = f"{current_path}{PATH_DELIMITER}{child_tag}"
        if child_path not in child_groups:
            child_groups[child_path] = []
        child_groups[child_path].append(child)
    
    repeating_paths = [path for path, elements in child_groups.items() if len(elements) > 1]
    non_repeating_paths = [path for path, elements in child_groups.items() if len(elements) == 1]
    
    all_row_groups = []
    
    for path in non_repeating_paths:
        child = child_groups[path][0]
        child_rows = flatten_element(child, current_path)
        if child_rows:
            all_row_groups.append(child_rows)
    
    for rep_path in repeating_paths:
        path_rows = []
        for child in child_groups[rep_path]:
            child_rows = flatten_element(child, current_path)
            path_rows.extend(child_rows)
        if path_rows:
            all_row_groups.append(path_rows)
    
    if not all_row_groups:
        return [base_data]
    
    combined = cartesian_product_rows(all_row_groups)
    
    result = []
    for combo in combined:
        row = OrderedDict(base_data)
        row.update(combo)
        result.append(row)
    
    return result if result else [base_data]


def get_record_elements(root: ET.Element) -> Tuple[str, List[ET.Element]]:
    """
    Identify the main record elements in the XML.
    These are typically the direct children of the root that represent data records.
    
    Args:
        root: The root XML element
        
    Returns:
        Tuple of (record tag name, list of record elements)
    """
    child_counts = {}
    for child in root:
        tag = strip_namespace(child.tag)
        child_counts[tag] = child_counts.get(tag, 0) + 1
    
    if child_counts:
        most_common_tag = max(child_counts, key=lambda k: child_counts[k])
        records = [child for child in root if strip_namespace(child.tag) == most_common_tag]
        return most_common_tag, records
    
    return "", []


def parse_xml_to_rows(xml_file: str) -> List[Dict[str, Any]]:
    """
    Parse an XML file and convert it to a list of row dictionaries.
    
    Args:
        xml_file: Path to the XML file
        
    Returns:
        List of dictionaries, each representing a row in the output
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    record_tag, records = get_record_elements(root)
    
    all_rows = []
    
    if records:
        for record in records:
            record_rows = flatten_element(record)
            all_rows.extend(record_rows)
    else:
        all_rows = flatten_element(root)
    
    return all_rows


def collect_all_columns(rows: List[Dict[str, Any]]) -> List[str]:
    """
    Collect all unique column names from all rows, preserving order.
    
    Args:
        rows: List of row dictionaries
        
    Returns:
        Ordered list of column names
    """
    columns = OrderedDict()
    for row in rows:
        for key in row.keys():
            columns[key] = True
    return list(columns.keys())


def normalize_rows(rows: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
    """
    Ensure all rows have all columns, filling missing ones with None.
    
    Args:
        rows: List of row dictionaries
        columns: List of all column names
        
    Returns:
        List of normalized row dictionaries
    """
    normalized = []
    for row in rows:
        normalized_row = OrderedDict()
        for col in columns:
            normalized_row[col] = row.get(col, None)
        normalized.append(normalized_row)
    return normalized


def xml_to_excel(input_file: str, output_file: str) -> None:
    """
    Convert an XML file to an Excel file.
    
    Args:
        input_file: Path to the input XML file
        output_file: Path for the output Excel file
    """
    print(f"Parsing XML file: {input_file}")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    rows = parse_xml_to_rows(input_file)
    
    if not rows:
        print("Warning: No data found in XML file. Creating empty Excel file.")
        df = pd.DataFrame()
    else:
        columns = collect_all_columns(rows)
        normalized_rows = normalize_rows(rows, columns)
        df = pd.DataFrame(normalized_rows)
    
    print(f"Found {len(rows)} row(s) and {len(df.columns)} column(s)")
    
    df.to_excel(output_file, index=False, engine="openpyxl")
    
    print(f"Excel file created: {output_file}")
    print(f"Columns: {list(df.columns)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert XML files to Excel format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python xml_to_excel.py data.xml
  python xml_to_excel.py data.xml output.xlsx

The script automatically:
  - Flattens nested XML structures using dot-notation
  - Handles repeating elements by creating multiple rows
  - Includes XML attributes with @ prefix
  - Fills missing fields with blank values
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input XML file"
    )
    
    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Path for the output Excel file (default: input filename with .xlsx extension)"
    )
    
    args = parser.parse_args()
    
    if args.output_file is None:
        base_name = os.path.splitext(args.input_file)[0]
        args.output_file = f"{base_name}.xlsx"
    
    try:
        xml_to_excel(args.input_file, args.output_file)
        print("\nConversion completed successfully!")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
