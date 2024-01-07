function updateQuantity(vegetableName, newQuantity) {
    $.ajax({
        type: 'POST',
        url: '/update_quantity',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            vegetable_name: vegetableName,
            new_quantity: newQuantity
        }),
        success: function (response) {
            console.log(response);
        },
        error: function (error) {
            console.log(error);
        }
    });

    window.location.reload();
}

function decrementCount(vegetableName) {
    var countElement = $('#' + vegetableName + '-count');
    var currentCount = parseInt(countElement.text(), 10);
    if (currentCount > 0) {
        var newCount = currentCount - 1;
        countElement.text(newCount);

    }
}

function incrementCount(vegetableName) {
    var countElement = $('#' + vegetableName + '-count');
    var currentCount = parseInt(countElement.text(), 10);
    var newCount = currentCount + 1;
    countElement.text(newCount);

}


