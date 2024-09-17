from datetime import datetime

from flask import render_template, request, redirect, session, jsonify, url_for
from sqlalchemy import func

import dao
from phongmachapp import app, admin, login, db
from flask_login import login_user, current_user, logout_user
from phongmachapp.models import NguoiDung, LichKham, DanhSachKham, ChiTietDanhSachKham, QuyDinh, HoaDon, \
    ChiTietPhieuKham
import cloudinary.uploader
from decorators import loggedin, not_loggedin, thuNgan_loggedin


@app.route('/')
def index():
    categories = dao.load_categories()
    return render_template('index.html', categories=categories)


@app.route('/bacsi')
def doctor():
    return render_template('trangBacSi.html')


@app.route('/tracuuthuoc')
def sreach_medicine():
    q = request.args.get('q')
    # medi_id = request.args.get('thuoc_id')
    medicines_unit = dao.load_medicines_unit()

    results = dao.sreach_medicines(q=q)
    return render_template('tracuuthuoc.html', results=results, medicines_unit=medicines_unit)


@app.route('/lapphieukham', methods=['post', 'get'])
def lapPhieuKham():
    thuocs = dao.load_medicines()
    medicines_unit = dao.load_medicines_unit()

    if request.method.__eq__('POST'):
        name = request.form.get('name')
        datepicker = request.form.get('datepicker')
        symptom = request.form.get('symptom')
        diseasePrediction = request.form.get('diseasePrediction')

        id_phieu = dao.add_phieu_kham(name, symptom, diseasePrediction, datepicker)
        # print(id_phieu)

        thuoc = dao.get_thuoc_by_name('nameMedicine')
        if thuoc:
            # nameMedicine = request.form.get('nameMedicine')
            quantity = request.form.get('quantity')
            howToUse = request.form.get('howToUse')
            dao.add_detail_phieu_kham(id_phieu.id, thuoc.id, quantity, howToUse)
    return render_template('lapPhieuKham.html', thuocs=thuocs,
                           medicines_unit=medicines_unit)


@app.route('/ketoathuoc')
def keToaThuoc():
    thuocs = dao.load_medicines()
    note = dao.load_examination()
    examinationDetails = dao.load_examination_details()

    if request.method.__eq__('POST'):
        print(request.form)
    return render_template('thuocKeToa.html', thuocs=thuocs, note=note,
                           examinationDetails=examinationDetails)


@app.route('/benhnhan')
def user():
    return render_template('trangBenhNhan.html')


@app.route('/dangkykham', methods=['get', 'post'])
@not_loggedin
def dangKyLich():
    err_msg = ''
    genders = dao.load_gender()
    # print(genders)
    if request.method.__eq__('POST'):
        # print(request.form)
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        gender = request.form.get('gender')
        address = request.form.get('address')
        date = request.form.get('date')
        phone = request.form.get('phone')
        ngay_kham = datetime.strptime(date, '%d/%m/%Y').date()
        nam_sinh = datetime.strptime(birthday, '%d/%m/%Y').date()

        # print(ngay_kham)
        # print(date)
        if (ngay_kham < datetime.now().date()):
            err_msg = 'Ngày khám không hợp lệ! Hãy chọn lại ngày khác!'
        else:
            lichKham_check = dao.get_lichKham_by_date(ngay_kham)
            if lichKham_check:
                # danhSachKham_check = DanhSachKham.query.filter_by(lichNgayKham_id=lichKham_check.id).first()
                danhSachKham_check = dao.get_danhSachKham_by_lichKhamID(lichKham_check.id)
                # print(danhSachKham_check)
                # lịch và danh sách đều đã có
                if danhSachKham_check:
                    # thêm chi tiết bệnh nhân
                    max = dao.get_max_benhNhan()
                    # print(danhSachKham_check.id)
                    result = dao.count_soBenhNhan(danhSachKham_check.id)

                    # print(result)

                    # check số bệnh nhân cùng danh sách
                    if (result <= max):
                        dao.add_detail_benhNhan(danhSachKham_check.id,
                                                current_user.id,
                                                hoTen=name,
                                                gioiTinh=gender,
                                                namSinh=nam_sinh,
                                                soDienThoai=phone,
                                                diaChi=address)

                        return redirect('/')
                    else:
                        # thông báo cho người dùng...
                        return redirect('/')
                else:
                    # tạo danh sách mới
                    dao.add_danhSachKham(lichKham_check.id)
                    danhSachKham_new = dao.get_danhSachKham_by_lichKhamID(lichKham_check.id)
                    dao.add_detail_benhNhan(danhSachKham_new.id,
                                            current_user.id,
                                            hoTen=name,
                                            gioiTinh=gender,
                                            namSinh=nam_sinh,
                                            soDienThoai=phone,
                                            diaChi=address)

                    return redirect('/')

            # không lịch không ds
            else:
                dao.add_lichKham(ngay_kham)
                lichKham_new = dao.get_lichKham_by_date(ngay_kham)
                dao.add_danhSachKham(lichKham_new.id)
                danhSachKham_new = dao.get_danhSachKham_by_lichKhamID(lichKham_new.id)
                dao.add_detail_benhNhan(danhSachKham_new.id,
                                        current_user.id,
                                        hoTen=name,
                                        gioiTinh=gender,
                                        namSinh=nam_sinh,
                                        soDienThoai=phone,
                                        diaChi=address)

                return redirect('/')

    return render_template('dangKyKham.html', genders=genders, err_msg=err_msg)


