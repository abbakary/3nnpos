#!/usr/bin/env python
"""
Test script to verify invoice extraction with the provided PDF samples.
Tests extraction of headers, line items, and monetary values.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tracker.utils.pdf_text_extractor import extract_from_bytes
from decimal import Decimal

def test_pi_1765632():
    """Test extraction from PI - 1765632.pdf"""
    print("=" * 80)
    print("TEST 1: PI - 1765632.pdf (STATEOIL TANZANIA LIMITED)")
    print("=" * 80)
    
    # Read the PDF file
    with open('PI - 1765632.pdf', 'rb') as f:
        file_bytes = f.read()
    
    result = extract_from_bytes(file_bytes, 'PI - 1765632.pdf')
    
    if not result['success']:
        print(f"❌ EXTRACTION FAILED: {result.get('message')}")
        print(f"Error: {result.get('error')}")
        print(f"Raw text preview:\n{result.get('raw_text', '')[:500]}")
        return False
    
    print("\n✓ Extraction succeeded\n")
    
    # Test header extraction
    header = result['header']
    print("HEADER INFORMATION:")
    print(f"  Invoice No (PI No): {header.get('invoice_no')}")
    print(f"  Code No: {header.get('code_no')}")
    print(f"  Customer: {header.get('customer_name')}")
    print(f"  Phone: {header.get('phone')}")
    print(f"  Address: {header.get('address')}")
    print(f"  Date: {header.get('date')}")
    print(f"  Reference: {header.get('reference')}")
    
    # Verify key fields
    tests_passed = 0
    tests_total = 0
    
    tests_total += 1
    if header.get('code_no') == 'A01696':
        print("  ✓ Code No correct (A01696)")
        tests_passed += 1
    else:
        print(f"  ❌ Code No wrong: expected A01696, got {header.get('code_no')}")
    
    tests_total += 1
    if 'STATEOIL' in (header.get('customer_name') or ''):
        print("  ✓ Customer name contains STATEOIL")
        tests_passed += 1
    else:
        print(f"  ❌ Customer name missing STATEOIL: {header.get('customer_name')}")
    
    tests_total += 1
    addr = header.get('address') or ''
    if '15950' in addr and 'DAR' in addr and 'TANZANIA' in addr:
        print("  ✓ Address contains P.O.BOX, DAR ES SALAAM, and TANZANIA (clean)")
        tests_passed += 1
    else:
        print(f"  ❌ Address incomplete or has unwanted labels: {addr}")
    
    tests_total += 1
    if header.get('phone') and header.get('phone') != '-':
        print(f"  ✓ Phone extracted: {header.get('phone')}")
        tests_passed += 1
    else:
        print(f"  ❌ Phone not extracted properly: {header.get('phone')}")
    
    # Test monetary values
    print("\nMONETARY VALUES:")
    print(f"  Subtotal: {header.get('subtotal')}")
    print(f"  Tax/VAT: {header.get('tax')}")
    print(f"  Total: {header.get('total')}")
    
    tests_total += 1
    if header.get('subtotal') == 3484144.0:
        print("  ✓ Subtotal correct (3,484,144.00)")
        tests_passed += 1
    else:
        print(f"  ❌ Subtotal wrong: expected 3484144.0, got {header.get('subtotal')}")
    
    tests_total += 1
    if header.get('tax') and abs(float(header.get('tax')) - 627145.92) < 1:
        print("  ✓ Tax/VAT correct (627,145.92)")
        tests_passed += 1
    else:
        print(f"  ❌ Tax wrong: expected 627145.92, got {header.get('tax')}")
    
    tests_total += 1
    if header.get('total') and abs(float(header.get('total')) - 4111289.92) < 1:
        print("  ✓ Total correct (4,111,289.92)")
        tests_passed += 1
    else:
        print(f"  ❌ Total wrong: expected 4111289.92, got {header.get('total')}")
    
    # Test line items
    items = result['items']
    print(f"\nLINE ITEMS ({len(items)} items):")
    
    tests_total += 1
    if len(items) == 4:
        print(f"  ✓ Correct number of items: 4")
        tests_passed += 1
    else:
        print(f"  ❌ Wrong number of items: expected 4, got {len(items)}")
    
    for i, item in enumerate(items, 1):
        print(f"\n  Item {i}:")
        print(f"    Code: {item.get('code')}")
        print(f"    Description: {item.get('description')}")
        print(f"    Qty: {item.get('qty')}")
        print(f"    Unit: {item.get('unit')}")
        print(f"    Rate: {item.get('rate')}")
        print(f"    Value: {item.get('value')}")
        
        # Validate each item
        if i == 1:
            tests_total += 1
            if 'BF GOODRICH' in (item.get('description') or '') or 'TYRE' in (item.get('description') or ''):
                print("    ✓ Description mentions BF GOODRICH/TYRE")
                tests_passed += 1
            else:
                print(f"    ❌ Description missing key details: {item.get('description')}")
            
            tests_total += 1
            if item.get('code') == '2132004135':
                print("    ✓ Code correct")
                tests_passed += 1
            else:
                print(f"    ❌ Code wrong: expected 2132004135, got {item.get('code')}")
            
            tests_total += 1
            if item.get('qty') == 4:
                print("    ✓ Qty correct (4)")
                tests_passed += 1
            else:
                print(f"    ❌ Qty wrong: expected 4, got {item.get('qty')}")
    
    print(f"\n{'=' * 80}")
    print(f"TEST RESULT: {tests_passed}/{tests_total} assertions passed")
    print(f"{'=' * 80}\n")
    
    return tests_passed == tests_total


def test_pi_1764509():
    """Test extraction from PI - 1764509.pdf"""
    print("=" * 80)
    print("TEST 2: PI - 1764509.pdf (JTI LEAF SERVICES LIMITED)")
    print("=" * 80)
    
    # Read the PDF file
    with open('PI - 1764509.pdf', 'rb') as f:
        file_bytes = f.read()
    
    result = extract_from_bytes(file_bytes, 'PI - 1764509.pdf')
    
    if not result['success']:
        print(f"❌ EXTRACTION FAILED: {result.get('message')}")
        print(f"Error: {result.get('error')}")
        return False
    
    print("\n✓ Extraction succeeded\n")
    
    header = result['header']
    print("HEADER INFORMATION:")
    print(f"  Invoice No (PI No): {header.get('invoice_no')}")
    print(f"  Code No: {header.get('code_no')}")
    print(f"  Customer: {header.get('customer_name')}")
    print(f"  Phone: {header.get('phone')}")
    print(f"  Address: {header.get('address')}")
    
    tests_passed = 0
    tests_total = 0
    
    tests_total += 1
    if 'JTI' in (header.get('customer_name') or ''):
        print("  ✓ Customer name contains JTI")
        tests_passed += 1
    else:
        print(f"  ❌ Customer name missing JTI: {header.get('customer_name')}")
    
    # Check monetary values
    print("\nMONETARY VALUES:")
    print(f"  Subtotal: {header.get('subtotal')}")
    print(f"  Tax/VAT: {header.get('tax')}")
    print(f"  Total: {header.get('total')}")
    
    tests_total += 1
    if header.get('subtotal') == 27542.37:
        print("  ✓ Subtotal correct")
        tests_passed += 1
    else:
        print(f"  ❌ Subtotal wrong: expected 27542.37, got {header.get('subtotal')}")
    
    # Check line items
    items = result['items']
    print(f"\nLINE ITEMS ({len(items)} items):")
    
    tests_total += 1
    if len(items) == 2:
        print(f"  ✓ Correct number of items: 2")
        tests_passed += 1
    else:
        print(f"  ❌ Wrong number of items: expected 2, got {len(items)}")
    
    print(f"\n{'=' * 80}")
    print(f"TEST RESULT: {tests_passed}/{tests_total} assertions passed")
    print(f"{'=' * 80}\n")
    
    return tests_passed == tests_total


if __name__ == '__main__':
    try:
        test1 = test_pi_1765632()
        test2 = test_pi_1764509()
        
        print("\n" + "=" * 80)
        if test1 and test2:
            print("✓ ALL TESTS PASSED!")
            sys.exit(0)
        else:
            print("✗ SOME TESTS FAILED")
            sys.exit(1)
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
