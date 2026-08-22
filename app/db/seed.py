from datetime import datetime, timezone, timedelta
# Import SessionLocal từ database.py của bạn
from app.db.database import SessionLocal
from app.models.role import SystemRoleModel, ClubRoleModel
from app.models.user import UserModel
from app.models.club import ClubModel
from app.models.club_members import *
from app.models.activity import *
from app.core.security import get_password_hash


def seed_data():

    db = SessionLocal()

    # b1 tạo các role
    try:

        role_admin = SystemRoleModel(
            name="ADMIN", description="QUẢN LÝ MỌI THỨ TRONG HỆ THỐNG")
        role_user = SystemRoleModel(
            name="USER", description="NGƯỜI DÙNG HỆ THỐNG")

        db.add(role_admin)
        db.add(role_user)

        role_owner = ClubRoleModel(name="OWNER", description="Chủ nhiệm CLB")
        role_member = ClubRoleModel(
            name="MEMBER", description="Thành viên CLB")
        db.add(role_owner)
        db.add(role_member)

        db.flush()  # lưu giả để lấy id role, chưa commit nha

        # -------------------------------------------------------------
        # BƯỚC 2: TẠO NGƯỜI DÙNG MẪU
        # -------------------------------------------------------------
        mat_khau_ma_hoa = get_password_hash("123456")

        user_leader = UserModel(
            email="leader@test.com",
            password_hash=mat_khau_ma_hoa,
            full_name="Nguyễn Văn Leader",
            role_id=role_user.id
        )
        user_member = UserModel(
            email="member@test.com",
            password_hash=mat_khau_ma_hoa,
            full_name="Trần Thị Member",
            role_id=role_user.id
        )
        db.add(user_leader)
        db.add(user_member)
        db.flush()  # Lấy ID của 2 user

        # -------------------------------------------------------------
        # BƯỚC 3: TẠO CÂU LẠC BỘ
        # -------------------------------------------------------------
        clb_lap_trinh = ClubModel(
            name="CLB Lập Trình PTIT",
            description="Nơi học hỏi backend và frontend",
            owner_id=user_leader.id
        )
        db.add(clb_lap_trinh)
        db.flush()  # Lấy ID của CLB

        # -------------------------------------------------------------
        # BƯỚC 4: GÁN THÀNH VIÊN VÀO CLB
        # -------------------------------------------------------------
        thanh_vien_1 = ClubMemberModel(
            club_id=clb_lap_trinh.id,
            user_id=user_leader.id,
            role_id=role_owner.id
        )
        thanh_vien_2 = ClubMemberModel(
            club_id=clb_lap_trinh.id,
            user_id=user_member.id,
            role_id=role_member.id
        )
        db.add(thanh_vien_1)
        db.add(thanh_vien_2)

        # -------------------------------------------------------------
        # BƯỚC 5: TẠO HOẠT ĐỘNG
        # -------------------------------------------------------------
        nhiem_vu = ClubActivityModel(
            club_id=clb_lap_trinh.id,
            title="Làm bài tập lớn FastAPI",
            description="Dựng API kết nối cơ sở dữ liệu",
            assignee_id=user_member.id,
            status=ActivityStatus.TODO,
            priority=ActivityPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(nhiem_vu)

        # -------------------------------------------------------------
        # CHỐT LƯU TOÀN BỘ VÀO DATABASE
        # -------------------------------------------------------------
        db.commit()
        print("🎉 Nạp dữ liệu mẫu thành công!")

    except Exception as e:
        db.rollback()
        print(f"Có lỗi sự cố hệ thống: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
