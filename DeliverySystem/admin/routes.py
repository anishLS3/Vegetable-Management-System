from flask import render_template, url_for, flash, redirect, request, Blueprint,jsonify, session
from flask_login import login_user, current_user, logout_user
from DeliverySystem import bcrypt
from DeliverySystem.models import Admin
from DeliverySystem.admin.forms import (LoginForm,RequestResetForm, ResetPasswordForm, AddItemForm)
from DeliverySystem.admin.utils import (send_reset_email, save_uploaded_file, read_customer_info_from_csv, 
                                        update_csv_order_status, send_order_state_change_email)
from DeliverySystem.admin.patterns import VegetableInventoryManager, Vegetable, StockObserver, Order

admin = Blueprint('admin', __name__)


inventory_manager = VegetableInventoryManager()
stock_observer = StockObserver()
inventory_manager.add_observer(stock_observer)

@admin.route("/admin_login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        admin = Admin.get_by_email(form.email.data)
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.stock'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('admin_login.html', title='Login', form=form)


@admin.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@admin.route("/reset_password", methods=['GET', 'POST'])
def reset_request():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        admin = Admin.get_by_email(form.email.data)
        if admin:
            send_reset_email(admin)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('admin.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@admin.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    admin = Admin.verify_reset_token(token)
    if admin is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('admin.reset_request'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        admin.password = hashed_password
        admin.save(hashed_password)
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('admin.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)


@admin.route('/additem', methods=['GET', 'POST'])
def additem():
    form = AddItemForm()

    if form.validate_on_submit():
        image_filename = save_uploaded_file(form.image.data)

        new_vegetable = Vegetable(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            num_items=form.num_items.data,
            image=image_filename
        )

        inventory_manager.add_item(new_vegetable)

        flash('New Item has been Added!', 'success')
        return redirect(url_for('admin.stock'))

    return render_template('additem.html', title="Add Item", form=form)

@admin.route('/admin/stock')
def stock():
    inventory_manager.load_from_csv()
    
    stock_data = inventory_manager.display_stock()
    print(stock_data)
    return render_template('stock.html', title="Stock", vegetables=stock_data)

@admin.route('/update_quantity', methods=['POST'])
def update_quantity():
    data = request.get_json()
    vegetable_name = data.get('vegetable_name')
    new_quantity = int(data.get('new_quantity'))
    inventory_manager.update_stock(vegetable_name, new_quantity)

    return jsonify({'message': 'Quantity updated successfully'})

@admin.route("/order")
def orders():
    billing_info_path = 'billing_info.csv'  
    order_info= read_customer_info_from_csv(billing_info_path)

    return render_template('orders.html', title="Orders", order_info=order_info)

@admin.route('/update_order_status', methods=['POST'])
def update_order_status():

    order_id = request.form.get('order_id')
    new_state = request.form.get('new_state')

    initial_order_state = 'Ordered'
    order = Order(order_id= order_id, status=initial_order_state)

    order.update_status(new_state)
    csv_path = 'billing_info.csv'
    update_csv_order_status(order.order_id, new_state, csv_path)
    send_order_state_change_email(order_id, new_state)

    return jsonify({'message': f'Status updated to {new_state} for order {order.order_id}'})
