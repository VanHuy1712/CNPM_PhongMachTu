import json, hashlib
from datetime import datetime

from flask_login import current_user
from sqlalchemy import func

from phongmachapp.models import (Thuoc, LoaiThuoc, DonViThuoc, NguoiDung, GioiTinh, ChiTietDanhSachKham, LichKham,
                                 DanhSachKham, QuyDinh, HoaDon, ChiTietPhieuKham, PhieuKham)
from phongmachapp import app, db


def load_categories():
    with open('data/categories.json', encoding='utf-8') as f:
        return json.load(f)


def load_gender():
    return [(gender.name, gender.value) for gender in GioiTinh]


def get_user_by_id(id):
    return NguoiDung.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    # print(password)
    # print(username)
    return NguoiDung.query.filter(NguoiDung.username.__eq__(username.strip()),
                                  NguoiDung.password.__eq__(password)).first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = NguoiDung(hoTen=name, username=username, password=password, anhDaiDien=avatar)
    db.session.add(u)
    db.session.commit()


def add_detail_benhNhan(danhSach_id, nguoiDangKy_id, hoTen, gioiTinh, namSinh, soDienThoai, diaChi):
    detail = ChiTietDanhSachKham(danhSachKham_id=danhSach_id,
                                 nguoiDung_id=nguoiDangKy_id,
                                 hoTen=hoTen,
                                 gioiTinh=gioiTinh,
                                 namSinh=namSinh,
                                 soDienThoai=soDienThoai,
                                 diaChi=diaChi)
    db.session.add(detail)
    db.session.commit()


def add_lichKham(ngayKham):
    lichKham = LichKham(ngayKham=ngayKham)
    db.session.add(lichKham)
    db.session.commit()


def add_danhSachKham(lichKham_id):
    danhSachKham = DanhSachKham(lichNgayKham_id=lichKham_id)
    db.session.add(danhSachKham)
    db.session.commit()


def count_soBenhNhan(id):
    return db.session.query(func.count(ChiTietDanhSachKham.id))\
        .filter(ChiTietDanhSachKham.danhSachKham_id == id)\
        .scalar()


def get_max_benhNhan():
    qd = QuyDinh.query.get(1)
    soBenhNhan = qd.soBenhNhan
    return soBenhNhan


def get_lichKham_by_date(date):
    return LichKham.query.filter_by(ngayKham=date).first()


def get_danhSachKham_by_lichKhamID(id):
    return DanhSachKham.query.filter_by(lichNgayKham_id=id).first()


def get_patient_list_info_by_listID(id):
    return ChiTietDanhSachKham.query.filter_by(danhSachKham_id=id).all()


def tinh_tong_tien_thuoc(phieuKham_id):
        total = 0
        # danh sách các chi tiết phiếu khám thuộc 1 phiếu khám có id = id phiếu khám ở hóa đơn
        chiTietPhieuKhams = ChiTietPhieuKham.query.filter_by(phieuKham_id=phieuKham_id).all()
        for c in chiTietPhieuKhams:
            total += c.soLuong * c.thuoc.price

        return total


def load_hoaDon(find=None):
    query = HoaDon.query

    if find:
        query = query.filter(HoaDon.hoTenBenhNhan.contains(find))


    return query.all()


def stats_revenue_by_month(year=datetime.now().year, month=datetime.now().month):

    query = db.session.query(func.extract('day', HoaDon.ngayKham)\
                             , func.count(HoaDon.hoTenBenhNhan)\
                             , func.sum(HoaDon.tienKham + HoaDon.tienThuoc).label('doanh_thu')\

    ).filter(func.extract('year', HoaDon.ngayKham).__eq__(year), func.extract('month', HoaDon.ngayKham).__eq__(month))


    # return query.group_by(func.extract(period, HoaDon.ngayKham)).all()
    return query.group_by(HoaDon.ngayKham).all()


def frequency_revenue_by_period(year=datetime.now().year, month=datetime.now().month, name=None):
    #đếm 1 tháng có bao nhiêu phiếu khám (1 phiếu bằng 1 lần khám)
    query = db.session.query(Thuoc.id, Thuoc.tenThuoc, func.sum(ChiTietPhieuKham.soLuong).label('so_luong'))\
        .join(ChiTietPhieuKham, Thuoc.id.__eq__(ChiTietPhieuKham.thuoc_id))\
        .join(PhieuKham, ChiTietPhieuKham.phieuKham_id.__eq__(PhieuKham.id))\
        .filter(func.extract('year', PhieuKham.ngayKham).__eq__(year), func.extract('month', PhieuKham.ngayKham).__eq__(month))

    if name:
        query = query.filter(Thuoc.tenThuoc.contains(name))

    return query.group_by(Thuoc.id).all()


def load_medicines():
    return Thuoc.query.all()


def load_medicines_unit():
    return DonViThuoc.query.all()


def load_examination():
    return PhieuKham.query.all()


def load_examination_details():
    return ChiTietPhieuKham.query.all()


def sreach_medicines(q=None):
    query = Thuoc.query

    if q:
        query = query.filter(Thuoc.tenThuoc.contains(q))

    return query.all()


def add_phieu_kham(tenBenhNhan, trieuChung, duDoanBenh, ngayKham):
    phieuKham = PhieuKham(benhNhan_id=current_user.id, tenBenhNhan=tenBenhNhan, trieuChung=trieuChung,
                          duDoanBenh=duDoanBenh, ngayKham=ngayKham)

    db.session.add(phieuKham)
    db.session.commit()
    return phieuKham


def add_detail_phieu_kham(phieuKham_id, thuoc_id, soLuong, cachDung):
    detail = ChiTietPhieuKham(phieuKham_id=phieuKham_id, thuoc_id=thuoc_id, soLuong=soLuong, cachDung=cachDung)

    db.session.add(detail)
    db.session.commit()


def get_thuoc_by_name(tenThuoc):
    return Thuoc.query.filter_by(tenThuoc=tenThuoc).first()


if __name__ == '__main__':
    with app.app_context():
        # print(stats_revenue_by_month(month=5))
        print(frequency_revenue_by_period())
