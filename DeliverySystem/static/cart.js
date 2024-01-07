$(document).ready(function () {
    // Fetch cart data
    $.post('/shop', $(this).serialize(), function (data) {
        console.log('AJAX Response:', data);
        alert(data.message);
        updateCartTable(data.cartData);
    });

    // Fetch totals data
    $.post('/get_totals', $(this).serialize(), function (data) {
        console.log('Totals AJAX Response:', data);
        updateTotalsTable(data.totals);
    });

    // Update totals when the page loads
    fetchTotals();
});

function updateCartTable(cartData) {
    let tableBody = $('.table tbody');

    if (!tableBody.length) {
        console.error('Table body not found');
        return;
    }

    tableBody.empty();

    for (let vegetableName in cartData) {
        let row = tableBody[0].insertRow();
        let cell1 = row.insertCell(0);
        let cell2 = row.insertCell(1);
        let cell3 = row.insertCell(2);
        let cell4 = row.insertCell(3);
        let cell5 = row.insertCell(4);

        cell1.textContent = vegetableName;
        cell2.textContent = cartData[vegetableName]['quantity'];
        cell3.textContent = 'Rs' + cartData[vegetableName]['price'];
        cell4.textContent = 'Rs' + (cartData[vegetableName]['quantity'] * cartData[vegetableName]['price']);
        cell5.innerHTML = `<button class="btn btn-danger" onclick="removeItem('${vegetableName}')">Remove</button>`;
    }
}

function updateTotalsTable(totals) {
    let totalsTableBody = $('#totalsTableBody');
    let totalQuantityElement = $('#totalQuantity');
    let totalPriceElement = $('#totalPrice');

    if (!totalsTableBody.length || !totalQuantityElement.length || !totalPriceElement.length) {
        console.error('Totals table body, total quantity element, or total price element not found');
        return;
    }

    totalsTableBody.empty();

    let row = totalsTableBody[0].insertRow();
    let cell1 = row.insertCell(0);
    let cell2 = row.insertCell(1);
    let cell3 = row.insertCell(2);
    let cell4 = row.insertCell(3);

    cell1.textContent = totals.totalQuantity;
    cell2.textContent = 'Rs' + totals.totalPrice;

    if (totals.totalPrice > 400) {
        applyDiscount(cell3, cell4, totals, 20);
    } else if (totals.totalPrice > 350) {
        applyDiscount(cell3, cell4, totals, 15);
    } else if (totals.totalPrice > 300) {
        applyDiscount(cell3, cell4, totals, 10);
    } else if (totals.totalPrice > 250) {
        applyDiscount(cell3, cell4, totals, 8);
    } else if (totals.totalPrice > 200) {
        applyDiscount(cell3, cell4, totals, 5);
    } else {
        cell3.textContent = 'No Discount Applied';
        cell4.textContent = '';
    }

    console.log("Total Quantity:", totals.totalQuantity);
    console.log("Total Price:", totals.totalPrice);
    console.log("Discount Applied:", cell3.textContent);
    console.log("Total Price After Discount:", cell4.textContent);
}

function applyDiscount(cell3, cell4, totals, discountPercentage) {
    let discount = totals.totalPrice * (discountPercentage / 100);
    let discountedPrice = totals.totalPrice - discount;
    cell3.textContent = `Rs${discount} (${discountPercentage}%)`;
    cell4.textContent = `Rs${discountedPrice}`;
}

function fetchTotals() {
    $.ajax({
        type: 'POST',
        url: '/get_totals',
        success: function (data) {
            updateTotalsTable(data.totals);
        },
        error: function (error) {
            console.error('Error fetching totals:', error);
        }
    });
}

function removeItem(vegetableName) {
    console.log(`Removing item: ${vegetableName}`);

    try {
        $.post(`/remove_item/${vegetableName}`, function (data) {
            console.log(data);
            updateCartTable(data.cartData);
            window.location.reload();
        });
    } catch (error) {
        console.error("Error processing removal:", error);
    }
}

function checkout() {
    $.post('/get_totals', function (totalsData) {
        console.log('Totals AJAX Response:', totalsData);

        if (totalsData.totals.totalPrice > 100) {
            $.get('/check_login', function (loginData) {
                console.log('Login Check Response:', loginData);

                if (loginData.logged_in) {
                    console.log('User is logged in');
                    $.post('/set_checkout_session', {
                        discount_percentage: totalsData.totals.discountPercentage,
                        discounted_price: totalsData.totals.discountedPrice
                    }, function (response) {
                        console.log('Checkout Session Set:', response);
                        window.location.href = '/billing';
                    });
                } else {
                    console.log('User is not logged in');
                    alert('Please log in to proceed with the checkout.');
                    window.location.href = '/login';
                }
            });
        } else {
            alert('Total price must be greater than 100 to proceed with the checkout.');
        }
    });
}
