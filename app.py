# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.title("Tra cứu danh sách Hộ Kinh Doanh Cá Thể (masothue.com)")
num_pages = st.number_input("Số trang cần quét", min_value=1, max_value=50, value=3)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def crawl_masothue(page_num):
    url = f"https://masothue.com/tra-cuu-ma-so-thue-ca-nhan?page={page_num}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for item in soup.select("div.tax-search-listing div.media-body"):
        name_tag = item.select_one("h3")
        info_tags = item.select("p")
        if len(info_tags) >= 3:
            ten_hkd = name_tag.text.strip() if name_tag else ""
            mst = info_tags[0].text.replace("Mã số thuế:", "").strip()
            dai_dien = info_tags[1].text.replace("Người đại diện:", "").strip()
            dia_chi = info_tags[2].text.strip()
            results.append({
                "Tên hộ kinh doanh": ten_hkd,
                "Mã số thuế": mst,
                "Người đại diện": dai_dien,
                "Địa chỉ": dia_chi
            })
    return results

data = []
with st.spinner("Đang tải dữ liệu..."):
    for i in range(1, num_pages + 1):
        st.write(f"🔍 Đang quét trang {i}...")
        try:
            data.extend(crawl_masothue(i))
            time.sleep(2)
        except Exception as e:
            st.error(f"Lỗi ở trang {i}: {e}")
            break

if data:
    df = pd.DataFrame(data)
    st.success(f"✅ Đã tải {len(df)} dòng dữ liệu từ {num_pages} trang.")
    st.dataframe(df)

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)
    st.download_button("📥 Tải file CSV", csv, "hkd_data.csv", "text/csv")
else:
    st.warning("⚠ Không lấy được dữ liệu. Có thể trang đang chặn hoặc đổi cấu trúc.")
