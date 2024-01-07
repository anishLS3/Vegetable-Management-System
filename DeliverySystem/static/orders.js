function changeOrderState(orderId, newState) {
    $.ajax({
        type: 'POST',
        url: '/update_order_status',  
        data: {
            order_id: orderId,
            new_state: newState
        },
        success: function (response) {
            console.log(response);
            location.reload()
        },
        error: function (error) {
            console.error('Error updating order status:', error);
        }
    });
    
}