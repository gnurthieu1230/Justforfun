import re
import urllib.parse
import json
import datetime
import os
import time

LOG_FILE = "phone_check_history.log"
REPORT_FILE = "scan_reports.json"

# --- 1. GHI NHẬT KÝ & XUẤT BÁO CÁO ---
def ghi_nhat_ky(noi_dung):
    thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{thoi_gian}] {noi_dung}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f" [!] Lỗi ghi file log: {e}")

def xuat_bao_cao_json(data):
    try:
        reports = []
        if os.path.exists(REPORT_FILE):
            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                try:
                    reports = json.load(f)
                except:
                    reports = []
        reports.append(data)
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f" [!] Lỗi xuất JSON: {e}")

# --- 2. PHÂN TÍCH ĐẦU SỐ & LOẠI HÌNH THUÊ BAO ---
def phan_tich_so_dien_thoai(sdt):
    sdt_clean = re.sub(r'[\s\-\.\+]', '', sdt)
    if sdt_clean.startswith("84"):
        sdt_clean = "0" + sdt_clean[2:]

    if not re.match(r'^0[1-9][0-9]{8,9}$', sdt_clean):
        return None, "Định dạng không hợp lệ (Cần số điện thoại từ 10 đến 11 chữ số)."

    dau_so_3 = sdt_clean[:3]
    dau_so_2 = sdt_clean[:2]
    
    nha_mang = "Không xác định"
    loai_hinh = "Di động"

    viettel = ["032", "033", "034", "035", "036", "037", "038", "039", "086", "096", "097", "098"]
    vinaphone = ["081", "082", "083", "084", "085", "088", "091", "094"]
    mobifone = ["070", "076", "077", "078", "079", "089", "090", "093"]
    vietnamobile = ["056", "058", "092"]
    mvno = ["087", "055"] # iTelecom, Wintel...

    if dau_so_3 in viettel:
        nha_mang = "Viettel"
    elif dau_so_3 in vinaphone:
        nha_mang = "VinaPhone"
    elif dau_so_3 in mobifone:
        nha_mang = "MobiFone"
    elif dau_so_3 in vietnamobile:
        nha_mang = "Vietnamobile"
    elif dau_so_3 in mvno:
        nha_mang = "Mạng ảo (MVNO - Wintel/iTelecom)"
        loai_hinh = "Mạng ảo (Tỷ lệ SIM rác cao)"
    elif dau_so_2 in ["02"]:
        nha_mang = "Mạng bàn / Cố định"
        loai_hinh = "Điện thoại cố định"

    return {
        "sdt_goc": sdt,
        "sdt_chuan": sdt_clean,
        "sdt_quoc_te": f"+84{sdt_clean[1:]}",
        "nha_mang": nha_mang,
        "loai_hinh": loai_hinh
    }, None

# --- 3. DOWK TRINH SÁT OSINT MẠNG XÃ HỘI & DATABASE ---
def tao_dork_osint(sdt_info):
    sdt = sdt_info["sdt_chuan"]
    sdt_intl = sdt_info["sdt_quoc_te"]

    # Tạo truy vấn tìm kiếm nâng cao
    query_scam = f'"{sdt}" OR "{sdt_intl}" "lừa đảo" OR "spam" OR "báo cáo"'
    query_social = f'"{sdt}" site:facebook.com OR site:zalo.me'

    links = {
        "Google Scam Dork": f"https://www.google.com/search?q={urllib.parse.quote(query_scam)}",
        "Facebook / Zalo Search": f"https://www.google.com/search?q={urllib.parse.quote(query_social)}",
        "Cổng Không Lừa Đảo": "https://khongluadao.org",
        "Chống Lừa Đảo VN": "https://chongluadao.vn"
    }
    return links

# --- 4. ĐÁNH GIÁ RỦI RO & PHÂN TÍCH HEURISTIC ---
def danh_gia_rui_ro(sdt_info):
    diem_rui_ro = 0
    canh_bao = []

    if "Mạng ảo" in sdt_info["nha_mang"]:
        diem_rui_ro += 25
        canh_bao.append("⚠️ Sử dụng đầu số mạng ảo (MVNO), thường được dùng làm SIM phụ hoặc SIM rác.")

    if sdt_info["loai_hinh"] == "Điện thoại cố định":
        diem_rui_ro += 15
        canh_bao.append("ℹ️ Số cố định: Cần xác minh xem có giả danh tổng đài cơ quan/ngân hàng không.")

    if diem_rui_ro >= 40:
        muc_danh_gia = "🔴 RỦI RO CAO / CẦN THẬM TRỌNG"
    elif diem_rui_ro >= 20:
        muc_danh_gia = "🟡 CÓ DẤU HIỆU CẦN CHÚ Ý"
    else:
        muc_danh_gia = "🟢 BÌNH THƯỜNG / CHƯA PHÁT HIỆN BẤT THƯỜNG"

    return muc_danh_gia, diem_rui_ro, canh_bao

