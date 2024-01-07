function removeOrder(orderId) {
    console.log("Removing order with ID:", orderId);
    const url = `http://127.0.0.1:5000/remove_order/${orderId}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to remove order: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        updateOrderList(data.orders);
        window.location.reload();
    })
    .catch(error => {
        console.error('Error removing order:', error);
        alert('Error removing order. Please try again.');
    });

}


function updateOrderList(orders) {
    console.log("Orders after update:", orders);

    let ordersList = document.getElementById('ordersList');

    if (!ordersList) {
        console.error('Orders list not found');
        return;
    }

    ordersList.innerHTML = '';  

    for (let order of orders) {
        let listItem = document.createElement('li');
        listItem.textContent = `Order ID: ${order.order_id}, Total Price: Rs${order.total_price}`;
        let removeButton = document.createElement('button');
        removeButton.textContent = 'Remove Order';
        removeButton.classList.add('btn', 'btn-danger');
        removeButton.onclick = function () {
            removeOrder(order.order_id);
        };

        listItem.appendChild(removeButton);
        ordersList.appendChild(listItem);
    }
}


