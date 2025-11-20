#!/usr/bin/env python
"""
Seed script to create sample data with 10 customers and 20 orders.
Demonstrates auto-progression lifecycle correctly:

AUTO-PROGRESSION FLOW:
  1. created (1-8 min old)
     → Middleware auto-progresses to 'in_progress' once 10 minutes elapsed
     → started_at is set by middleware when auto-progressing

  2. in_progress (11+ min old)
     → Auto-progressed from 'created' by middleware
     → Actively being worked on

  3. overdue (9+ working hours in progress)
     → When 'in_progress' order exceeds 9 working hours (8 AM - 5 PM)
     → Middleware marks as 'overdue' based on started_at timestamp

  4. completed
     → Finished orders with completion_at timestamp

  5. cancelled
     → Cancelled with cancellation_reason

The middleware (tracker/middleware.py) handles all transitions automatically.
No manual status changes needed - it's fully automated!
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_tracker.settings')
django.setup()

from tracker.models import Customer, Vehicle, Order, Branch, InventoryItem, Brand
from django.utils import timezone
from django.contrib.auth.models import User

def get_or_create_branch():
    """Get or create default branch"""
    branch, _ = Branch.objects.get_or_create(
        code='MAIN',
        defaults={'name': 'Main Branch', 'is_active': True}
    )
    return branch

def get_or_create_user():
    """Get or create a staff user for order assignment"""
    user, _ = User.objects.get_or_create(
        username='staff_user',
        defaults={
            'email': 'staff@example.com',
            'first_name': 'Staff',
            'last_name': 'User',
            'is_staff': True
        }
    )
    return user

def create_sample_data():
    print("=" * 70)
    print("SEEDING SAMPLE DATA: 10 Customers and 20 Orders with All Statuses")
    print("=" * 70)
    
    branch = get_or_create_branch()
    staff_user = get_or_create_user()
    now = timezone.now()
    
    # Sample customer data
    customers_data = [
        {'name': 'John Smith', 'phone': '0701234567', 'email': 'john.smith@email.com', 'type': 'personal'},
        {'name': 'Sarah Johnson', 'phone': '0701234568', 'email': 'sarah.j@email.com', 'type': 'personal'},
        {'name': 'Michael Brown', 'phone': '0701234569', 'email': 'mike.brown@email.com', 'type': 'personal'},
        {'name': 'Uganda Revenue Authority', 'phone': '0701234570', 'email': 'fleet@ura.go.ug', 'type': 'government'},
        {'name': 'Red Cross Uganda', 'phone': '0701234571', 'email': 'logistics@redcross.ug', 'type': 'ngo'},
        {'name': 'MTN Uganda Ltd', 'phone': '0701234572', 'email': 'fleet@mtn.co.ug', 'type': 'company'},
        {'name': 'David Wilson', 'phone': '0701234573', 'email': 'david.w@email.com', 'type': 'personal'},
        {'name': 'Ministry of Health', 'phone': '0701234574', 'email': 'transport@health.go.ug', 'type': 'government'},
        {'name': 'UNICEF Uganda', 'phone': '0701234575', 'email': 'ops@unicef.org', 'type': 'ngo'},
        {'name': 'Grace Nakato', 'phone': '0701234576', 'email': 'grace.n@email.com', 'type': 'personal'},
    ]
    
    # Create customers
    print("\n[1] Creating 10 Customers...")
    customers = []
    for i, customer_data in enumerate(customers_data, 1):
        customer, created = Customer.objects.get_or_create(
            phone=customer_data['phone'],
            branch=branch,
            defaults={
                'full_name': customer_data['name'],
                'email': customer_data['email'],
                'customer_type': customer_data['type'],
                'registration_date': now - timedelta(days=random.randint(30, 365)),
                'address': f"Plot {random.randint(100, 999)}, Kampala"
            }
        )
        customers.append(customer)
        status = "✓ Created" if created else "✓ Already exists"
        print(f"  {i:2d}. {customer.full_name:30s} ({customer_data['type']:12s}) {status}")
    
    # Create vehicles for each customer
    print("\n[2] Creating Vehicles for Customers...")
    vehicles = []
    vehicle_makes = ['Toyota', 'Honda', 'Nissan', 'Mercedes', 'Isuzu']
    vehicle_models = ['Camry', 'Hilux', 'Civic', 'X-Trail', 'Actros']
    
    for customer in customers:
        num_vehicles = random.randint(1, 2)
        for _ in range(num_vehicles):
            plate = f"U{random.randint(100, 999)}{random.choice('ABCDE')}"
            vehicle, created = Vehicle.objects.get_or_create(
                plate_number=plate,
                customer=customer,
                defaults={
                    'make': random.choice(vehicle_makes),
                    'model': random.choice(vehicle_models),
                    'vehicle_type': 'sedan'
                }
            )
            vehicles.append(vehicle)
            if created:
                print(f"  ✓ {vehicle.plate_number:10s} for {customer.full_name}")
    
    # Create brands and inventory items for sales orders
    print("\n[3] Creating Brands and Inventory Items...")
    brands_data = [
        {'name': 'Michelin', 'description': 'Premium tires'},
        {'name': 'Bridgestone', 'description': 'Quality tires'},
        {'name': 'Goodyear', 'description': 'Trusted brand'},
    ]
    
    brands = []
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={'description': brand_data['description']}
        )
        brands.append(brand)
        if created:
            print(f"  ✓ Brand: {brand.name}")
    
    inventory_items = []
    tire_types = ['All Season', 'Summer', 'Winter', 'Performance']
    sizes = ['195/65R15', '205/55R16', '225/45R17']
    
    for brand in brands:
        for i, tire_type in enumerate(tire_types[:2]):
            item_name = f"{tire_type} {sizes[i]}"
            item, created = InventoryItem.objects.get_or_create(
                name=item_name,
                brand=brand,
                defaults={
                    'quantity': random.randint(20, 100),
                    'price': Decimal(str(random.randint(150, 300))),
                    'reorder_level': 5
                }
            )
            inventory_items.append(item)
            if created:
                print(f"  ✓ {brand.name} - {item_name}")
    
    # Create 20 orders with different statuses
    print("\n[4] Creating 20 Orders - Auto-Progress Demonstration...")
    print("-" * 70)

    orders_by_status = {
        'created': [],
        'in_progress': [],
        'overdue': [],
        'completed': [],
        'cancelled': []
    }

    # Helper to calculate timestamps for orders
    def create_timestamps_for_status(status):
        """
        Create appropriate timestamps based on order status.

        Auto-progression timeline:
        1. created (0-9 minutes old) - stays in 'created' until 10 min elapsed
        2. in_progress (10+ minutes old) - auto-progressed by middleware after 10 min
        3. overdue (9+ working hours in progress) - marked by middleware when 9 hrs exceeded
        """
        started = None
        completed = None
        cancelled = None

        if status == 'created':
            # Orders 1-8 minutes old - will NOT auto-progress yet (< 10 min)
            # Middleware will auto-progress them once 10 minutes elapse
            created = now - timedelta(minutes=random.randint(1, 8))
            # Do NOT set started_at for created orders - middleware will set it after 10 min

        elif status == 'in_progress':
            # Orders 11-120 minutes old - already auto-progressed by middleware
            # These were created 11+ minutes ago, so middleware already set them to 'in_progress'
            # and set started_at = created_at
            created = now - timedelta(minutes=random.randint(11, 120))
            started = created  # Middleware sets started_at = created_at when auto-progressing

        elif status == 'overdue':
            # Orders that have been in progress for 9+ working hours
            # Working hours: 8 AM to 5 PM (9 hours/day)
            # Create order yesterday at 8:15 AM so it's in progress for 9+ hours
            yesterday_815am = (now - timedelta(days=1)).replace(hour=8, minute=15, second=0, microsecond=0)
            created = yesterday_815am
            started = created  # Middleware will have set this after 10 min
            # Middleware will mark as 'overdue' because:
            # From yesterday 8:15 AM to now is 9+ working hours

        elif status == 'completed':
            # Orders completed 1-30 days ago
            created = now - timedelta(days=random.randint(1, 30))
            started = created + timedelta(minutes=10)  # Was auto-progressed
            completed = started + timedelta(hours=random.randint(2, 8))

        elif status == 'cancelled':
            # Orders cancelled 1-20 days ago
            created = now - timedelta(days=random.randint(1, 20))
            started = created + timedelta(minutes=10)  # Was auto-progressed before cancelling
            cancelled = started + timedelta(minutes=random.randint(30, 240))

        return created, started, completed, cancelled

    # Create orders: 4 of each status = 20 orders
    # These are static to ensure predictable distribution
    order_statuses = [
        # created status: 4 orders (1-8 minutes old, will auto-progress after 10 min)
        'created', 'created', 'created', 'created',
        # in_progress status: 4 orders (11-120 minutes old, already auto-progressed)
        'in_progress', 'in_progress', 'in_progress', 'in_progress',
        # overdue status: 4 orders (created yesterday 8:15 AM, now 9+ working hours old)
        'overdue', 'overdue', 'overdue', 'overdue',
        # completed status: 4 orders
        'completed', 'completed', 'completed', 'completed',
        # cancelled status: 4 orders
        'cancelled', 'cancelled', 'cancelled', 'cancelled',
    ]
    
    service_descriptions = [
        'Oil change and filter replacement',
        'Brake pad replacement and inspection',
        'Tire rotation and balancing',
        'Engine tune-up and diagnostics',
        'Transmission fluid service'
    ]

    order_num = 0
    for status in order_statuses:
        order_num += 1

        # Select random customer and vehicle
        customer = random.choice(customers)
        vehicle = random.choice(customer.vehicles.all()) if customer.vehicles.exists() else None
        order_type = random.choice(['service', 'sales', 'service'])
        priority = random.choice(['low', 'medium', 'high', 'urgent'])

        # Generate timestamps based on auto-progression flow
        created_at, started_at, completed_at, cancelled_at = create_timestamps_for_status(status)

        order_data = {
            'customer': customer,
            'vehicle': vehicle,
            'branch': branch,
            'type': order_type,
            'status': status,
            'priority': priority,
            'created_at': created_at,
            'estimated_duration': random.randint(60, 480),
            'assigned_to': staff_user if random.choice([True, False]) else None,
        }

        # Set timestamps based on status
        # IMPORTANT: Only set started_at for in_progress, overdue, completed, cancelled
        # Do NOT set started_at for 'created' orders - middleware will set it after 10 minutes
        if started_at:
            order_data['started_at'] = started_at

        if completed_at:
            order_data['completed_at'] = completed_at
            order_data['completion_date'] = completed_at

        if cancelled_at:
            order_data['cancelled_at'] = cancelled_at
            order_data['cancellation_reason'] = random.choice([
                'Customer request',
                'Parts unavailable',
                'Weather conditions',
                'Customer no-show'
            ])

        # Type-specific data
        if order_type == 'service':
            order_data['description'] = random.choice(service_descriptions)
        elif order_type == 'sales':
            item = random.choice(inventory_items)
            order_data['item_name'] = item.name
            order_data['brand'] = item.brand.name
            order_data['quantity'] = random.randint(1, 4)
            order_data['tire_type'] = 'New'

        try:
            order = Order.objects.create(**order_data)
            orders_by_status[status].append(order)

            # Update customer visit tracking
            customer.total_visits = (customer.total_visits or 0) + 1
            customer.last_visit = created_at
            customer.save(update_fields=['total_visits', 'last_visit'])

            # Display order with timestamp info
            status_display = status.replace('_', ' ').upper().ljust(12)
            age_info = ""
            if status == 'created':
                minutes_ago = int((now - created_at).total_seconds() / 60)
                age_info = f" (created {minutes_ago} min ago)"
            elif status == 'in_progress':
                minutes_ago = int((now - created_at).total_seconds() / 60)
                age_info = f" (auto-progressed {minutes_ago} min ago)"
            elif status == 'overdue':
                hours_ago = (now - created_at).total_seconds() / 3600
                age_info = f" (in progress {hours_ago:.1f} hours)"

            print(f"{order_num:2d}. {order.order_number:20s} | {customer.full_name:25s} | {status_display} | {order_type.upper()}{age_info}")
        except Exception as e:
            print(f"  ✗ Error creating order: {e}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY - AUTO-PROGRESSION LIFECYCLE")
    print("=" * 70)

    print(f"\nData Created:")
    print(f"  Customers : {len(customers)}")
    print(f"  Vehicles  : {len(vehicles)}")
    print(f"  Total Orders : {sum(len(orders) for orders in orders_by_status.values())}")

    print("\n" + "-" * 70)
    print("Auto-Progression Flow (Middleware Driven):")
    print("-" * 70)
    print("""
