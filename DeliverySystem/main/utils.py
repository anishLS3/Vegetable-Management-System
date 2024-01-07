import csv
from flask import session
from DeliverySystem.main.patterns import ProductBuilder
from flask_mail import Message
from DeliverySystem import mail
import ast
import json

def sanitize_order_id(order_id):
    return order_id.replace("-", "").strip().lower()

def read_vegetables_from_csv():
    vegetables = {}
    with open('vegetable_inventory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            vegetable_name = row['Name']
            description = row['Description']
            price_str = row['Price']
            try:
                price = float(price_str)
            except ValueError:
                print(f"Invalid 'Price' value for {vegetable_name}: {price_str}")
                continue

            stock_str = row['Number of Items']
            try:
                stock = int(stock_str)
            except ValueError:
                print(f"Invalid 'Number of Items' value for {vegetable_name}: {stock_str}")
                continue

            image = row['Image']

            product = ProductBuilder(vegetable_name).set_description(description).set_price(price).set_stock(stock).set_image(image).build()
            vegetables[vegetable_name] = product
    return vegetables


def get_cart_items():
    cart_data = session.get('cart', {})
    cart_items = []

    for vegetable_name, cart_item in cart_data.items():
        cart_items.append({
            'vegetable_name': vegetable_name,
            'quantity': cart_item.get('quantity', 0),
            'price': cart_item.get('price', 0)
        })

    return cart_items

def save_customer_info_to_csv(form):
    with open('customer_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            form.first_name.data,
            form.last_name.data,
            form.address.data,
            form.city.data,
            form.state.data,
            form.postal_code.data,
            form.country.data,
            form.phone_number.data,
            form.email.data
        ])

def calculate_discount(cart):
    total_price = sum(item['quantity'] * item['price'] for item in cart.values())
    global_discount_percentage = 0

    if total_price > 400:
        global_discount_percentage = 20
    elif total_price > 350:
        global_discount_percentage = 15
    elif total_price > 300:
        global_discount_percentage = 10
    elif total_price > 250:
        global_discount_percentage = 8
    elif total_price > 200:
        global_discount_percentage = 5

    global_discount = total_price * (global_discount_percentage / 100)
    discounted_total_price = total_price - global_discount

    return {
        'discount_percentage': global_discount_percentage,  
        'discountedTotalPrice': discounted_total_price,
        'total_price': total_price
    }


def save_order_to_csv(order):
    csv_file_path = 'billing_info.csv' 

    with open(csv_file_path, mode='a', newline='') as csv_file:
        fieldnames = ['order_id', 'order_date', 'first_name', 'last_name', 'address', 'city',
                      'state', 'postal_code', 'country', 'phone_number', 'email',
                      'payment_method', 'cart', 'total_quantity', 'total_price',
                      'discount_percentage', 'discounted_total_price','status']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        if csv_file.tell() == 0:  
            writer.writeheader()

        writer.writerow({
            'order_id': order['order_id'],
            'order_date': order['order_date'],
            'first_name': order['customer_info']['first_name'],
            'last_name': order['customer_info']['last_name'],
            'address': order['customer_info']['address'],
            'city': order['customer_info']['city'],
            'state': order['customer_info']['state'],
            'postal_code': order['customer_info']['postal_code'],
            'country': order['customer_info']['country'],
            'phone_number': order['customer_info']['phone_number'],
            'email': order['customer_info']['email'],
            'payment_method': order['payment_method'],
            'cart': order['cart'],
            'total_quantity': order['total_quantity'],
            'total_price': order['total_price'],
            'discount_percentage': order['discount_percentage'],
            'discounted_total_price': order['discounted_total_price'],
            'status' : 'Ordered'
        })
        

