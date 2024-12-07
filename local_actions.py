import random

def get_user_data():
    """Return a list of key/value pairs for the table."""
    return [
        {"Name": "Alice", "Age": str(random.randint(20, 60)), "Department": "HR", "Location": "New York", "Years": "5"},
        {"Name": "Bob", "Age": str(random.randint(20, 60)), "Department": "Engineering", "Location": "San Francisco", "Years": "2"},
        {"Name": "Charlie", "Age": str(random.randint(20, 60)), "Department": "Marketing", "Location": "Chicago", "Years": "8"},
        {"Name": "Diana", "Age": str(random.randint(20, 60)), "Department": "Design", "Location": "Seattle", "Years": "3"},
        {"Name": "Evan", "Age": str(random.randint(20, 60)), "Department": "Management", "Location": "Boston", "Years": "10"},
        {"Name": "Fiona", "Age": str(random.randint(20, 60)), "Department": "Finance", "Location": "Austin", "Years": "6"},
        {"Name": "Grace", "Age": str(random.randint(20, 60)), "Department": "Customer Support", "Location": "Miami", "Years": "4"},
        {"Name": "Henry", "Age": str(random.randint(20, 60)), "Department": "IT", "Location": "Dallas", "Years": "15"},
        {"Name": "Isabel", "Age": str(random.randint(20, 60)), "Department": "Sales", "Location": "Denver", "Years": "1"},
        {"Name": "Jack", "Age": str(random.randint(20, 60)), "Department": "Legal", "Location": "Atlanta", "Years": "2"},
        {"Name": "Karen", "Age": str(random.randint(20, 60)), "Department": "R&D", "Location": "Portland", "Years": "7"},
        {"Name": "Leo", "Age": str(random.randint(20, 60)), "Department": "Operations", "Location": "Las Vegas", "Years": "12"},
        {"Name": "Mia", "Age": str(random.randint(20, 60)), "Department": "Training", "Location": "Phoenix", "Years": "3"},
        {"Name": "Nathan", "Age": str(random.randint(20, 60)), "Department": "Procurement", "Location": "Philadelphia", "Years": "20"},
        {"Name": "Olivia", "Age": str(random.randint(20, 60)), "Department": "Logistics", "Location": "Houston", "Years": "6"},
        {"Name": "Paul", "Age": str(random.randint(20, 60)), "Department": "Accounting", "Location": "Detroit", "Years": "13"},
        {"Name": "Quincy", "Age": str(random.randint(20, 60)), "Department": "Admin", "Location": "Charlotte", "Years": "10"}
    ]
