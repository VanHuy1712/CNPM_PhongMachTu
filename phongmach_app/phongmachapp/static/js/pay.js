//    function updatePaymentStatus(hoa_don_id, button) {
//        fetch('/update_payment_status', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//            body: JSON.stringify({
//                'hoa_don_id': hoa_don_id
//            }),
//        })
//        .then(response => response.json())
//        .then(data => {
//            if (data.status === 'success') {
//                button.classList.toggle('text-success', data.da_thanh_toan);
//                button.classList.toggle('text-normal', !data.da_thanh_toan);
//                button.textContent = data.da_thanh_toan ? 'Đã thanh toán' : 'Thanh toán';
//            } else {
//                alert(data.message);
//            }
//        });
//    }
