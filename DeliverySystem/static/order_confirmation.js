function generatePDF(orderId) {
    $.ajax({
        url: `/generate_pdf/${orderId}`,
        method: 'GET',
        success: function(response) {
            const blob = new Blob([response], { type: 'application/pdf' });
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = `order_${orderId}.pdf`;
            link.click();
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}

function printInvoice() {
    window.print();
}