import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

# Danh sách các tỉnh thành (trước sáp nhập)
provinces = [
    "an-giang", "ba-ria-vung-tau", "bac-giang", "bac-kan", "bac-lieu", "bac-ninh",
    "ben-tre", "binh-duong", "binh-dinh", "binh-phuoc", "binh-thuan", "ca-mau",
    "can-tho", "cao-bang", "da-nang", "dak-lak", "dak-nong", "dien-bien", "dong-nai",
    "dong-thap", "gia-lai", "ha-giang", "ha-nam", "ha-noi", "ha-tinh", "hai-duong",
    "hai-phong", "hau-giang", "hoa-binh", "hung-yen", "khanh-hoa", "kien-giang",
    "kon-tum", "lai-chau", "lam-dong", "lang-son", "lao-cai", "long-an", "nam-dinh",
    "nghe-an", "ninh-binh", "ninh-thuan", "phu-tho", "phu-yen", "quang-binh",
    "quang-nam", "quang-ngai", "quang-ninh", "quang-tri", "soc-trang", "son-la",
    "tay-ninh", "thai-binh", "thai-nguyen", "thanh-hoa", "thua-thien-hue", "tien-giang",
    "tp-ho-chi-minh", "tra-vinh", "tuyen-quang", "vinh-long", "vinh-phuc", "yen-bai"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

@st.cache_data

def crawl_province_data(province):
    url = f"https://doanhnghiep.me/{province}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        blocks = soup.find_all("div", class_="col-md-6")
        for block in blocks:
            title = block.find("a").text.strip()
            info = block.get_text("\n").split("\n")
            mst = next((line.replace("Mã số thuế:", "").strip() for line in info if "Mã số thuế:" in line), "")
            nguoidd = next((line.replace("Người đại diện:", "").strip() for line in info if "Người đại diện:" in line), "")
            diachi = info[-1].strip() if info else ""
            results.append({"Tên hộ kinh doanh": title, "Mã số thuế": mst, "Người đại diện": nguoidd, "Địa chỉ": diachi})
        return results
    except Exception as e:
        return []

st.title("🧾 Tra cứu Hộ Kinh Doanh theo tỉnh thành")

selected_provinces = st.multiselect("Chọn tỉnh thành để tra cứu:", provinces, default=["bac-ninh"])

if st.button("🔍 Bắt đầu tra cứu"):
    all_data = []
    for prov in selected_provinces:
        st.write(f"⏳ Đang xử lý: {prov.replace('-', ' ').title()}...")
        data = crawl_province_data(prov)
        if data:
            all_data.extend(data)
        else:
            st.warning(f"⚠ Không lấy được dữ liệu từ tỉnh {prov}")

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"✅ Đã tải {len(df)} dòng dữ liệu từ {len(selected_provinces)} tỉnh thành.")
        st.dataframe(df)

        def convert_df(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="HoKinhDoanh")
            return output.getvalue()

        excel_data = convert_df(df)
        st.download_button(
            label="📥 Tải xuống Excel",
            data=excel_data,
            file_name="ho_kinh_doanh.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ Không thu được dữ liệu nào.")
