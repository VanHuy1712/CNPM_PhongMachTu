from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, Boolean, DateTime, Date
from sqlalchemy.orm import relationship, backref
from phongmachapp import db, app
from flask_login import UserMixin
from enum import Enum as RoleEnum
from datetime import datetime, date


class VaiTroNguoiDung(RoleEnum):
    BenhNhan = 1
    YTa = 2
    BacSi = 3
    ThuNgan = 4
    ADMIN = 5


class GioiTinh(RoleEnum):
    Nam = 1
    Nu = 2
    KhongTraLoi = 3


class Base(db.Model):
    __abstract__ = True

    id = Column(Integer, autoincrement=True, primary_key=True)


class NguoiDung(Base, UserMixin):
    hoTen = Column(String(100), nullable=False)
    anhDaiDien = Column(String(100), nullable=False)
    username = Column(String(50), unique=True)
    password = Column(String(50), nullable=False)
    vaiTro_NguoiDung = Column(Enum(VaiTroNguoiDung), default=VaiTroNguoiDung.BenhNhan)
    phieuKhams = relationship('PhieuKham', backref='nguoidung', lazy=True)
    chiTietDanhSachKhams = relationship('ChiTietDanhSachKham', backref='nguoidung', lazy=True)
    hoaDons = relationship('HoaDon', backref='nguoidung', lazy=True)
    # backref dùng để truy vấn ngược lại dễ hơn,
    # lazy được sử dụng để xác định cách truy xuất dữ liệu từ cơ sở dữ liệu khi cần thiết
    # active = models.BooleanField(default=True)

    def __str__(self):
        return self.hoTen


class PhieuKham(Base):
    benhNhan_id = Column(Integer, ForeignKey(NguoiDung.id), nullable=False) #bác sĩ
    tenBenhNhan = Column(String(100), nullable=False)
    trieuChung = Column(String(50), nullable=False)
    duDoanBenh = Column(String(50), nullable=False)
    ngayKham = Column(Date, default=datetime.now(), nullable=False)
    chiTietPhieuKhams = relationship('ChiTietPhieuKham', backref='phieukham', lazy=True)
    hoaDon = relationship('HoaDon', backref='phieukham', lazy=True)


class DonViThuoc(Base):
    tenDonVi = Column(String(50), nullable=False)
    thuocs = relationship('Thuoc', backref='donViThuoc', lazy=True)

    def __str__(self):
        return self.tenDonVi


class Thuoc(Base):
    tenThuoc = Column(String(50), unique=True, nullable=False)
    congDung = Column(String(50), nullable=False)
    price = Column(Float, nullable=False) # thêm giá tiền
    donViThuoc_id = Column(Integer, ForeignKey(DonViThuoc.id), nullable=False)
    chiTietPhieuKham = relationship('ChiTietPhieuKham', backref='thuoc', lazy=True)
    loaiThuocs = relationship('LoaiThuoc', secondary='thuoc_loaiThuoc', lazy='subquery',
                              backref=backref('thuocs_list', lazy=True))

    def __str__(self):
        return self.tenThuoc


class LoaiThuoc(Base):
    tenLoai = Column(String(50), unique=True, nullable=False)
    thuocs = relationship('Thuoc', secondary='thuoc_loaiThuoc', lazy='subquery',
                          backref=backref('loaiThuocs_list', lazy=True), viewonly=True)

    def __str__(self):
        return self.tenLoai


thuoc_loaiThuoc = db.Table('thuoc_loaiThuoc',
                           Column('thuoc_id', Integer, ForeignKey(Thuoc.id), primary_key=True),
                           Column('loaiThuoc_id', Integer, ForeignKey(LoaiThuoc.id), primary_key=True))


class ChiTietPhieuKham(Base):
    soLuong = Column(Integer, default=1)
    cachDung = Column(String(100), nullable=True)
    phieuKham_id = Column(Integer, ForeignKey(PhieuKham.id), nullable=False)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.id), nullable=False)


class HoaDon(Base): # cần có khóa ngoại là người dùng cụ thể lần lượt là bệnh nhân và phiếu khám
    ngayKham = Column(Date, default=date.today, nullable=False)
    hoTenBenhNhan = Column(String(50), nullable=False)
    tienKham = Column(Float, default=0)
    tienThuoc = Column(Float, default=0)
    nguoiDung_id = Column(Integer, ForeignKey(NguoiDung.id), nullable=False) #người đăng ký
    phieuKham_id = Column(Integer, ForeignKey(PhieuKham.id), nullable=False)
    da_thanh_toan = Column(Boolean, default=False)

    # def tinh_tong_tien_thuoc(self, session):
    #     total = 0
    #     chiTietPhieuKhams = session.query(ChiTietPhieuKham).filter_by(phieuKham_id=self.phieuKham_id).all()
    #     for ct in chiTietPhieuKhams:
    #         total += ct.soLuong * ct.thuoc.price  # Giả sử `thuoc` có thuộc tính `price`
    #     self.tienThuoc = total


class LichKham(Base): # chứa ngày khám để danh sách khám nó lấy về cái id ngày khám đó
    ngayKham = Column(Date, default=date.today, nullable=False)
    danhSachKham = relationship('DanhSachKham', backref='lichKham', lazy=True)


class DanhSachKham(Base):
    lichNgayKham_id = Column(Integer, ForeignKey(LichKham.id), nullable=False)
    chiTietDanhSachKham = relationship('ChiTietDanhSachKham', backref='danhSachKham', lazy=True)


class ChiTietDanhSachKham(Base): # trong class diagram la ThemBenhNhan
    danhSachKham_id = Column(Integer, ForeignKey(DanhSachKham.id), nullable=False)
    nguoiDung_id = Column(Integer, ForeignKey(NguoiDung.id), nullable=False)
    #nguoi dùng ở đây là tất cả - người đăng ký
    hoTen = Column(String(100), nullable=False)
    gioiTinh = Column(Enum(GioiTinh), default=GioiTinh.Nam)
    namSinh = Column(Date, nullable=False)
    soDienThoai = Column(String(10), nullable=False)
    diaChi = Column(String(100), nullable=False)

    def nam_sinh(self):
        if self.namSinh:
            return self.namSinh.year
        else:
            None



class QuyDinh(Base):
    soTienKham = Column(Float, default=100000, nullable=False)
    soLoaiThuoc = Column(Integer, default=30, nullable=False)
    soBenhNhan = Column(Integer, default=40, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        #
        loaiThuoc1 = LoaiThuoc(tenLoai="Thuốc Ngủ")
        loaiThuoc2 = LoaiThuoc(tenLoai="Thuốc Nhứt Đầu")

        qd = QuyDinh(soTienKham=100000, soLoaiThuoc=30, soBenhNhan=40)
        db.session.add(qd)
        db.session.commit()

        import hashlib
        u = NguoiDung(hoTen='Quản Trị Viên',
                      anhDaiDien='https://res.cloudinary.com/dstjar2iy/image/upload/v1712391157/lwocwuc4opc6c9kl6fcw.jpg',
                      username='admin',
                      password=str(hashlib.md5("1".encode('utf-8')).hexdigest()),
                      vaiTro_NguoiDung=VaiTroNguoiDung.ADMIN)

        db.session.add(u)
        db.session.commit()

