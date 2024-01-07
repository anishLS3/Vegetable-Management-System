from abc import ABC, abstractmethod
import csv

class PaymentProcessorStrategy(ABC):
    @abstractmethod
    def process_payment(self, customer_info, items):
        pass

class CreditCardPaymentStrategy(PaymentProcessorStrategy):
    def process_payment(self, customer_info, items):
        return f"Paid {calculate_total_amount(items)} via Credit Card"
    
    def process_payment_with_details(self, customer_info, items):
        print("Processing credit card payment with customer_info:", customer_info)
        print("Processing credit card payment with items:", items)

class PaytmPaymentStrategy(PaymentProcessorStrategy):
    def process_payment(self, customer_info, items):
        return f"Paid {calculate_total_amount(items)} via Paytm"
    
    def process_payment_with_details(self, customer_info, items):
        print("Processing Paytm payment with customer_info:", customer_info)
        print("Processing Paytm payment with items:", items)

class GenerateBillCommand:
    def __init__(self, billing_service):
        self.billing_service = billing_service

    def execute(self, customer_info, items):
        bill = self.billing_service.generate_bill(customer_info, items)
        return f"Bill generated: {bill}"

class BillingObserver:
    def update(self, message):
        print(f"Notification: {message}")

class BillingService:
    def __init__(self, csv_filename='billing_data.csv'):
        self.observers = []
        self.csv_filename = csv_filename

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def generate_bill(self, customer_info, items):
        total_amount = calculate_total_amount(items)
        message = f"Bill generated for {customer_info['first_name']} {customer_info['last_name']}. Total amount: {total_amount}"
        self.notify_observers(message)
        self.save_to_csv(customer_info, total_amount)
        
        return total_amount

    def save_to_csv(self, customer_info, total_amount):
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([customer_info['first_name'], customer_info['last_name'], customer_info['address'],
                             customer_info['city'], customer_info['state'], customer_info['postal_code'],
                             customer_info['country'], customer_info['phone_number'], customer_info['email'],
                             total_amount])

def calculate_total_amount(items):
    if isinstance(items, dict):
        total_amount = sum(item['price'] * item['quantity'] for item in items.values())
    else:
        total_amount = sum(item['price'] * item['quantity'] for item in items)
    return total_amount

class ExecutePaymentCommand:
    def __init__(self, payment_processor_strategy):
        self.payment_processor_strategy = payment_processor_strategy

    def execute(self, customer_info, items):
        self.payment_processor_strategy.process_payment_with_details(customer_info, items)

