import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)

# Function to generate sales data
def generate_sales_data(num_records=1000):
    """Generate random sales transaction data"""
    
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 
                'Webcam', 'USB Cable', 'HDMI Cable', 'Desk Chair', 'Standing Desk']
    
    categories = {
        'Laptop': 'Electronics', 'Mouse': 'Accessories', 'Keyboard': 'Accessories',
        'Monitor': 'Electronics', 'Headphones': 'Accessories', 'Webcam': 'Electronics',
        'USB Cable': 'Accessories', 'HDMI Cable': 'Accessories', 
        'Desk Chair': 'Furniture', 'Standing Desk': 'Furniture'
    }
    
    prices = {
        'Laptop': (800, 2500), 'Mouse': (15, 80), 'Keyboard': (30, 150),
        'Monitor': (200, 800), 'Headphones': (50, 300), 'Webcam': (40, 150),
        'USB Cable': (5, 25), 'HDMI Cable': (8, 40), 
        'Desk Chair': (150, 600), 'Standing Desk': (300, 1200)
    }
    
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_records):
        product = random.choice(products)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(*prices[product]), 2)
        total_price = round(quantity * unit_price, 2)
        
        data.append({
            'Transaction_ID': f'TXN{i+1:05d}',
            'Date': start_date + timedelta(days=random.randint(0, 730)),
            'Product': product,
            'Category': categories[product],
            'Quantity': quantity,
            'Unit_Price': unit_price,
            'Total_Price': total_price,
            'Customer_Name': fake.name(),
            'Region': random.choice(regions),
            'Sales_Rep': fake.name(),
            'Payment_Method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Cash']),
            'Discount_Applied': random.choice([0, 5, 10, 15, 20]) if random.random() > 0.7 else 0
        })
    
    return pd.DataFrame(data)

# Function to generate employee data
def generate_employee_data(num_records=200):
    """Generate random employee data"""
    
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    positions = {
        'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager'],
        'Sales': ['Sales Rep', 'Account Manager', 'Sales Director'],
        'Marketing': ['Marketing Specialist', 'Content Writer', 'Marketing Manager'],
        'HR': ['HR Coordinator', 'Recruiter', 'HR Manager'],
        'Finance': ['Accountant', 'Financial Analyst', 'Finance Manager'],
        'Operations': ['Operations Specialist', 'Operations Manager']
    }
    
    data = []
    
    for i in range(num_records):
        department = random.choice(departments)
        hire_date = fake.date_between(start_date='-10y', end_date='today')
        
        data.append({
            'Employee_ID': f'EMP{i+1:04d}',
            'Name': fake.name(),
            'Email': fake.email(),
            'Department': department,
            'Position': random.choice(positions[department]),
            'Hire_Date': hire_date,
            'Salary': random.randint(40000, 150000),
            'Age': random.randint(22, 65),
            'City': fake.city(),
            'Years_of_Experience': random.randint(0, 20),
            'Performance_Rating': round(random.uniform(2.5, 5.0), 1)
        })
    
    return pd.DataFrame(data)

# Function to generate e-commerce data
def generate_ecommerce_data(num_records=500):
    """Generate random e-commerce data"""
    
    data = []
    
    for i in range(num_records):
        order_date = fake.date_between(start_date='-2y', end_date='today')
        delivered = random.random() > 0.1
        
        data.append({
            'Order_ID': f'ORD{i+1:06d}',
            'Order_Date': order_date,
            'Customer_ID': f'CUST{random.randint(1, 100):04d}',
            'Customer_Email': fake.email(),
            'Product_Name': fake.catch_phrase(),
            'Product_Category': random.choice(['Books', 'Electronics', 'Clothing', 'Home & Garden', 'Sports']),
            'Price': round(random.uniform(10, 500), 2),
            'Quantity': random.randint(1, 10),
            'Shipping_Cost': round(random.uniform(5, 30), 2),
            'Status': 'Delivered' if delivered else random.choice(['Pending', 'Shipped', 'Cancelled']),
            'Delivery_Date': order_date + timedelta(days=random.randint(2, 14)) if delivered else None,
            'Rating': random.randint(1, 5) if delivered else None
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate different datasets
    print("Generating datasets...")
    
    # Sales data
    sales_df = generate_sales_data(1000)
    sales_df.to_csv('data/sales_data.csv', index=False)
    print(f"✓ Generated sales_data.csv with {len(sales_df)} records")
    
    # Employee data
    employee_df = generate_employee_data(200)
    employee_df.to_csv('data/employee_data.csv', index=False)
    employee_df.to_excel('data/employee_data.xlsx', index=False)
    print(f"✓ Generated employee_data.csv and .xlsx with {len(employee_df)} records")
    
    # E-commerce data
    ecommerce_df = generate_ecommerce_data(500)
    ecommerce_df.to_csv('data/ecommerce_data.csv', index=False)
    print(f"✓ Generated ecommerce_data.csv with {len(ecommerce_df)} records")
    
    print("\nDataset summaries:")
    print("\n--- Sales Data ---")
    print(sales_df.head())
    print(f"\nColumns: {sales_df.columns.tolist()}")
    
    print("\n--- Employee Data ---")
    print(employee_df.head())
    print(f"\nColumns: {employee_df.columns.tolist()}")
    
    print("\n--- E-commerce Data ---")
    print(ecommerce_df.head())
    print(f"\nColumns: {ecommerce_df.columns.tolist()}")

