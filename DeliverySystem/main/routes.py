import ast
import json
from datetime import datetime
from uuid import uuid4
from flask import render_template, request, Blueprint, redirect, url_for, flash, jsonify,session
from DeliverySystem.main.utils import (read_vegetables_from_csv, save_customer_info_to_csv, calculate_discount,save_order_to_csv,
                                       read_customer_info_from_csv, remove_order_from_csv,get_cart_items, send_order_confirmation_email, 
                                       get_order_info_by_id,send_order_removal_email,reduce_quantity)
from DeliverySystem.main.patterns import ProductBuilder, DiscountDecorator
from DeliverySystem.main.patternsB import (PaytmPaymentStrategy, CreditCardPaymentStrategy, 
                                           GenerateBillCommand, ExecutePaymentCommand, BillingObserver,BillingService,calculate_total_amount )
from DeliverySystem.main.forms import BillingForm, PayTMForm, CreditCardForm

main = Blueprint('main', __name__)

credit_card_strategy = CreditCardPaymentStrategy()
paytm_strategy = PaytmPaymentStrategy()
billing_service = BillingService()
billing_observer = BillingObserver()
billing_service.add_observer(billing_observer)

generate_bill_command = GenerateBillCommand(billing_service)
execute_payment_command_credit_card = ExecutePaymentCommand(credit_card_strategy)
execute_payment_command_paytm = ExecutePaymentCommand(paytm_strategy)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/about")
def about():
    return render_template('about.html', title="About")

@main.route("/contact")
def contact():
    return render_template('contact.html', title="Contact")

@main.route("/shop", methods=['GET', 'POST'])
def shop():
    vegetables = read_vegetables_from_csv()
    session.setdefault('cart', {})

    if request.method == 'POST':
        vegetable_name = request.form.get('vegetableName')
        quantity_str = request.form.get('quantity')

        if not vegetable_name or not quantity_str:
            return jsonify({'error': 'Both vegetable name and quantity are required'}), 400

        try:
            quantity = int(quantity_str)
        except ValueError:
            return jsonify({'error': 'Invalid quantity value'}), 400

        if vegetable_name in vegetables:
            product = vegetables[vegetable_name]
            available_quantity = product.stock

            if int(available_quantity) >= int(quantity):
                cart = session['cart']
                if vegetable_name in cart:
                    cart[vegetable_name]['quantity'] += quantity
                else:
                    cart[vegetable_name] = {'quantity': quantity, 'price': product.price}
                session.permanent = True
                product.add_to_cart(quantity)

                return jsonify({'message': 'Product added to cart successfully'})
            else:
                return jsonify({'message': 'Not enough quantity available'})
        else:
            return jsonify({'message': 'Product not found'}), 404

    return render_template('shop.html', title="Shop", vegetables=vegetables)



@main.route("/cart")
def cart():
    cart_data = get_cart_items()
    print("Cart Items:", cart_data)
    return render_template('cart.html', title="Cart", cart=cart_data)

@main.route("/remove_item/<vegetable_name>", methods=['POST'])
def remove_item(vegetable_name):
    cart = session.get('cart', {})
    if vegetable_name in cart:
        del cart[vegetable_name]
        session['cart'] = cart
        return jsonify({'message': 'Item removed successfully'})
    else:
        return jsonify({'message': 'Item not found in the cart'}), 404
    
@main.route("/get_totals", methods=['POST'])
def get_totals():
    total_quantity = 0
    total_price = 0

    discount_percentage = session.get('discount_percentage', 0)

    for vegetable_name, item in session.get('cart', {}).items():
        product = ProductBuilder(vegetable_name).set_price(item['price']).set_stock(100).build()
        discounted_product = DiscountDecorator(product, discount_percentage)

        total_quantity += item['quantity']
        total_price += product.get_total_price(item['quantity'])

    return jsonify({
        'totals': {
            'totalQuantity': total_quantity,
            'totalPrice': total_price,
            'discountApplied': discount_percentage
        }
    })



@main.route("/check_login", methods=['GET'])
def check_login():
    user_email = session.get('email')
    logged_in = user_email is not None

    return jsonify({'logged_in': logged_in})

@main.route('/set_checkout_session', methods=['POST'])
def set_checkout_session():
    discount_percentage = request.form.get('discount_percentage')
    discounted_price = request.form.get('discounted_price')
    session['discount_percentage'] = discount_percentage
    session['discounted_price'] = discounted_price

    return jsonify({'message': 'Checkout session set successfully'})

