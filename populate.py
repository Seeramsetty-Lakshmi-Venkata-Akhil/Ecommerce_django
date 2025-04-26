import os
import django
import random
from decimal import Decimal

# Setup Django (only if you run separately)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_application.settings')
django.setup()

from products.models import User, Products, Category, Order, OrderProduct

# Clear existing data (optional, be careful!)
User.objects.all().delete()
Products.objects.all().delete()
Category.objects.all().delete()
Order.objects.all().delete()
OrderProduct.objects.all().delete()

# Create Categories
categories = []
for name in ['Electronics', 'Clothing', 'Books', 'Home', 'Toys']:
    cat = Category.objects.create(name=name)
    categories.append(cat)
print(f"✅ Created {len(categories)} Categories")

# Create Users
users = []
for i in range(10):
    user = User.objects.create(name=f"User{i+1}")
    users.append(user)
print(f"✅ Created {len(users)} Users")

# Create Products
products = []
for i in range(10):
    product = Products.objects.create(
        name=f"Product{i+1}",
        price=Decimal(random.randint(100, 5000)),
        description=f"Description for product {i+1}",
        is_available=True,
        category=random.choice(categories)
    )
    products.append(product)
print(f"✅ Created {len(products)} Products")

# Create Orders
for i in range(5):
    order = Order.objects.create(
        user=random.choice(users),
        order_status=random.choice([Order.OrderStatus.PENDING, Order.OrderStatus.SUCCESS])
    )
    # Add random products to the order
    selected_products = random.sample(products, random.randint(1, 4))
    for prod in selected_products:
        OrderProduct.objects.create(
            order=order,
            product=prod,
            quantity=random.randint(1, 5)
        )
print(f"✅ Created 5 Orders with products")

print("🎉 Data population complete!")
