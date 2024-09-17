function del_patient(p_id) {
    if (confirm("Bạn có chắc muốn xóa người này khỏi danh sách?") === true) {
        let e = document.getElementById(`patient${p_id}`);
        e.style.display = "none";
    }
}