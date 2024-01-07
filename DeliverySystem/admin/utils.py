from flask import url_for, current_app
from flask_mail import Message
from DeliverySystem import mail
from werkzeug.utils import secure_filename
import os, csv

def send_reset_email(user):
    token = user.get_reset_token() 
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def save_uploaded_file(file):
    if file:
        images_folder = os.path.join(current_app.root_path, 'static', 'images')
        os.makedirs(images_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        file.save(os.path.join(images_folder, filename))
        return filename  
    return None

def sanitize_order_id(order_id):
    return order_id.replace("-", "").strip().lower()

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

def update_csv_order_status(order_id, new_state, csv_path):
    rows = []

    with open(csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            if sanitize_order_id(row['order_id']) == sanitize_order_id(order_id):
                row['status'] = new_state
                rows.append(row)
            else:
                rows.append(row)
    
    fieldnames = reader.fieldnames
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def get_order_info(order_id):
    csv_path = 'billing_info.csv'

    with open(csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if sanitize_order_id(row['order_id']) == sanitize_order_id(order_id):
                return row

    return None

def send_order_state_change_email(order_id, new_status):
    order = get_order_info(order_id)

    if order:
        recipient_email = order['email']
        subject = f'Order Status Update - Order ID: {order_id}'
        body = f'Your order with ID {order_id} has been updated to status: {new_status}.'
        body = f'Thank you for shopping with FreshFarmFinds!\n\n'
        message = Message(subject=subject, recipients=[recipient_email], body=body)
        mail.send(message)
    else:
        print(f"Order with ID {order_id} not found.")

