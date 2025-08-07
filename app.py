import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="Tra cứu Hộ kinh doanh - doanhnghiep.me", layout="wide")

st.title("🔍 Tra cứu Hộ kinh doanh theo tỉnh - doanhnghiep.me")

provinces = {
    # Miền Bắc
    "Hà Nội": "ha-noi",
    "Hải Phòng": "hai-phong",
    "Quảng Ninh": "quang-ninh",
    "Bắc Ninh": "bac-ninh",
    "Hải Dương": "hai-duong",
    "Nam Định": "nam-dinh",
    "Vĩnh Phúc": "vinh-phuc",
    "Hưng Yên": "hung-yen",
    "Thái Bình": "thai-binh",
    "Bắc Giang": "bac-giang",
    "Phú Thọ": "phu-tho",
    "Thái Nguyên": "thai-nguyen",
    "Ninh Bình": "ninh-binh",
    "Lào Cai": "lao-cai",
    "Hà Nam": "ha-nam",
    "Hòa Bình": "hoa-binh",
    "Lạng Sơn": "lang-son",
    "Sơn La": "son-la",
    "Yên Bái": "yen-bai",
    "Hà Giang": "ha-giang",
    "Tuyên Quang": "tuyen-quang",
    "Cao Bằng": "cao-bang",
    "Điện Biên": "dien-bien",
    "Lai Châu": "lai-chau",
    "Bắc Kạn": "bac-kan",
    # Miền Trung
    "Đà Nẵng": "da-nang",
    "Thanh Hóa": "thanh-hoa",
    "Nghệ An": "nghe-an",
    "Khánh Hòa": "khanh-hoa",
    "Lâm Đồng": "lam-dong",
    "Bình Định": "binh-dinh",
    "Đắk Lắk": "dak-lak",
    "Quảng Nam": "quang-nam",
    "Thừa Thiên – Huế": "thua-thien-hue",
    "Bình Thuận": "binh-thuan",
    "Hà Tĩnh": "ha-tinh",
    "Quảng Ngãi": "quang-ngai",
    "Gia Lai": "gia-lai",
    "Quảng Bình": "quang-binh",
    "Quảng Trị": "quang-tri",
    "Phú Yên": "phu-yen",
    "Đắk Nông": "dak-nong",
    "Kon Tum": "kon-tum",
    "Ninh Thuận": "ninh-thuan",
    # Miền Nam
    "TP Hồ Chí Minh": "ho-chi-minh",
    "Bình Dương": "binh-duong",
    "Đồng Nai": "dong-nai",
    "Bà Rịa – Vũng Tàu": "ba-ria-vung-tau",
    "Long An": "long-an",
    "Cần Thơ": "can-tho",
    "Kiên Giang": "kien-giang",
    "An Giang": "an-giang",
    "Cà Mau": "ca-mau",
    "Tây Ninh": "tay-ninh",
    "Đồng Tháp": "dong-thap",
    "Bình Phước": "binh-phuoc",
    "Tiền Giang": "tien-giang",
    "Bến Tre": "ben-tre",
    "Vĩnh Long": "vinh-long",
    "Sóc Trăng": "soc-trang",
    "Trà Vinh": "tra-vinh",
    "Hậu Giang": "hau-giang",
    "Bạc Liêu": "bac-lieu"
}

province_name = st.selectbox("Chọn tỉnh/thành phố", list(provinces.keys()))
province_slug = provinces[province_name]
num_pages = st.slider("Số trang cần quét", 1, 30, 3)

@st.cache_data
def crawl_data(province_slug, num_pages):
    results = []
    for page in range(1, num_pages + 1):
        url = f"https://doanhnghiep.me/ho-kinh-doanh-{province_slug}?page={page}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                st.warning(f"Trang {page} trả về lỗi {response.status_code}")
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("div", class_="business-item")
            if not items:
                break
            for item in items:
                name = item.find("h2").text.strip()
                spans = item.find_all("span")
                mst, nguoidd, diachi = "", "", ""
                for span in spans:
                    text = span.text.strip()
                    if "Mã số thuế:" in text:
                        mst = text.replace("Mã số thuế:", "").strip()
                    elif "Người đại diện:" in text:
                        nguoidd = text.replace("Người đại diện:", "").strip()
                    else:
                        diachi = text.strip()
                results.append({
                    "Tên hộ kinh doanh": name,
                    "Mã số thuế": mst,
                    "Người đại diện": nguoidd,
                    "Địa chỉ": diachi
                })
            time.sleep(1)
        except Exception as e:
            st.error(f"Lỗi trang {page}: {e}")
            continue
    return pd.DataFrame(results)

if st.button("🔎 Tra cứu"):
    with st.spinner("Đang quét dữ liệu..."):
        df = crawl_data(province_slug, num_pages)
        if not df.empty:
            st.success(f"✅ Đã tải {len(df)} dòng dữ liệu từ {num_pages} trang.")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                label="⬇ Tải file Excel",
                data=df.to_excel(index=False, engine='openpyxl'),
                file_name=f"{province_slug}_ho_kinh_doanh.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠ Không tìm thấy dữ liệu.")
