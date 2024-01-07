var shopUrl = "{{ url_for('main.shop') }}";

function addToCart(vegetableName, price) {
    var quantity = document.getElementById(vegetableName + "-count").innerText;
    if (parseInt(quantity, 10) === 0) {
        alert("Please select a quantity greater than 0.");
        return;
    }

    var formData = new FormData();
    formData.append('vegetableName', vegetableName);
    formData.append('price', price);
    formData.append('quantity', quantity);

    fetch(shopUrl, {
        method: 'POST',
        body: formData,
        ContentType: 'application/x-www-form-urlencoded',
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        resetCount(vegetableName);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


  function resetCount(vegetableName) {
    var countElement = document.getElementById(vegetableName + "-count");
    countElement.innerText = "0";
}
  
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.add-to-cart-form').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      const formData = new FormData(form);
      fetch(shopUrl, {
        method: 'POST',
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        alert(data.message);
      })
      .catch(error => {
        console.error('Error:', error);
      });
    });
  });
});
function incrementCount(vegetableName) {
  var countElement = document.getElementById(vegetableName + "-count");
  var count = parseInt(countElement.innerText, 10);
  count++;
  countElement.innerText = count;
}

function decrementCount(vegetableName) {
  var countElement = document.getElementById(vegetableName + "-count");
  var count = parseInt(countElement.innerText, 10);
  if (count > 0) {
    count--;
    countElement.innerText = count;
  }
}
