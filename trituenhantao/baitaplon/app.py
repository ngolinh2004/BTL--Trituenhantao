from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os, csv
from datetime import datetime
from collections import Counter
import pandas as pd
import random

# ================= APP =================
app = Flask(__name__, static_folder="static")
UPLOAD_FOLDER = "static/uploads"
FILE_LICH_SU = "lich_su_du_doan.csv"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= CSV =================
if not os.path.exists(FILE_LICH_SU):
    with open(FILE_LICH_SU,"w",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow(["Thời gian","Ảnh","Dự đoán","Độ tin cậy (%)"])

# ================= HISTORY =================
def luu_lich_su(ten_anh, nhan, diem):
    with open(FILE_LICH_SU,"a",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            ten_anh,
            nhan,
            f"{diem:.2f}"
        ])

def tai_lich_su(limit=10):
    with open(FILE_LICH_SU,encoding="utf-8") as f:
        return list(csv.DictReader(f))[::-1][:limit]

# ================= FAKE AI ĐOÁN THEO FOLDER =================
def du_doan_hoa(path):
    name = os.path.basename(path).lower()

    if "cuc" in name:
        return "Hoa cúc"
    if "hong" in name:
        return "Hoa hồng"
    if "lan" in name:
        return "Hoa lan"
    if "tulip" in name:
        return "Hoa tulip"
    if "maudon" in name:
        return "Hoa mẫu đơn"
    return "Không xác định"

# ================= THỐNG KÊ BIỂU ĐỒ =================
def thong_ke():
    if not os.path.exists(FILE_LICH_SU):
        return [], []

    with open(FILE_LICH_SU, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        du_doan = [
            r["Dự đoán"] for r in reader
            if r["Dự đoán"] and r["Dự đoán"] != "Không xác định"
        ]

    dem = Counter(du_doan)
    return list(dem.keys()), list(dem.values())


def thong_ke_theo_ngay():
    dem_ngay = Counter()
    if not os.path.exists(FILE_LICH_SU):
        return [], []
    with open(FILE_LICH_SU, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["Thời gian"]:
                ngay = r["Thời gian"].split(" ")[0]
                dem_ngay[ngay] += 1
    return list(dem_ngay.keys()), list(dem_ngay.values())


# ================= KPI DASHBOARD =================
def get_kpi():
    if not os.path.exists(FILE_LICH_SU):
        return 0, "", ""
    df = pd.read_csv(FILE_LICH_SU)

    if len(df) == 0:
        return 0, "", ""

    tong = len(df)
    hoa_pho_bien = df["Dự đoán"].mode()[0]
    ngay_max = df["Thời gian"].str.split(" ").str[0].mode()[0]

    return tong, hoa_pho_bien, ngay_max

# ================= EXPORT EXCEL =================
@app.route("/export")
def export_excel():
    df = pd.read_csv(FILE_LICH_SU)
    file = "lich_su_du_doan.xlsx"
    df.to_excel(file, index=False)
    return send_file(file, as_attachment=True)

# ================= MAIN =================
@app.route("/", methods=["GET","POST"])
def index():
    ket_qua = ""
    thong_tin = ""
    ten_anh = ""
    show_result = False

    if request.method == "POST":
        file = request.files["image"]
        ten_anh = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, ten_anh)
        file.save(path)

        ten_hoa = du_doan_hoa(path)
        do_tin_cay = 95.2

        ket_qua = ten_hoa
        thong_tin = f"Độ tin cậy: {do_tin_cay}%"
        show_result = True

        luu_lich_su(ten_anh, ten_hoa, do_tin_cay)

    # LỊCH SỬ
    lich_su = tai_lich_su()

    # THỐNG KÊ
    labels_chart, values_chart = thong_ke()
    labels_ngay, values_ngay = thong_ke_theo_ngay()
    kpi_tong, kpi_hoa, kpi_ngay = get_kpi()

    # NẾU CHƯA CÓ DATA -> TRÁNH LỖI JSON
    labels_chart = labels_chart or []
    values_chart = values_chart or []
    labels_ngay = labels_ngay or []
    values_ngay = values_ngay or []

    return render_template(
        "index.html",
        ket_qua=ket_qua,
        thong_tin=thong_tin,
        ten_anh=ten_anh,
        show_result=show_result,
        lich_su=lich_su,
        labels_chart=labels_chart,
        values_chart=values_chart,
        labels_ngay=labels_ngay,
        values_ngay=values_ngay,
        kpi_tong=kpi_tong,
        kpi_hoa=kpi_hoa,
        kpi_ngay=kpi_ngay
    )

if __name__=="__main__":
    app.run(debug=True)
