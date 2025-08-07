import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

def scrape_masothue(pages=1):
    base_url = ("https://masothue.com/tra-cuu-ma-so-thue-theo-loai-hinh-doanh-nghiep/"
                "ho-kinh-doanh-ca-the-20?page=")
    results = []
    for page in range(1, pages + 1):
        url = base_url + str(page)
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        section = soup.find("div", class_="tax-listing")
        if not section:
            continue

        raw_text = section.get_text(separator="\n").strip()
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        i = 0
        while i < len(lines) - 3:
            name = lines[i]
            mst_line = lines[i+1]
            nguoidd_line = lines[i+2]
            diachi = lines[i+3]

            if mst_line.startswith("Mã số thuế:") and nguoidd_line.startswith("Người đại diện:"):
                mst = mst_line.replace("Mã số thuế:", "").strip()
                nguoidd = nguoidd_line.replace("Người đại diện:", "").strip()
                results.append({
                    "Tên hộ kinh doanh": name,
                    "Mã số thuế": mst,
                    "Người đại diện": nguoidd,
                    "Địa chỉ": diachi
                })
                i += 4
            else:
                i += 1
    return results

@st.cache_data
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='HoKD')
    return output.getvalue()

st.set_page_config(page_title="Tra cứu hộ KD cá thể", layout="wide")
st.title("📋 Tra cứu hộ kinh doanh cá thể từ masothue.com")
pages = st.slider("🔢 Chọn số trang muốn tải", min_value=1, max_value=10, value=3)

if st.button("🚀 Tải dữ liệu"):
    with st.spinner("Đang tải dữ liệu..."):
        data = scrape_masothue(pages)
        df = pd.DataFrame(data)
        if df.empty:
            st.warning("⚠️ Không lấy được dữ liệu. Có thể đang bị chặn hoặc đổi cấu trúc.")
        else:
            st.success(f"✅ Đã tải {len(df)} dòng từ {pages} trang.")
            st.dataframe(df, use_container_width=True)
            excel_data = convert_df_to_excel(df)
            st.download_button(
                label="📥 Tải về Excel",
                data=excel_data,
                file_name="ho_kinh_doanh.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
