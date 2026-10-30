"""Generate a realistic synthetic e-commerce CSV for the data warehouse project.

Usage:  python generate_data.py            -> writes data/sample_ecommerce.csv
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
N_ORDERS = 2500
START, END = date(2025, 1, 1), date(2026, 10, 31)
OUT = Path(__file__).resolve().parent / "data" / "sample_ecommerce.csv"

CITIES = {
    "Delhi": 14, "Noida": 11, "Greater Noida": 8, "Ghaziabad": 8,
    "Gurugram": 9, "Faridabad": 4, "Mumbai": 10, "Pune": 6,
    "Bengaluru": 9, "Hyderabad": 6, "Chennai": 5, "Kolkata": 4,
    "Jaipur": 3, "Lucknow": 3, "Ahmedabad": 3, "Chandigarh": 2,
}
FIRST = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karan", "Rahul", "Amit",
         "Sanjay", "Vikram", "Neha", "Priya", "Anjali", "Pooja", "Sneha", "Kavya",
         "Riya", "Isha", "Meera", "Divya", "Nikhil", "Manish", "Deepak", "Sakshi"]
LAST = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Yadav", "Mishra", "Jain",
        "Agarwal", "Patel", "Reddy", "Nair", "Iyer", "Das", "Chauhan", "Tiwari"]

PRODUCTS = [
    ("Wireless Mouse", "Electronics", 599), ("USB-C Cable", "Electronics", 245),
    ("Bluetooth Earbuds", "Electronics", 1499), ("Power Bank 10000mAh", "Electronics", 1199),
    ("Phone Stand", "Electronics", 349), ("Mechanical Keyboard", "Electronics", 2799),
    ("Smart Watch", "Electronics", 3299), ("Webcam HD", "Electronics", 1899),
    ("Desk Organizer", "Home", 749), ("Water Bottle", "Home", 324),
    ("LED Desk Lamp", "Home", 899), ("Storage Box Set", "Home", 649),
    ("Wall Clock", "Home", 549), ("Cushion Cover Pack", "Home", 429),
    ("Notebook Pack", "Stationery", 120), ("Gel Pen Set", "Stationery", 99),
    ("Sticky Notes", "Stationery", 79), ("Office Planner", "Stationery", 299),
    ("Running Shoes", "Fashion", 2199), ("Cotton T-Shirt", "Fashion", 499),
    ("Denim Jeans", "Fashion", 1299), ("Backpack", "Fashion", 999),
    ("Face Wash", "Beauty", 249), ("Moisturizer", "Beauty", 399),
    ("Hair Dryer", "Beauty", 1099), ("Yoga Mat", "Sports", 699),
    ("Dumbbell Set", "Sports", 1799), ("Skipping Rope", "Sports", 199),
    ("Python Programming Book", "Books", 449), ("SQL Handbook", "Books", 379),
]
PAY = (["UPI"] * 40 + ["Card"] * 25 + ["Cash on Delivery"] * 15 +
       ["Wallet"] * 12 + ["Net Banking"] * 8)

cities, weights = zip(*CITIES.items())
customers = []
for i in range(1, 481):
    customers.append((f"C{i:04d}", f"{random.choice(FIRST)} {random.choice(LAST)}",
                      random.choices(cities, weights)[0]))
products = [(f"P{100 + i}", n, c, p) for i, (n, c, p) in enumerate(PRODUCTS, 1)]

days = (END - START).days + 1
all_days = [START + timedelta(d) for d in range(days)]
def day_weight(d):
    w = 1 + 0.6 * ((d - START).days / days)
    w *= {10: 1.35, 11: 1.5, 12: 1.4, 1: 0.85}.get(d.month, 1.0)
    return w * (1.15 if d.weekday() >= 5 else 1.0)
order_dates = sorted(random.choices(all_days, [day_weight(d) for d in all_days], k=N_ORDERS))

rows = []
for n, d in enumerate(order_dates, 1):
    cid, cname, city = random.choice(customers)
    pid, pname, cat, base = random.choice(products)
    qty = random.choices([1, 2, 3, 4, 5], [55, 25, 12, 5, 3])[0]
    price = round(base * random.uniform(0.95, 1.08))
    gross = qty * price
    discount = round(gross * random.choice([0, 0, 0, 0.05, 0.10, 0.15]))
    age = (END - d).days
    if age > 20:
        status = random.choices(["Completed", "Cancelled"], [92, 8])[0]
    else:
        status = random.choices(["Completed", "Shipped", "Pending", "Cancelled"],
                                [55, 20, 17, 8])[0]
    rows.append([f"ORD{10000 + n}", d.isoformat(), cid, cname, city, pid, pname, cat,
                 qty, price, discount, random.choice(PAY), status])

dirty = []
for r in random.sample(rows, 30):
    dirty.append(list(r))
for r in random.sample(rows, 12):
    x = list(r); x[0] = x[0] + "X"; x[8] = ""; dirty.append(x)
for r in random.sample(rows, 8):
    x = list(r); x[0] = x[0] + "Y"; x[8] = -1; dirty.append(x)
for r in random.sample(rows, 8):
    x = list(r); x[0] = x[0] + "Z"; x[1] = "not-a-date"; dirty.append(x)
for r in random.sample(rows, 20):
    r[3] = f"  {r[3]} "; r[7] = f"{r[7]}  "
rows.extend(dirty)
random.shuffle(rows)

OUT.parent.mkdir(parents=True, exist_ok=True)
header = ["order_id", "order_date", "customer_id", "customer_name", "city",
          "product_id", "product_name", "category", "quantity", "unit_price",
          "discount", "payment_method", "order_status"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(rows)
print(f"Wrote {len(rows)} rows ({N_ORDERS} valid orders + {len(dirty)} dirty) to {OUT}")