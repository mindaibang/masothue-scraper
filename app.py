import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_masothue(pages=1):
    base_url = "https://masothue.com/tra-cuu-ma-so-thue-theo-loai-hinh-doanh-nghiep/ho-kinh-doanh-ca-the-20?page="
    results = []

    for page in range(1, pages + 1):
        url = base_url + str(page)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select(".tax-listing .media")

        for item in items:
            name = item.select_one("h3").get_text(strip=True)
            detail_lines = item.select("p")
            mst = ""
            nguoidd = ""
            diachi = ""
            for line in detail_lines:
                txt = line.get_text(strip=True)
                if txt.startswith("Mã số thuế:"):
                    mst = txt.replace("Mã số thuế:", "").strip()
                elif txt.startswith("Người đại diện:"):
                    nguoidd = txt.replace("Người đại diện:", "").strip()
                else:
                    diachi = txt.strip()

            results.append({
                "Tên hộ kinh doanh": name,
                "Mã số thuế": mst,
                "Người đại diện": nguoidd,
                "Địa chỉ": diachi
            })

    return results

# Giao diện Streamlit
st.set_page_config(page_title="Tra cứu hộ kinh doanh cá thể", layout="wide")
st.title("📋 Tra cứu hộ kinh doanh cá thể - masothue.com")

pages = st.slider("Chọn số trang cần lấy", min_value=1, max_value=10, value=3)

if st.button("Tải dữ liệu"):
    with st.spinner("Đang lấy dữ liệu..."):
        data = scrape_masothue(pages)
        df = pd.DataFrame(data)
        st.success(f"Đã tải {len(df)} dòng dữ liệu.")
        st.dataframe(df, use_container_width=True)

        @st.cache_data
        def convert_df(df):
            return df.to_excel(index=False, engine='openpyxl')

        excel_data = convert_df(df)

        st.download_button(
            label="📥 Tải về Excel",
            data=excel_data,
            file_name="ho_kinh_doanh.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
