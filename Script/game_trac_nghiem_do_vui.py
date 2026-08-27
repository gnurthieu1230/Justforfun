print("=== GAME TRAC NGHIEM TINH CACH ===")
print("Khi dong ho bao thuc vao luc 6h sang, cau se:")
print("1. Day ngay lap tuc, tap the duc!")
print("2. Tat bao thuc ngu tiep 5 phut (thanh 2 tieng).")
print("3. Trum chan khoc tham vi lai phai di hoc di/di lam.")

chon = input("nhap lua chon cua cau (1, 2 hoac 3: ")

if chon == "1":
	print("\n👉 Cau la cho soi nang no! Sieu nguyen tac va day nang luong!")
elif chon == "2":
	print("\n👉 Cau la con lon luoi de thuong! Mon khoai khau cua cau la cai giuong!")
elif chon == "3":
	print("\n👉 Cau la meo tram cam! Luon hoai nghi ve nhan sinh!")
else:
	print("\n👉 Cau go cai gi the? Bam sai so roi kia kia!")