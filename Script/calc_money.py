tiep_tuc = "co"

while tiep_tuc == "co":
    print("\n=== MÁY TÍNH TIỀN TRÀ SỮA ===")
    print("1. Trà sữa truyền thống: 30,000 VNĐ")
    print("2. Trà sữa Matcha: 35,000 VNĐ")
    print("3. Trà sữa Taro: 40,000 VNĐ")

    mon = input("Chọn món (1, 2 hoặc 3): ")
    so_luong = int(input("Nhập số lượng ly: "))

    # 1. Xác định giá tiền từng món
    if mon == "1":
        gia = 30000
    elif mon == "2":
        gia = 35000
    elif mon == "3":
        gia = 40000
    else:
        print("Món không hợp lệ!")
        gia = 0

    # 2. Tính tổng tiền nếu chọn đúng món
    if gia > 0:
        tong_tien = gia * so_luong
        print(f"\n👉 Tổng tiền của cậu là: {tong_tien} VNĐ")

        tien_khach_dua = int(input("Nhập số tiền khách đưa: "))

        # 3. Tính tiền thừa hoặc thiếu
        if tien_khach_dua >= tong_tien:
            tien_thua = tien_khach_dua - tong_tien
            print(f"✅ Thanh toán thành công! Trả lại khách: {tien_thua} VNĐ")
        else:
            tien_thieu = tong_tien - tien_khach_dua
            print(f"❌ Khách đưa thiếu {tien_thieu} VNĐ rồi cậu ơi!")

    # 4. Hỏi xem có muốn tính đơn mới không
    tiep_tuc = input("\nTính đơn tiếp theo? (gõ 'co' hoặc 'khong'): ")

print("\nCảm ơn cậu! Hết ca làm việc rồi, nghỉ ngơi thôi! 🎉")