1. CREATED (1-8 minutes old)
   → Stays in 'created' status until 10 minutes elapse
   → Middleware checks and auto-progresses when created_at + 10 min < now
   → started_at will be set to created_at by middleware

2. IN PROGRESS (11+ minutes old)
   → Auto-progressed from 'created' by middleware
   → started_at = created_at (the moment it was created)
   → Actively being worked on

3. OVERDUE (9+ working hours in progress)
   → Orders in 'in_progress' for 9+ working hours marked as 'overdue'
   → Working hours: 8 AM - 5 PM (9 hours/day)
   → Calculated by middleware based on started_at
   → Example: Created yesterday 8:15 AM → now is 9+ working hours elapsed

4. COMPLETED
   → Orders finished with completed_at timestamp

5. CANCELLED
   → Orders cancelled with cancellation_reason
""")

    print("-" * 70)
    print("Order Distribution by Status:")
    print("-" * 70)
    for status, orders in orders_by_status.items():
        if orders:
            oldest = min(o.created_at for o in orders)
            time_diff = (now - oldest).total_seconds() / 3600
            print(f"  {status.replace('_', ' ').title():12s} : {len(orders):2d} orders (oldest: {time_diff:.1f} hours ago)")

    print("\n" + "-" * 70)
    print("Order Distribution by Type:")
    print("-" * 70)
    service_count = Order.objects.filter(type='service').count()
    sales_count = Order.objects.filter(type='sales').count()
    inquiry_count = Order.objects.filter(type='inquiry').count()
    print(f"  Service : {service_count:2d} orders")
    print(f"  Sales   : {sales_count:2d} orders")
    print(f"  Inquiry : {inquiry_count:2d} orders")

    print("\n" + "-" * 70)
    print("Customer Visit Tracking:")
    print("-" * 70)
    for customer in customers:
        visit_count = customer.total_visits
        order_count = customer.orders.count()
        print(f"  {customer.full_name:30s} | Visits: {visit_count:2d} | Orders: {order_count:2d}")

    print("\n" + "=" * 70)
    print("✓ Sample data seeding completed successfully!")
    print("\nNote: The middleware will automatically:")
    print("  • Auto-progress 'created' orders to 'in_progress' after 10 minutes")
    print("  • Mark 'in_progress' orders as 'overdue' when 9 working hours exceeded")
    print("=" * 70)

if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n✗ Error during data seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
