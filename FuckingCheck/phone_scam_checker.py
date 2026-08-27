import re
import urllib.parse
import json
import urllib.request
import datetime
import os

# --- 1. TỰ ĐỘNG GHI NHẬT KÝ (LOGGING) ---
def ghi_nhat_ky(noi_dung):
    thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{thoi_gian}] {noi_dung}\n"
    try:
        with open("phone_check_history.log", "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f" [!] Không thể ghi file log: {e}")

# --- 2. CHUẨN HÓA VÀ NHẬN DIỆN ĐẦU SỐ VIỆT NAM ---
def phan_tich_dau_so(sdt):
    # Xóa khoảng trắng, dấu gạch ngang
    sdt_clean = re.sub(r'[\s\-\.\+]', '', sdt)
    
    # Chuyển đầu +84 thành 0
    if sdt_clean.startswith("84"):
        sdt_clean = "0" + sdt_clean[2:]

    # Kiểm tra định dạng số điện thoại Việt Nam (10 chữ số)
    if not re.match(r'^0[3|5|7|8|9][0-9]{8}$', sdt_clean):
        return None, "Định dạng số điện thoại không hợp lệ (Cần 10 chữ số bắt đầu bằng 03, 05, 07, 08, 09 hoặc +84)"

    # Nhận diện nhà mạng Việt Nam
    dau_so_3 = sdt_clean[:3]
    nha_mang = "Không xác định"

    viettel = ["032", "033", "034", "035", "036", "037", "038", "039", "086", "096", "097", "098"]
    vinaphone = ["081", "082", "083", "084", "085", "088", "091", "094"]
    mobifone = ["070", "076", "077", "078", "079", "089", "090", "093"]
    vietnamobile = ["056", "058", "092"]
    iTelecom = ["087"]

    if dau_so_3 in viettel:
        nha_mang = "Viettel"
    elif dau_so_3 in vinaphone:
        nha_mang = "VinaPhone"
    elif dau_so_3 in mobifone:
        nha_mang = "MobiFone"
    elif dau_so_3 in vietnamobile:
        nha_mang = "Vietnamobile"
    elif dau_so_3 in iTelecom:
        nha_mang = "iTelecom (Mạng ảo MVNO)"

    return sdt_clean, nha_mang

# --- 3. ĐÁNH GIÁ MỨC ĐỘ RỦI RRO DỰA TRÊN DẤU HIỆU HIỆN CÓ ---
def dánh_gia_rui_ro(sdt, nha_mang):
    diem_rui_ro = 0
    canh_bao = []

    # Kiểm tra các đầu số vệ tinh/quốc tế lạ nếu người dùng nhập số quốc tế
    if sdt.startswith("+") and not sdt.startswith("+84"):
        diem_rui_ro += 40
        canh_bao.append("⚠️ Số điện thoại từ quốc tế (Cần cảnh giác nếu giả danh cơ quan công an/ngân hàng)")

    # SIM rác / Mạng ảo thường bị lạm dụng để spam
    if nha_mang in ["Vietnamobile", "iTelecom (Mạng ảo MVNO)"]:
        diem_rui_ro += 20
        canh_bao.append("ℹ️ Dải số thuộc nhà mạng ảo/SIM phụ, thường có tỉ lệ SIM rác cao")

    # Mức độ đánh giá
    if diem_rui_ro >= 50:
        muc_do = "🔴 RỦI RO CAO"
    elif diem_rui_ro >= 20:
        muc_do = "🟡 CẦN CHÚ Ý"
    else:
        muc_do = "🟢 BÌNH THƯỜNG / CHƯA PHÁT HIỆN DẤU HIỆU BẤT THƯỜNG"

    return muc_do, canh_bao

# --- 4. TẠO TRUY VẤN TRINHSÁT OSINT DỮ LIỆU CÔNG KHAI ---
def tao_link_trinh_sat(sdt):
    sdt_intl = "+84" + sdt[1:] if sdt.startswith("0") else sdt
    
    # Tạo liên kết tìm kiếm dấu vết báo cáo lừa đảo trên Google
    query_google = f'"{sdt}" OR "{sdt_intl}" "lừa đảo" OR "spam" OR "đòi nợ"'
    url_google = f"https://www.google.com/search?q={urllib.parse.quote(query_google)}"

    # Tạo liên kết tra cứu trên trang chống lừa đảo
    url_chongluadao = f"https://chongluadao.vn"

    return url_google, url_chongluadao

# --- 5. CHƯƠNG TRÌNH CHÍNH ---
def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          PHONE SCAM DETECTOR & OSINT RECON TOOL                   ║")
    print("║       Kiểm Tra & Phân Tích Dấu Hiệu Số Điện Thoại Lừa Đảo         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")

    sdt_nhap = input("\n[?] Nhập số điện thoại cần kiểm tra (Ví dụ: 0981234567 hoặc +84981234567): ").strip()
    
    if not sdt_nhap:
        print(" [!] Số điện thoại không được để trống.")
        return

    sdt_chuan, nha_mang = phan_tich_dau_so(sdt_nhap)

    if not sdt_chuan:
        print(f"\n [!] Lỗi: {nha_mang}")
        return

    muc_do, canh_bao = dánh_gia_rui_ro(sdt_chuan, nha_mang)
    url_google, url_cld = tao_link_trinh_sat(sdt_chuan)

    print("\n" + "═" * 70)
    print(" [*] THÔNG TIN PHÂN TÍCH SỐ ĐIỆN THOẠI")
    print("═" * 70)
    print(f" [+] Số điện thoại chuẩn : {sdt_chuan} (Định dạng quốc tế: +84{sdt_chuan[1:]})")
    print(f" [+] Nhà cung cấp mạng  : {nha_mang}")
    print(f" [+] Đánh giá rủi ro     : {muc_do}")

    if canh_bao:
        print("\n [!] CÁC CẢNH BÁO LƯU Ý:")
        for cb in canh_bao:
            print(f"     └── {cb}")

    print("\n [*] DẤU VẾT TRINH SÁT OSINT (MỞ TRÊN TRÌNH DUYỆT ĐỂ XEM BÁO CÁO COMMUNITY):")
    print(f"     └── Google Search Scam Log : {url_google}")
    print(f"     └── Cơ sở dữ liệu Cổng An Toàn Thông Tin: https://khongluadao.org")

    ghi_nhat_ky(f"Kiểm tra SDT: {sdt_chuan} | Nhà mạng: {nha_mang} | Kết quả: {muc_do}")

    print("\n" + "═" * 70)
    print(" [✓] Đã hoàn thành phân tích và ghi nhật ký vào file: phone_check_history.log")
    print("═" * 70)

if __name__ == "__main__":
    main()