@app.route('/yta')
def trang_yTa():
    return render_template('trangYTa.html')


@app.route('/danhsachkham', methods=['get', 'post'])
def get_patient_list():
    patients = []
    if request.method.__eq__('POST'):
        date = request.form.get('date')
        ngayChon = datetime.strptime(date, '%d/%m/%Y')  # Chuyển đổi sang định dạng date

        # Xử lí dữ liệu
        lichKham_check = dao.get_lichKham_by_date(ngayChon)
        if lichKham_check:
            danhSachKham = dao.get_danhSachKham_by_lichKhamID(lichKham_check.id)
            print(danhSachKham)
            patient_infos = dao.get_patient_list_info_by_listID(danhSachKham.id)
            patients.extend(patient_infos)

    return render_template('danhsachkham.html', patients=patients)


@app.route('/thungan')
# @thuNgan_loggedin
def trang_ThuNgan():
    return render_template('trangThuNgan.html')


@app.route('/tracuuhoadon')
# @thuNgan_loggedin
def traCuuHoaDon():
    find = request.args.get('find')
    hoaDons = dao.load_hoaDon(find)

    return render_template('hoaDon.html', hoaDons=hoaDons)


# @app.route('/update_payment_status', methods=['post'])
# def update_payment_status():
#     data = request.json
#     hoa_don_id = data.get('hoa_don_id')
#     hoa_don = HoaDon.query().filter_by(id=hoa_don_id).first()
#
#     if hoa_don:
#         hoa_don.da_thanh_toan = not hoa_don.da_thanh_toan  # đảo trạng thái
#         db.session.commit()
#         return jsonify({'status': 'success', 'da_thanh_toan': hoa_don.da_thanh_toan})
#
#     return jsonify({'status': 'error', 'message': 'Hóa đơn không tồn tại'}), 404


@app.route('/login', methods=['get', 'post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')
    err_msg = ''
    done_msg = request.args.get('done_msg')
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không đúng'
    return render_template('login.html', err_msg=err_msg)


@app.route('/logout', methods=['get'])
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['get', 'post'])
@loggedin
def register_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        if NguoiDung.query.filter(NguoiDung.username.__eq__(username)).first():
            err_msg = 'Tài khoản đã tồn tại'
        else:
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            if password.__eq__(confirm_password):
                avatar_path = ''
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                dao.add_user(name=request.form.get('name'),
                             username=username,
                             password=password,
                             avatar=avatar_path)
                return redirect('/login')
            else:
                err_msg = 'Mật khẩu xác nhận không đúng'

    return render_template('/register.html', err_msg=err_msg)


@app.route('/admin-login', methods=['post'])
def process_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    # print(username)
    # print(password)
    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)

    return redirect('/admin')


# @app.route('/api/test', methods=['post'])
# def test_add():
#     print(request.json)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
