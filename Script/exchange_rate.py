PHI_DICH_VU = 1  # Phí dịch vụ 1%

print("=== HỆ THỐNG ĐỔI TIỀN BẢO VỆ CHỐNG SẬP (TRY-EXCEPT) ===")

# Bắt lỗi ngay từ bước nhập tỷ giá ban đầu
while True:
    try:
        ty_gia = float(input("Nhập tỷ giá 1 USD = bao nhiêu VND hôm nay: "))
        break
    except ValueError:
        print("❌ Tỷ giá phải là số! Vui lòng nhập lại.\n")

tiep_tuc = "co"

while tiep_tuc == "co":
    print("\n--- MENU ĐỔI TIỀN ---")
    print(f"(Tỷ giá: 1 USD = {ty_gia:,.0f} VND | Phí dịch vụ: {PHI_DICH_VU}%)")
    print("1. Đổi từ USD -> VND")
    print("2. Đổi từ VND -> USD")
    print("3. Cập nhật tỷ giá mới")
    
    chon = input("Chọn chức năng (1, 2 hoặc 3): ")

    if chon == "1":
        # Bắt lỗi khi nhập tiền USD
        while True:
            try:
                usd = float(input("Nhập số tiền USD: "))
                break
            except ValueError:
                print("❌ Số tiền phải là chữ số! Vui lòng nhập lại.")

        vnd_goc = usd * ty_gia
        phi_vnd = vnd_goc * (PHI_DICH_VU / 100)
        vnd_thuc_nhan = vnd_goc - phi_vnd
        
        print(f"\n💵 Tổng tiền gốc: {vnd_goc:,.0f} VND")
        print(f"💸 Phí dịch vụ ({PHI_DICH_VU}%): {phi_vnd:,.0f} VND")
        print(f"👉 Tiền khách THỰC NHẬN: {vnd_thuc_nhan:,.0f} VND")

    elif chon == "2":
        # Bắt lỗi khi nhập tiền VND
        while True:
            try:
                vnd = float(input("Nhập số tiền VND: "))
                break
            except ValueError:
                print("❌ Số tiền phải là chữ số! Vui lòng nhập lại.")

        usd_goc = vnd / ty_gia
        phi_usd = usd_goc * (PHI_DICH_VU / 100)
        usd_thuc_nhan = usd_goc - phi_usd
        
        print(f"\n💵 Tổng tiền gốc: {usd_goc:.2f} USD")
        print(f"💸 Phí dịch vụ ({PHI_DICH_VU}%): {phi_usd:.2f} USD")
        print(f"👉 Tiền khách THỰC NHẬN: {usd_thuc_nhan:.2f} USD")

    elif chon == "3":
        while True:
            try:
                ty_gia = float(input("Nhập tỷ giá USD mới: "))
                break
            except ValueError:
                print("❌ Tỷ giá phải là chữ số! Vui lòng nhập lại.")
        print(f"✅ Đã cập nhật tỷ giá mới: 1 USD = {ty_gia:,.0f} VND")

    else:
        print("❌ Lựa chọn không hợp lệ rồi cậu ơi!")

    tiep_tuc = input("\nCậu có muốn tiếp tục không? (gõ 'co' hoặc 'khong'): ")

print("\nCảm ơn cậu đã sử dụng dịch vụ! Tạm biệt nha! 👋")
