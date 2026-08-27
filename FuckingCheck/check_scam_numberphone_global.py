import os
import re
import json
import time
import datetime
import urllib.parse

# Import thư viện phonenumbers chính thức từ Google
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, number_type, PhoneNumberType
except ImportError:
    print("[!] Chưa cài đặt thư viện 'phonenumbers'. Hãy chạy: pip install phonenumbers")
    exit(1)

LOG_FILE = "global_phone_history.log"
REPORT_FILE = "global_scan_reports.json"

# --- 1. GHI NHẬT KÝ & BÁO CÁO ---
def ghi_log(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def luu_json(data):
    reports = []
    if os.path.exists(REPORT_FILE):
        try:
            with open(REPORT_FILE, "r", encoding="utf-8") as f:
                reports = json.load(f)
        except:
            reports = []
    reports.append(data)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=4)

# --- 2. PHÂN TÍCH CHUYÊN SÂU SỐ ĐIỆN THOẠI TOÀN CẦU ---
def phan_tich_so_toan_cau(phone_str, default_region="VN"):
    try:
        # Tự động thêm dấu + nếu người dùng nhập mã quốc gia không có +
        if not phone_str.startswith("+") and not phone_str.startswith("0"):
            phone_str = "+" + phone_str

        # Parse số điện thoại bằng Google Lib
        parsed_num = phonenumbers.parse(phone_str, default_region)

        # Kiểm tra tính hợp lệ
        is_valid = phonenumbers.is_valid_number(parsed_num)
        is_possible = phonenumbers.is_possible_number(parsed_num)

        if not is_possible:
            return None, "Số điện thoại có độ dài hoặc cấu trúc không khả thi."

        # Định dạng chuẩn quốc tế E.164
        formatted_e164 = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
        formatted_intl = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        # Tra cứu vị trí quốc gia / vùng miền (Tiếng Việt)
        quoc_gia = geocoder.description_for_number(parsed_num, "vi") or geocoder.description_for_number(parsed_num, "en") or "Không xác định"

        # Tra cứu nhà mạng
        nha_mang = carrier.name_for_number(parsed_num, "vi") or carrier.name_for_number(parsed_num, "en") or "Không xác định / Mạng cố định"

        # Tra cứu múi giờ
        mui_gio = list(timezone.time_zones_for_number(parsed_num))

        # Phân loại loại hình thuê bao
        num_type_code = number_type(parsed_num)
        loai_hinh_map = {
            PhoneNumberType.MOBILE: "Di động (Mobile)",
            PhoneNumberType.FIXED_LINE: "Cố định / Bàn (Fixed Line)",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "Di động hoặc Cố định",
            PhoneNumberType.TOLL_FREE: "Tổng đài miễn cước (Toll-Free)",
            PhoneNumberType.PREMIUM_RATE: "Tổng đài tính cước cao (Premium Rate)",
            PhoneNumberType.VOIP: "Mạng ảo / Điện thoại Internet (VOIP)",
            PhoneNumberType.PERSONAL_NUMBER: "Số cá nhân",
            PhoneNumberType.PAGER: "Máy nhắn tin",
            PhoneNumberType.UAN: "Tổng đài dịch vụ (UAN)",
            PhoneNumberType.UNKNOWN: "Không xác định"
        }
        loai_hinh = loai_hinh_map.get(num_type_code, "Không xác định")

        return {
            "sdt_goc": phone_str,
            "e164": formatted_e164,
            "intl_format": formatted_intl,
            "is_valid": is_valid,
            "quoc_gia": quoc_gia,
            "nha_mang": nha_mang,
            "mui_gio": mui_gio,
            "loai_hinh": loai_hinh,
            "type_code": num_type_code
        }, None

    except phonenumbers.NumberParseException as e:
        return None, f"Lỗi định dạng số điện thoại: {e}"

# --- 3. ĐÁNH GIÁ RỦI RO LƯỜNG GẠT (HEURISTIC RISK SCORE) ---
def danh_gia_rui_ro_global(info):
    score = 0
    warnings = []

    if not info["is_valid"]:
        score += 30
        warnings.append("⚠️ Số điện thoại không hợp lệ theo quy chuẩn viễn thông quốc tế.")

    # VOIP (Điện thoại Internet) thường được dùng giả mạo vị trí
    if info["type_code"] == PhoneNumberType.VOIP:
        score += 40
        warnings.append("🔴 Thuê bao VOIP (Điện thoại qua Internet): Tỷ lệ lừa đảo/mạo danh rất cao.")

    # Premium rate (Tổng đài cước cao)
    if info["type_code"] == PhoneNumberType.PREMIUM_RATE:
        score += 50
        warnings.append("🔴 Đầu số tính cước phí rất cao khi gọi lại (Cạm bẫy trừ tiền tài khoản).")

    # Số quốc tế gọi về (Nếu không phải Việt Nam)
    if info["quoc_gia"] not in ["Việt Nam", "Vietnam"]:
        score += 20
        warnings.append(f"🌐 Số điện thoại xuất xứ quốc tế: {info['quoc_gia']}.")

    # Đánh giá chung
    if score >= 50:
        level = "🔴 RỦI RO CAO - CẦN CẢNH GIÁC"
    elif score >= 20:
        level = "🟡 CHÚ Ý - CÓ DẤU HIỆU CẦN XÁC MINH"
    else:
        level = "🟢 BÌNH THƯỜNG / CHƯA PHÁT HIỆN DẤU HIỆU BẤT THƯỜNG"

    return level, score, warnings

