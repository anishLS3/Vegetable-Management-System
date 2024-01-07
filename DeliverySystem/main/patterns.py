from abc import ABC, abstractmethod

class Observable:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

class Observer(ABC):
    @abstractmethod
    def update(self, observable):
        pass

class CartObserver(Observer):
    def update(self, observable):
        product = observable  
        print(f"Product {product.name} added to the cart.")

class Product(Observable):
    def __init__(self, name, description, price, stock, image):
        super().__init__()
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.image = image

    def get_price(self):
        return self.price

    def get_total_price(self, quantity):
        return self.price * quantity

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

    def add_to_cart(self, quantity):
        if int(self.stock) >= int(quantity) > 0:
            self.stock -= quantity
            self.notify_observers()
            print(f"Added {quantity} {self.name}(s) to the cart.")
        elif quantity <= 0:
            print("Quantity must be greater than zero.")
        else:
            print(f"Not enough stock available for {self.name}. Available stock: {self.stock}.")

class ProductBuilder:
    def __init__(self, name):
        self.product = Product(name, "", 0, 0, "")

    def set_description(self, description):
        self.product.description = description
        return self

    def set_price(self, price):
        self.product.price = price
        return self

    def set_stock(self, stock):
        self.product.stock = stock
        return self

    def set_image(self, image):
        self.product.image = image
        return self

    def build(self):
        return self.product

class Component(ABC):
    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_total_price(self, quantity):
        pass

class ProductB(Component):
    def __init__(self, name, description, price, stock, image):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.image = image

    def get_price(self):
        return self.price

    def get_total_price(self, quantity):
        return self.price * quantity

class Decorator(Component):
    def __init__(self, component):
        self.component = component

    @abstractmethod
    def get_price(self):
        pass

    @abstractmethod
    def get_total_price(self, quantity):
        pass

class PriceDecorator(Decorator):
    def get_price(self):
        return self.component.get_price()

    def get_total_price(self, quantity):
        return self.component.get_total_price(quantity)
    
class DiscountDecorator(Decorator):
    def __init__(self, component, discount_percentage):
        super().__init__(component)
        self.discount_percentage = discount_percentage

    def get_price(self):
        if self.discount_percentage is not None:
            discounted_price = self.component.get_price() * (1 - self.discount_percentage / 100)
            return discounted_price
        else:
            return self.component.get_price()

    def get_total_price(self, quantity):
        return self.get_price() * quantity

    


