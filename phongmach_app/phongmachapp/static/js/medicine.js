$(document).ready(function() {
    // Gắn sự kiện click cho nút "Thêm thuốc"
    $('#addMedicineBtn').click(function() {
        // Lấy bảng bằng class
        var table = $('.medicineTable');

        // Đếm số hàng trong bảng (trừ hàng header)
        var rowCount = table.find('tr').length - 1;

        // Tạo một dòng mới
        var newRow = $('<tr>');

        // Thêm các ô vào dòng mới
        newRow.append('<td>' + (rowCount + 1) + '</td>');
        newRow.append('<td><select class="form-select" name="nameMedicine"><option value=""></option>{% for t in thuocs %}<option value=""></option>{% endfor %}</select></td>');
        newRow.append('<td><select class="form-select" name="medicineType">{% for m in medicines_unit %}<option value=""></option>{% endfor %}</select></td>');
        newRow.append('<td><input class="form-control" name="quantity"></td>');
        newRow.append('<td><input class="form-control" name="howToUse"></td>');

        // Thêm dòng mới vào cuối bảng trừ header
        table.append(newRow);
    });
});