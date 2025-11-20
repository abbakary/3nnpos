"""
Utility to determine order type based on extracted invoice item codes.
Compares item codes against LabourCode mappings to classify orders as
labour, service, sales, or mixed types.
"""

import json
import logging
from typing import List, Dict, Tuple, Set

logger = logging.getLogger(__name__)


def determine_order_type_from_codes(item_codes: List[str]) -> Tuple[str, List[str], Dict]:
    """
    Determine order type based on invoice item codes.
    
    Args:
        item_codes: List of item codes extracted from invoice
        
    Returns:
        Tuple of:
        - order_type: 'labour', 'service', 'sales', or 'mixed'
        - categories: List of unique categories found
        - mapping_info: Dict with code->category mappings and unmapped codes
    """
    if not item_codes:
        return 'sales', [], {'mapped': {}, 'unmapped': []}
    
    from tracker.models import LabourCode
    
    # Clean and normalize codes
    cleaned_codes = [str(code).strip() for code in item_codes if code]
    if not cleaned_codes:
        return 'sales', [], {'mapped': {}, 'unmapped': []}
    
    # Query database for matching labour codes
    found_codes = LabourCode.objects.filter(
        code__in=cleaned_codes,
        is_active=True
    ).values('code', 'category')
    
    # Build mappings
    code_to_category = {}
    categories_found = set()
    unmapped_codes = []
    
    found_code_set = set()
    for row in found_codes:
        code = row['code']
        category = row['category']
        code_to_category[code] = category
        categories_found.add(category)
        found_code_set.add(code)
    
    # Track unmapped codes
    for code in cleaned_codes:
        if code not in found_code_set:
            unmapped_codes.append(code)
    
    # Determine order type
    if not categories_found:
        order_type = 'sales'
        categories = []
    elif len(categories_found) == 1:
        category = list(categories_found)[0]
        order_type = _normalize_category_to_order_type(category)
        categories = [category]
    else:
        order_type = 'mixed'
        categories = sorted(list(categories_found))
    
    mapping_info = {
        'mapped': code_to_category,
        'unmapped': unmapped_codes,
        'categories_found': categories
    }
    
    logger.info(
        f"Order type detection: codes={cleaned_codes}, "
        f"categories={categories}, type={order_type}"
    )
    
    return order_type, categories, mapping_info


def _normalize_category_to_order_type(category: str) -> str:
    """
    Normalize a labour code category to a valid order type.
    
    Examples:
    - 'labour' -> 'labour'
    - 'tyre service' -> 'service'
    - 'tyre service / makill' -> 'service'
    """
    if not category:
        return 'sales'
    
    category_lower = category.lower().strip()
    
    # Direct mapping
    if category_lower == 'labour':
        return 'labour'
    elif 'tyre' in category_lower or 'service' in category_lower:
        return 'service'
    else:
        return 'labour'


def get_mixed_order_status_display(order_type: str, categories: List[str]) -> str:
    """
    Generate a display string for order status showing mixed types.
    
    Examples:
    - 'service', ['tyre service'] -> 'Service'
    - 'labour', ['labour'] -> 'Labour'
    - 'mixed', ['labour', 'tyre service'] -> 'Mixed (Labour, Tyre Service)'
    """
    if order_type == 'mixed' and categories:
        formatted_categories = ', '.join(
            cat.title() for cat in categories
        )
        return f"Mixed ({formatted_categories})"
    elif order_type == 'labour':
        return 'Labour'
    elif order_type == 'service':
        return 'Service'
    elif order_type == 'sales':
        return 'Sales'
    elif order_type == 'inquiry':
        return 'Inquiry'
    else:
        return order_type.title()
