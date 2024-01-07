from abc import ABC, abstractmethod
import csv, os

# Abstract Singleton Pattern - AbstractVegetableInventoryManager
class AbstractVegetableInventoryManager(ABC):
    @abstractmethod
    def add_observer(self, observer):
        pass
    
    @abstractmethod
    def remove_observer(self, observer):
        pass

    @abstractmethod    
    def notify_observers(self, vegetable_name, new_stock):
        pass
    
    @abstractmethod
    def add_item(self, vegetable):
        pass

    @abstractmethod
    def update_stock(self, vegetable_name, new_stock):
        pass

    @abstractmethod
    def display_stock(self):
        pass

# Abstract Observer Pattern - AbstractObserver
class AbstractObserver:
    def update(self, vegetable_name, new_stock):
        pass

# Concrete Observer Pattern - StockObserver
class StockObserver(AbstractObserver):
    def update(self, vegetable_name, new_stock):
        print(f"Notification: {vegetable_name} stock updated to {new_stock}")

# Abstract Command Pattern - AbstractOperation
class AbstractOperation:
    def execute(self):
        pass

    def undo(self):
        pass

# Concrete Command Pattern - UpdateStockCommand
class UpdateStockCommand(AbstractOperation):
    def __init__(self, manager, vegetable_name, new_stock):
        self.manager = manager
        self.vegetable_name = vegetable_name
        self.new_stock = new_stock
        self.old_stock = None

    def execute(self):
        self.old_stock = self.manager.update_stock(self.vegetable_name, self.new_stock)

    def undo(self):
        if self.old_stock is not None:
            self.manager.update_stock(self.vegetable_name, self.old_stock)

# Concrete Singleton Pattern - VegetableInventoryManager
class VegetableInventoryManager(AbstractVegetableInventoryManager):
    _instance = None
    _observers = []
    _csv_file_path = 'vegetable_inventory.csv'

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(VegetableInventoryManager, cls).__new__(cls)
            cls._instance.inventory = {}
        return cls._instance

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, vegetable_name, new_stock):
        for observer in self._observers:
            observer.update(vegetable_name, new_stock)

    def add_item(self, vegetable):
        if vegetable.name not in self.inventory:
            self.inventory[vegetable.name] = {
                'description': vegetable.description,
                'price': vegetable.price,
                'num_items': vegetable.num_items,
                'image': vegetable.image
            }
            self.write_to_csv()
        else:
            self.inventory[vegetable.name]['description'] = vegetable.description
            self.inventory[vegetable.name]['price'] = vegetable.price
            self.inventory[vegetable.name]['num_items'] += vegetable.num_items
            self.write_to_csv()

    def update_stock(self, vegetable_name, new_stock):
        if vegetable_name in self.inventory:
            old_stock = self.inventory[vegetable_name]['num_items']
            old_stock= int(old_stock)
            stock = old_stock  + int(new_stock)
            self.notify_observers(vegetable_name, new_stock)
            self.write_to_csv()
            return old_stock
        else:
            return None

    def display_stock(self):
        return self.inventory

    def write_to_csv(self):
        with open(self._csv_file_path, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Description', 'Price', 'Number of Items', 'Image']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for name, data in self.inventory.items():
                writer.writerow({
                    'Name': name,
                    'Description': data['description'],
                    'Price': data['price'],
                    'Number of Items': data['num_items'],
                    'Image': data['image']
                })

    def load_from_csv(self):
        if os.path.exists(self._csv_file_path):
            with open(self._csv_file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row['Name']
                    description = row['Description']
                    price_str = row['Price']
                    try:
                        price = float(price_str)
                    except ValueError:
                        print(f"Invalid 'Price' value for {name}: {price_str}")
                        continue

                    stock_str = row['Number of Items']
                    try:
                        stock = int(stock_str)
                    except ValueError:
                        print(f"Invalid 'Number of Items' value for {name}: {stock_str}")
                        continue
                    image = row['Image']

                    self.inventory[name] = {
                        'description': description,
                        'price': price,
                        'num_items': stock,
                        'image': image
                    }

class Vegetable:
    def __init__(self, name, description, price, num_items, image):
        self.name = name
        self.description = description
        self.price = price
        self.num_items = num_items
        self.image = image

# Define State interface
class OrderState(ABC):
    @abstractmethod
    def update_status(self, order):
        pass

class OrderedState(OrderState):
    def update_status(self, order, new_state):
        # Logic to update status to 'Processing'
        order.current_state = ShippingState()  # Example transition
        order.status = new_state

class ShippingState(OrderState):
    def update_status(self, order, new_state):
        # Logic to update status to 'Processing'
        order.current_state = ShippedState()  # Example transition
        order.status = new_state

class ShippedState(OrderState):
    def update_status(self, order, new_state):
        # Logic to update status to 'Shipped'
        order.current_state = DeliveredState()  # Example transition
        order.status = new_state

class DeliveredState(OrderState):
    def update_status(self, order, new_state):
        # Logic to update status to 'Delivered'
        order.current_state = self  # No more transitions
        order.status = new_state

# Context class
class Order:
    def __init__(self, order_id, status):
        self.order_id = order_id
        self.current_state = OrderedState() 
        self.status = status

    def update_status(self, new_state):
        # Delegate state-specific behavior to the current state
        self.current_state.update_status(self,new_state)

    def __str__(self):
        return f"Order {self.order_id} - Status: {self.status}"