def read_customer_info_from_csv(csv_path):
    try:
        order_info = []
        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                order_details= {
                    'order_id': sanitize_order_id(row['order_id']),
                    'order_date': row['order_date'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'address': row['address'],
                    'city': row['city'],
                    'state': row['state'],
                    'postal_code': row['postal_code'],
                    'country': row['country'],
                    'phone_number': row['phone_number'],
                    'email': row['email'],
                    'payment_method': row['payment_method'],
                    'cart' : row['cart'],
                    'total_quantity': row['total_quantity'],
                    'total_price': row['total_price'],
                    'discount_percentage': row['discount_percentage'],
                    'discounted_total_price': row['discounted_total_price'],
                    'status':row['status']
                }
                order_info.append(order_details)
        return order_info
    
    except FileNotFoundError:
        print(f"File not found: {csv_path}")

def remove_order_from_csv(order_id):
    csv_path = 'billing_info.csv'
    orders = read_customer_info_from_csv(csv_path)
    rows = []
    removed_orders = []

    for order in orders:
        order_id = order['order_id']
        email = order['email']

        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if sanitize_order_id(row['order_id']) == sanitize_order_id(order_id):
                    if row['status'] == "Shipped":
                        raise ValueError(f"Order {order_id} is already shipped! Cannot remove order")
                else:
                    rows.append(row)

        removed_orders.append({'order_id': order_id, 'email': email})

    with open(csv_path, 'w', newline='') as csv_file:
        fieldnames = ['order_id', 'order_date', 'first_name', 'last_name', 'address', 'city',
                      'state', 'postal_code', 'country', 'phone_number', 'email',
                      'payment_method', 'cart', 'total_quantity', 'total_price',
                      'discount_percentage', 'discounted_total_price', 'status']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    for removed_order in removed_orders:
        send_order_removal_email(removed_order['email'], removed_order['order_id'])


def remove_all_orders_from_csv():
    csv_path = 'billing_info.csv'
    with open(csv_path, 'w', newline='') as csv_file:
        fieldnames = ['order_id', 'order_date', 'first_name', 'last_name', 'address', 'city', 'state', 'postal_code', 'country', 'phone_number', 'email', 'payment_method', 'total_quantity', 'total_price', 'discount_percentage', 'discounted_total_price']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

def send_order_confirmation_email(email, order_info):
    subject = 'Order Confirmation'
    body = f'Thank you for your order! Your order with ID {order_info["order_id"]} has been confirmed.\n\n'
    
    body += '**Order Details:**\n'
    body += f' - <strong>Order Date:</strong> {order_info["order_date"]}\n'
    body += f' - <strong>Name:</strong> {order_info["first_name"]} {order_info["last_name"]}\n'
    body += f' - <strong>Address:</strong> {order_info["address"]}, {order_info["city"]}, {order_info["state"]}, {order_info["postal_code"]}, {order_info["country"]}\n'
    body += f' - <strong>Phone Number:</strong> {order_info["phone_number"]}\n'
    body += f' - <strong>Email:</strong> {order_info["email"]}\n'
    body += f' - <strong>Payment Method:</strong> {order_info["payment_method"]}\n\n'

    body += '**Ordered Items:**\n'
    body += '<table border="1">\n'
    body += '<tr>\n'
    body += '<th>Vegetable</th>\n'
    body += '<th>Quantity (kg)</th>\n'
    body += '<th>Price per kg (Rs)</th>\n'
    body += '<th>Total Price (Rs)</th>\n'
    body += '</tr>\n'

    cart_items = ast.literal_eval(order_info["cart"])
    for vegetable_name, cart_item in cart_items.items():
        body += f'<tr>\n'
        body += f'<td>{vegetable_name}</td>\n'
        body += f'<td>{cart_item["quantity"]}</td>\n'
        body += f'<td>{cart_item["price"]}</td>\n'
        body += f'<td>{cart_item["quantity"] * cart_item["price"]}</td>\n'
        body += f'</tr>\n'

    body += '</table>\n'
    body += f'\n<strong>Total Quantity:</strong> {order_info["total_quantity"]} kg\n'
    body += f'<strong>Total Price:</strong> Rs {order_info["total_price"]}\n'
    body += f'<strong>Discount Percentage:</strong> {order_info["discount_percentage"]}%\n'
    body += f'<strong>Discounted Total Price:</strong> Rs {order_info["discounted_total_price"]}\n\n'
    body = f'Thank you for shopping with FreshFarmFinds!\n\n'
    send_email(email, subject, body)

def get_order_info_by_id(order_id):
    orders = read_customer_info_from_csv('billing_info.csv')
    for order in orders:
        if sanitize_order_id(order['order_id']) == sanitize_order_id(order_id):
            return {
                'order_id' :order['order_id'],
                'order_date': order['order_date'],
                'email': order['email']
            }
    raise ValueError('Order not found')

def send_order_removal_email(email,order_id):

    subject = 'Order Removal Confirmation'
    body = f'Thank you for shopping with FreshFarmFinds!\n\n'
    body += f'Order ID: {order_id}\n'
    body += 'Your order has been successfully removed.\n'
    body += '\nWe appreciate your business and look forward to serving you again!\n'

    send_email(email, subject, body)



def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)

def reduce_quantity(cart):
    veggies = []
    all_veggies = []

    for vegetable_name, details in cart.items():
        veggies.append((vegetable_name, details['quantity']))
        all_veggies.append(sanitize_order_id(vegetable_name))


    reader = csv.reader(open("vegetable_inventory.csv"))
    data = list(reader)
    reader = csv.reader(open("vegetable_inventory.csv"))
    next(reader)
    for idx, row in enumerate(reader):
        if sanitize_order_id(row[0]) in all_veggies:
            data[idx+1][3] = int(row[3]) - int(veggies[all_veggies.index(sanitize_order_id(row[0]))][1])
    
    f = open('vegetable_inventory.csv', "w", newline='')
    writer = csv.writer(f)
    writer.writerows(data)    
