from cryptography.fernet import Fernet
# 1. Tạo một chiếc chìa khóa bí mật tự động
key = Fernet.generate_key()
cipher = Fernet(key)
# 2. Thông điệp cậu muốn mã hóa (có thể đổi chữ)
message = "heheheeheheh"
print(f"Ma hoa thanh: {message}")
# 3. Tiến hành khóa (mã hóa) thông điệp
encrypted = cipher.encrypt(message.encode())
print(f"Ma hoa thanh: {encrypted}")
# 4. Mở khóa (giải mã) lại xem có đúng không
decrypted = cipher.decrypt(encrypted).decode()
print(f"Giai ma ra: {decrypted}")