# --- 4. TẠO TÌM KIẾM OSINT TOÀN CẦU ---
def tao_link_osint_global(info):
    e164 = info["e164"]
    clean_num = e164.replace("+", "")

    # Google Dorks
    q_scam = f'"{e164}" OR "{clean_num}" "scam" OR "fraud" OR "lừa đảo" OR "spam"'
    
    return {
        "Google Global Scam Search": f"https://www.google.com/search?q={urllib.parse.quote(q_scam)}",
        "ScamAdviser Check": f"https://www.scamadviser.com/check-phone/{clean_num}",
        "WhoCallsMe Tracker": f"https://whocallsme.com/Phone-Number.aspx/{clean_num}",
        "Cổng Không Lừa Đảo (VN)": "https://khongluadao.org"
    }

# --- 5. TÍNH NĂNG THỰC THI ---
def quet_sdt(sdt_input):
    info, err = phan_tich_so_toan_cau(sdt_input)
    if err:
        print(f"\n [!] Lỗi: {err}")
        return

    level, score, warnings = danh_gia_rui_ro_global(info)
    osint_links = tao_link_osint_global(info)

    print("\n" + "═" * 70)
    print(" [*] KẾT QUẢ TRINH SÁT SỐ ĐIỆN THOẠI TOÀN CẦU (GLOBAL OSINT)")
    print("═" * 70)
    print(f" [+] Định dạng chuẩn E.164  : {info['e164']}")
    print(f" [+] Định dạng Quốc tế     : {info['intl_format']}")
    print(f" [+] Tình trạng số          : {'✅ Hợp lệ' if info['is_valid'] else '❌ Không hợp lệ'}")
    print(f" [+] Quốc gia / Vùng lãnh thổ: {info['quoc_gia']}")
    print(f" [+] Nhà mạng (Carrier)     : {info['nha_mang']}")
    print(f" [+] Loại hình kết nối      : {info['loai_hinh']}")
    print(f" [+] Múi giờ vị trí         : {', '.join(info['mui_gio'])}")
    print(f" [+] Đánh giá Mức độ Rủi ro : {level} (Điểm: {score}/100)")

    if warnings:
        print("\n [!] CẢNH BÁO TỰ ĐỘNG:")
        for w in warnings:
            print(f"     └── {w}")

    print("\n [*] DỮ LIỆU BÁO CÁO CỘNG ĐỒNG TOÀN CẦU (OSINT LINKS):")
    for name, url in osint_links.items():
        print(f"     └── {name:<25}: {url}")

    # Ghi file
    ghi_log(f"SDT: {info['e164']} | Quốc gia: {info['quoc_gia']} | Loai: {info['loai_hinh']} | KetQua: {level}")
    luu_json({
        "timestamp": datetime.datetime.now().isoformat(),
        "info": info,
        "risk_score": score,
        "risk_level": level,
        "warnings": warnings
    })

    print("\n" + "═" * 70)
    print(" [✓] Đã lưu báo cáo vào log và JSON.")

# --- 6. MENU ĐIỀU KHIỂN ---
def main():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║        GLOBAL PHONE RECONNAISSANCE & SCAM DETECTOR SUITE          ║")
        print("║      Hệ Thống Phân Tích & Trinh Sát Số Điện Thoại Toàn Cầu        ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print("\n [1] Kiểm tra 1 số điện thoại bất kỳ (Hỗ trợ tất cả quốc gia)")
        print(" [2] Kiểm tra danh sách SĐT hàng loạt từ file (.txt)")
        print(" [3] Xem lịch sử nhật ký (Log)")
        print(" [4] Thoát")

        choice = input("\n[?] Chọn chức năng (1-4): ").strip()

        if choice == "1":
            sdt = input("\n[?] Nhập SĐT kèm mã quốc gia (VD: +84981234567, +14155552671, +819012345678): ").strip()
            if sdt:
                quet_sdt(sdt)
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "2":
            path = input("\n[?] Nhập đường dẫn file txt: ").strip()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                for idx, num in enumerate(lines, 1):
                    print(f"\n[{idx}/{len(lines)}] Đang quét: {num}")
                    quet_sdt(num)
                    time.sleep(0.3)
            else:
                print("[!] File không tồn tại.")
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "3":
            print("\n" + "═" * 70)
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("Chưa có nhật ký.")
            input("\nNhấn Enter để tiếp tục...")
        elif choice == "4":
            print("\n [✓] Tạm biệt cậu!")
            break

if __name__ == "__main__":
    main()
