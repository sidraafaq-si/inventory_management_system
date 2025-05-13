
from abc import ABC, abstractmethod
import json
from datetime import datetime

# Custom Exceptions
class DuplicateProductIDException(Exception):
    pass

class InsufficientStockException(Exception):
    pass

class InvalidProductDataException(Exception):
    pass

# Abstract Base Class
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
            raise InsufficientStockException("Not enough stock to sell.")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock

    @abstractmethod
    def __str__(self):
        pass

# Subclasses
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, warranty_years, brand):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.warranty_years = warranty_years
        self.brand = brand

    def __str__(self):
        return f"[Electronics] {self._name} (ID: {self._product_id}, Brand: {self.brand}, Warranty: {self.warranty_years} yrs, Price: {self._price}, Stock: {self._quantity_in_stock})"

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")

    def is_expired(self):
        return datetime.now() > self.expiry_date

    def __str__(self):
        return f"[Grocery] {self._name} (ID: {self._product_id}, Expiry: {self.expiry_date.date()}, Price: {self._price}, Stock: {self._quantity_in_stock})"

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.size = size
        self.material = material

    def __str__(self):
        return f"[Clothing] {self._name} (ID: {self._product_id}, Size: {self.size}, Material: {self.material}, Price: {self._price}, Stock: {self._quantity_in_stock})"

# Inventory Class
class Inventory:
    def __init__(self):
        self._products = {}

    def add_product(self, product):
        if product._product_id in self._products:
            raise DuplicateProductIDException("Product with this ID already exists.")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        self._products.pop(product_id, None)

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if isinstance(p, product_type)]

    def list_all_products(self):
        return list(self._products.values())

    def sell_product(self, product_id, quantity):
        if product_id in self._products:
            self._products[product_id].sell(quantity)

    def restock_product(self, product_id, quantity):
        if product_id in self._products:
            self._products[product_id].restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        expired_ids = [pid for pid, p in self._products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired_ids:
            del self._products[pid]

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump({pid: self.serialize_product(p) for pid, p in self._products.items()}, f, indent=4)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self._products = {pid: self.deserialize_product(info) for pid, info in data.items()}
        except Exception as e:
            raise InvalidProductDataException(f"Error loading file: {e}")

    def serialize_product(self, product):
        base = {
            "type": type(product).__name__,
            "product_id": product._product_id,
            "name": product._name,
            "price": product._price,
            "quantity_in_stock": product._quantity_in_stock
        }
        if isinstance(product, Electronics):
            base.update({"warranty_years": product.warranty_years, "brand": product.brand})
        elif isinstance(product, Grocery):
            base.update({"expiry_date": product.expiry_date.strftime("%Y-%m-%d")})
        elif isinstance(product, Clothing):
            base.update({"size": product.size, "material": product.material})
        return base

    def deserialize_product(self, data):
        t = data["type"]
        if t == "Electronics":
            return Electronics(data["product_id"], data["name"], data["price"], data["quantity_in_stock"], data["warranty_years"], data["brand"])
        elif t == "Grocery":
            return Grocery(data["product_id"], data["name"], data["price"], data["quantity_in_stock"], data["expiry_date"])
        elif t == "Clothing":
            return Clothing(data["product_id"], data["name"], data["price"], data["quantity_in_stock"], data["size"], data["material"])
        else:
            raise InvalidProductDataException("Unknown product type.")

# CLI Interface
if __name__ == "__main__":
    inventory = Inventory()

    while True:
        print("\n--- Inventory Management Menu ---")
        print("1. Add Product")
        print("2. Sell Product")
        print("3. View All Products")
        print("4. Search Product by Name")
        print("5. Save Inventory to File")
        print("6. Load Inventory from File")
        print("7. Remove Expired Products")
        print("8. Exit")
        choice = input("Enter your choice: ")

        try:
            if choice == '1':
                p_type = input("Enter type (Electronics/Grocery/Clothing): ").strip().lower()
                pid = input("Product ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))
                if p_type == 'electronics':
                    warranty = int(input("Warranty (years): "))
                    brand = input("Brand: ")
                    p = Electronics(pid, name, price, qty, warranty, brand)
                elif p_type == 'grocery':
                    expiry = input("Expiry Date (YYYY-MM-DD): ")
                    p = Grocery(pid, name, price, qty, expiry)
                elif p_type == 'clothing':
                    size = input("Size: ")
                    material = input("Material: ")
                    p = Clothing(pid, name, price, qty, size, material)
                else:
                    print("Invalid type!")
                    continue
                inventory.add_product(p)
                print("Product added.")

            elif choice == '2':
                pid = input("Enter Product ID: ")
                qty = int(input("Quantity to Sell: "))
                inventory.sell_product(pid, qty)
                print("Product sold.")

            elif choice == '3':
                for p in inventory.list_all_products():
                    print(p)

            elif choice == '4':
                name = input("Enter name to search: ")
                results = inventory.search_by_name(name)
                for r in results:
                    print(r)

            elif choice == '5':
                fname = input("Enter filename to save: ")
                inventory.save_to_file(fname)
                print("Inventory saved.")

            elif choice == '6':
                fname = input("Enter filename to load: ")
                inventory.load_from_file(fname)
                print("Inventory loaded.")

            elif choice == '7':
                inventory.remove_expired_products()
                print("Expired products removed.")

            elif choice == '8':
                print("Exiting... Goodbye!")
                break
            else:
                print("Invalid choice!")

        except Exception as e:
            print(f"Error: {e}")