@main.route("/billing", methods=['GET', 'POST'])
def billing():
    form = BillingForm()

    if form.validate_on_submit():
        customer_info = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'address': form.address.data,
            'city': form.city.data,
            'state': form.state.data,
            'postal_code': form.postal_code.data,
            'country': form.country.data,
            'phone_number': form.phone_number.data,
            'email': form.email.data,
            'payment_method': form.payment_method.data
        }

        save_customer_info_to_csv(form)

        cart = session.get('cart', {})

        total_quantity = sum(item['quantity'] for item in cart.values())
        total_price = calculate_total_amount(cart)
        discount_info = calculate_discount(cart)
        discount_percentage = discount_info['discount_percentage']
        discounted_total_price = discount_info['discountedTotalPrice']
        
        order_id = str(uuid4())
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        orders = {
            'order_id': order_id,
            'order_date': order_date,
            'customer_info': customer_info,
            'payment_method': form.payment_method.data,
            'cart': cart,
            'total_quantity': total_quantity,
            'total_price': total_price,
            'discount_percentage':discount_percentage,
            'discounted_total_price': discounted_total_price
        }

        save_order_to_csv(orders)

        flash('Billing information saved successfully!', 'success')

        bill_result = generate_bill_command.execute(customer_info, cart)
        print(bill_result)

        if form.payment_method.data == 'credit_card':
            execute_payment_command_credit_card.execute(customer_info, cart)
            return redirect(url_for('main.credit_card_details'))
        elif form.payment_method.data == 'paytm':
            execute_payment_command_paytm.execute(customer_info, cart)
            return redirect(url_for('main.paytm_details'))
        else:
            flash('Invalid payment method selected', 'danger')
            return redirect(url_for('main.billing'))


    return render_template('billing.html', title='Billing', form=form)

@main.route("/paytm_details", methods=['GET', 'POST'])
def paytm_details():
    form = PayTMForm()
    if form.validate_on_submit():
        session['paytm_details'] = {
            'paytm_id' : form.paytm_id.data,
            'phone_number': form.phone_number.data,
            'pin': form.pin.data
        }
        flash('Payment made successfully!', 'success')
        return redirect(url_for('main.order_confirmation'))

    return render_template('paytm_details.html', title='Paytm Details', form=form)

@main.route('/credit_card_details', methods=['GET', 'POST'])
def credit_card_details():
    form = CreditCardForm()

    if form.validate_on_submit():
        session['credit_card_details'] = {
            'credit_card_number': form.credit_card_number.data,
            'expiry_date': form.expiry_date.data,
            'cvv': form.cvv.data
        }
        flash('Payment made successfully!', 'success')
        return redirect(url_for('main.order_confirmation'))

    return render_template('credit_card_details.html', title='Credit Card Details', form=form)

from operator import itemgetter

@main.route("/order_confirmation")
def order_confirmation():
    
    cart = session.get('cart', {})
    billing_info_path = 'billing_info.csv'  
    order_info_list = read_customer_info_from_csv(billing_info_path)
    sorted_order_info_list = sorted(order_info_list, key=itemgetter('order_date'), reverse=True)
    latest_order_info = sorted_order_info_list[0]
    for order_info in latest_order_info:
        order_id = latest_order_info['order_id']
        email = latest_order_info['email']

    send_order_confirmation_email(email, latest_order_info)
    reduce_quantity(cart)
    session['cart'] = {}
    return render_template('order_confirmation.html', title='Order Confirmation', order_info=latest_order_info, cart=cart)


@main.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
    billing_info_path = 'billing_info.csv'  
    order_info = read_customer_info_from_csv(billing_info_path)

    return render_template('my_orders.html', title='My Orders',order_info=order_info)

@main.route('/order_details/<order_id>')
def order_details(order_id):
    billing_info_path = 'billing_info.csv'  
    order_info = read_customer_info_from_csv(billing_info_path)
    for order in order_info:
        if order['order_id'] == order_id:
            if 'cart' in order and isinstance(order['cart'], str):
                order['cart'] = ast.literal_eval(order['cart'])
            index = order_info.index(order)

    return render_template('order_details.html', order_info = order_info, index = index)

@main.route('/remove_order/<order_id>', methods=['POST'])
def remove_order(order_id):
    try:
        remove_order_from_csv(order_id)
    except ValueError as e:
        return jsonify({'message': e})

    updated_orders = read_customer_info_from_csv('billing_info.csv')
    return jsonify({'orders': updated_orders})











