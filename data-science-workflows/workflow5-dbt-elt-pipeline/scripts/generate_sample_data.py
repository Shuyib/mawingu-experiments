"""
Generate sample e-commerce data for the dbt ELT pipeline.

This script creates realistic sample data for customers, products, and orders
that will be used to demonstrate the dbt transformations.
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)


def generate_customers(num_customers=1000):
    """Generate sample customer data."""
    customers = []
    for customer_id in range(1, num_customers + 1):
        customer = {
            'customer_id': customer_id,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'country': 'USA',
            'created_at': fake.date_time_between(start_date='-3y', end_date='now').isoformat()
        }
        customers.append(customer)
    return customers


def generate_products(num_products=200):
    """Generate sample product data."""
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys']
    products = []
    
    for product_id in range(1, num_products + 1):
        product = {
            'product_id': product_id,
            'product_name': fake.word().capitalize() + ' ' + fake.word().capitalize(),
            'category': random.choice(categories),
            'price': round(random.uniform(9.99, 999.99), 2),
            'cost': round(random.uniform(5.00, 500.00), 2),
            'created_at': fake.date_time_between(start_date='-2y', end_date='-6m').isoformat()
        }
        # Ensure price > cost
        if product['price'] < product['cost']:
            product['price'] = product['cost'] * 1.5
        products.append(product)
    return products


def generate_orders(num_orders=5000, num_customers=1000, num_products=200):
    """Generate sample order data."""
    orders = []
    order_id = 1
    
    for _ in range(num_orders):
        customer_id = random.randint(1, num_customers)
        order_date = fake.date_time_between(start_date='-2y', end_date='now')
        num_items = random.randint(1, 5)
        
        # Generate order items
        selected_products = random.sample(range(1, num_products + 1), num_items)
        
        for product_id in selected_products:
            order = {
                'order_id': order_id,
                'customer_id': customer_id,
                'product_id': product_id,
                'quantity': random.randint(1, 5),
                'order_date': order_date.isoformat(),
                'status': random.choices(
                    ['completed', 'pending', 'cancelled', 'refunded'],
                    weights=[80, 10, 7, 3]
                )[0]
            }
            orders.append(order)
            order_id += 1
    
    return orders


def save_to_csv(data, filename, fieldnames):
    """Save data to CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filename} with {len(data)} rows")


def main():
    """Generate all sample datasets."""
    print("Generating sample e-commerce data...")
    
    # Generate data
    customers = generate_customers(1000)
    products = generate_products(200)
    orders = generate_orders(5000, 1000, 200)
    
    # Save to CSV
    save_to_csv(
        customers,
        'data/customers.csv',
        ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'country', 'created_at']
    )
    
    save_to_csv(
        products,
        'data/products.csv',
        ['product_id', 'product_name', 'category', 'price', 'cost', 'created_at']
    )
    
    save_to_csv(
        orders,
        'data/orders.csv',
        ['order_id', 'customer_id', 'product_id', 'quantity', 'order_date', 'status']
    )
    
    print("\nSample data generation complete!")
    print("Files created:")
    print("  - data/customers.csv")
    print("  - data/products.csv")
    print("  - data/orders.csv")


if __name__ == '__main__':
    main()
