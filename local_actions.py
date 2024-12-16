import random


def get_user_data():
    """Return a list of key/value pairs for the table."""
    return [
        {"name": "Alice", "age": str(random.randint(20, 60)), "department": "HR", "location": "New York", "years": "5"},
        {"name": "Bob", "age": str(random.randint(20, 60)), "department": "Engineering", "location": "San Francisco", "years": "2"},
        {"name": "Charlie", "age": str(random.randint(20, 60)), "department": "Marketing", "location": "Chicago", "years": "8"},
        {"name": "Diana", "age": str(random.randint(20, 60)), "department": "Design", "location": "Seattle", "years": "3"},
        {"name": "Evan", "age": str(random.randint(20, 60)), "department": "Management", "location": "Boston", "years": "10"},
        {"name": "Fiona", "age": str(random.randint(20, 60)), "department": "Finance", "location": "Austin", "years": "6"},
        {"name": "Grace", "age": str(random.randint(20, 60)), "department": "Customer Support", "location": "Miami", "years": "4"},
        {"name": "Henry", "age": str(random.randint(20, 60)), "department": "IT", "location": "Dallas", "years": "15"},
        {"name": "Isabel", "age": str(random.randint(20, 60)), "department": "Sales", "location": "Denver", "years": "1"},
        {"name": "Jack", "age": str(random.randint(20, 60)), "department": "Legal", "location": "Atlanta", "years": "2"},
        {"name": "Karen", "age": str(random.randint(20, 60)), "department": "R&D", "location": "Portland", "years": "7"},
        {"name": "Leo", "age": str(random.randint(20, 60)), "department": "Operations", "location": "Las Vegas", "years": "12"},
        {"name": "Mia", "age": str(random.randint(20, 60)), "department": "Training", "location": "Phoenix", "years": "3"},
        {"name": "Nathan", "age": str(random.randint(20, 60)), "department": "Procurement", "location": "Philadelphia", "years": "20"},
        {"name": "Olivia", "age": str(random.randint(20, 60)), "department": "Logistics", "location": "Houston", "years": "6"},
        {"name": "Paul", "age": str(random.randint(20, 60)), "department": "Accounting", "location": "Detroit", "years": "13"},
        {"name": "Quincy", "age": str(random.randint(20, 60)), "department": "Admin", "location": "Charlotte", "years": "10"}
    ]