# --- 5. TÍNH NĂNG QUÉT TỪNG SỐ ---
def quet_don_le(sdt_input):
    info, err = phan_tich_so_dien_thoai(sdt_input)
    if err:
        print(f"\n [!] Lỗi: {err}")
        return

    muc_danh_gia, diem, canh_bao = danh_gia_rui_ro(info)
    links = tao_dork_osint(info)

    print("\n" + "═" * 70)
    print(" [*] KẾT QUẢ PHÂN TÍCH CHI TIẾT")
    print("═" * 70)
    print(f" [+] Số điện thoại chuẩn : {info['sdt_chuan']} ({info['sdt_quoc_te']})")
    print(f" [+] Nhà mạng quản lý   : {info['nha_mang']}")
    print(f" [+] Loại hình thuê bao  : {info['loai_hinh']}")
    print(f" [+] Đánh giá rủi ro     : {muc_danh_gia} (Điểm cảnh báo: {diem}/100)")

    if canh_bao:
        print("\n [!] CẢNH BÁO TỰ ĐỘNG:")
        for cb in canh_bao:
            print(f"     └── {cb}")

    print("\n [*] LIÊN KẾT TRINH SÁT OSINT (MỞ ĐỂ TRA CỨU DỮ LIỆU CỘNG ĐỒNG):")
    for ten_link, url in links.items():
        print(f"     └── {ten_link:<22}: {url}")

    # Lưu dữ liệu
    log_msg = f"SDT: {info['sdt_chuan']} | Mạng: {info['nha_mang']} | Đánh giá: {muc_danh_gia}"
    ghi_nhat_ky(log_msg)

    report_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "info": info,
        "risk_score": diem,
        "risk_level": muc_danh_gia,
        "warnings": canh_bao
    }
    xuat_bao_cao_json(report_data)

    print("\n" + "═" * 70)
    print(" [✓] Đã ghi nhật ký vào 'phone_check_history.log' & xuất JSON vào 'scan_reports.json'.")

# --- 6. TÍNH NĂNG QUÉT HÀNG LOẠT TỪ FILE ---
def quet_hang_loat():
    file_path = input("\n[?] Nhập đường dẫn file chứa danh sách SĐT (mỗi số 1 dòng): ").strip()
    if not os.path.exists(file_path):
        print(" [!] File không tồn tại.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        danh_sach = [line.strip() for line in f if line.strip()]

    print(f"\n [*] Bắt đầu kiểm tra {len(danh_sach)} số điện thoại...\n")
    for idx, sdt in enumerate(danh_sach, 1):
        print(f"[{idx}/{len(danh_sach)}] Đang xử lý: {sdt}")
        quet_don_le(sdt)
        time.sleep(0.5)

# --- 7. MENU ĐIỀU KHIỂN ---
def main():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║          PHONE SCAM RECONNAISSANCE & OSINT SUITE                  ║")
        print("║       Hệ Thống Phân Tích & Báo Cáo Số Điện Thoại Lừa Đảo          ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print("\n [1] Quét & Phân tích đơn lẻ 1 số điện thoại")
        print(" [2] Quét hàng loạt từ file danh sách (.txt)")
        print(" [3] Xem lịch sử nhật ký đã quét (Log file)")
        print(" [4] Thoát chương trình")

        chon = input("\n[?] Chọn chức năng (1-4): ").strip()

        if chon == "1":
            sdt = input("\n[?] Nhập SĐT cần tra cứu: ").strip()
            if sdt:
                quet_don_le(sdt)
            input("\nNhấn Enter để quay lại menu...")
        elif chon == "2":
            quet_hang_loat()
            input("\nNhấn Enter để quay lại menu...")
        elif chon == "3":
            print("\n" + "═" * 70)
            print(" [*] LỊCH SỬ NHẬT KÝ QUÉT")
            print("═" * 70)
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print(" Chưa có dữ liệu lịch sử.")
            input("\nNhấn Enter để quay lại menu...")
        elif chon == "4":
            print("\n [✓] Cảm ơn cậu đã sử dụng tool. Tạm biệt!")
            break

if __name__ == "__main__":
    main()
