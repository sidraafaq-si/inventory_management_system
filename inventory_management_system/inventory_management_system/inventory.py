from abc import ABC, abstractmethod
from datetime import datetime
import json

# Abstract Product Class
class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    def restock(self, amount):
        self._quantity_in_stock += amount

    def sell(self, quantity):
        if quantity > self._quantity_in_stock:
            raise ValueError(f"Only {self._quantity_in_stock} items available.")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock

    @abstractmethod
    def __str__(self):
        pass

# Subclasses
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity, brand, warranty_years):
        super().__init__(product_id, name, price, quantity)
        self.brand = brand
        self.warranty_years = warranty_years

    def __str__(self):
        return f"[Electronics] ID: {self._product_id}, Name: {self._name}, Brand: {self.brand}, Price: {self._price}, Qty: {self._quantity_in_stock}, Warranty: {self.warranty_years} years"

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity, expiry_date):
        super().__init__(product_id, name, price, quantity)
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")

    def is_expired(self):
        return datetime.now() > self.expiry_date

    def __str__(self):
        status = "Expired" if self.is_expired() else "Fresh"
        return f"[Grocery] ID: {self._product_id}, Name: {self._name}, Price: {self._price}, Qty: {self._quantity_in_stock}, Expiry: {self.expiry_date.date()} ({status})"

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity, size, material):
        super().__init__(product_id, name, price, quantity)
        self.size = size
        self.material = material

    def __str__(self):
        return f"[Clothing] ID: {self._product_id}, Name: {self._name}, Price: {self._price}, Qty: {self._quantity_in_stock}, Size: {self.size}, Material: {self.material}"

# Inventory Class
class Inventory:
    def __init__(self):
        self._products = {}

    def add_product(self, product):
        if product._product_id in self._products:
            raise ValueError("Duplicate product ID.")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        if product_id in self._products:
            del self._products[product_id]

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if p.__class__.__name__.lower() == product_type.lower()]

    def list_all_products(self):
        return list(self._products.values())

    def sell_product(self, product_id, quantity):
        if product_id not in self._products:
            raise ValueError("Product not found.")
        self._products[product_id].sell(quantity)

    def restock_product(self, product_id, quantity):
        if product_id not in self._products:
            raise ValueError("Product not found.")
        self._products[product_id].restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        expired_ids = [pid for pid, p in self._products.items()
                       if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired_ids:
            del self._products[pid]

    def save_to_file(self, filename):
        data = []
        for p in self._products.values():
            p_data = p.__dict__.copy()
            p_data["type"] = p.__class__.__name__
            if isinstance(p, Grocery):
                p_data["expiry_date"] = p.expiry_date.strftime("%Y-%m-%d")
            data.append(p_data)
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self._products = {}
            for item in data:
                type_ = item.pop("type")
                if type_ == "Electronics":
                    obj = Electronics(**item)
                elif type_ == "Grocery":
                    obj = Grocery(**item)
                elif type_ == "Clothing":
                    obj = Clothing(**item)
                else:
                    raise ValueError(f"Unknown product type: {type_}")
                self._products[obj._product_id] = obj
        except Exception as e:
            raise ValueError("Failed to load inventory data.") from e

# CLI Menu
def cli():
    inv = Inventory()
    while True:
        print("\nInventory Menu")
        print("1. Add Product")
        print("2. Sell Product")
        print("3. Search Product")
        print("4. View All Products")
        print("5. Save to File")
        print("6. Load from File")
        print("7. Total Inventory Value")
        print("8. Remove Expired Products")
        print("9. Exit")
        
        choice = input("Enter choice: ")
        try:
            if choice == "1":
                print("Product Types: Electronics, Grocery, Clothing")
                type_ = input("Enter product type: ").capitalize()
                pid = input("Product ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))

                if type_ == "Electronics":
                    brand = input("Brand: ")
                    warranty = int(input("Warranty (years): "))
                    product = Electronics(pid, name, price, qty, brand, warranty)
                elif type_ == "Grocery":
                    expiry = input("Expiry date (YYYY-MM-DD): ")
                    product = Grocery(pid, name, price, qty, expiry)
                elif type_ == "Clothing":
                    size = input("Size: ")
                    material = input("Material: ")
                    product = Clothing(pid, name, price, qty, size, material)
                else:
                    print("Invalid product type.")
                    continue
                inv.add_product(product)
                print("Product added.")
            elif choice == "2":
                pid = input("Enter Product ID: ")
                qty = int(input("Quantity: "))
                inv.sell_product(pid, qty)
            elif choice == "3":
                name = input("Enter product name to search: ")
                results = inv.search_by_name(name)
                for p in results:
                    print(p)
            elif choice == "4":
                for p in inv.list_all_products():
                    print(p)
            elif choice == "5":
                inv.save_to_file("inventory.json")
                print("Inventory saved.")
            elif choice == "6":
                inv.load_from_file("inventory.json")
                print("Inventory loaded.")
            elif choice == "7":
                print(f"Total Value: {inv.total_inventory_value()}")
            elif choice == "8":
                inv.remove_expired_products()
                print("Expired products removed.")
            elif choice == "9":
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print("Error:", e)
