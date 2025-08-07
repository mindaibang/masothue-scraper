import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# -----------------------------
# Hàm lấy dữ liệu từ masothue.com theo HTML mới
# -----------------------------
def scrape_masothue(pages=1):
    base_url = ("https://masothue.com/tra-cuu-ma-so-thue-theo-loai-hinh-doanh-nghiep/"
                "ho-kinh-doanh-ca-the-20?page=")
    results = []

    for page in range(1, pages + 1):
        url = base_url + str(page)
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            # Mỗi hộ KD hiển thị trong thẻ <div data-prefetch>
            listings = soup.select("div.tax-listing > div[data-prefetch]")

            for listing in listings:
                # Tên hộ KD
                name_tag = listing.select_one("h3 > a")
                name = name_tag.get_text(strip=True) if name_tag else ""

                # Địa chỉ
                address_tag = listing.select_one("address")
                address = address_tag.get_text(strip=True) if address_tag else ""

                # Mã số thuế & Người đại diện
                divs = listing.find_all("div")
                mst = ""
                nguoidd = ""
                for div in divs:
                    txt = div.get_text(strip=True)
                    if "Mã số thuế:" in txt:
                        mst = txt.replace("Mã số thuế:", "").strip()
                    elif "Người đại diện:" in txt:
                        nguoidd = txt.replace("Người đại diện:", "").strip()

                results.append({
                    "Tên hộ kinh doanh": name,
                    "Mã số thuế": mst,
                    "Người đại diện": nguoidd,
                    "Địa chỉ": address
                })

        except Exception as e:
            st.error(f"Lỗi khi tải trang {page}: {e}")

    return results

# -----------------------------
# Chuyển DataFrame thành file Excel (RAM)
# -----------------------------
@st.cache_data
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='HoKD')
    return output.getvalue()

# -----------------------------
# Giao diện chính
# -----------------------------
st.set_page_config(page_title="Tra cứu hộ KD cá thể", layout="wide")
st.title("📋 Tra cứu hộ kinh doanh cá thể từ masothue.com")

pages = st.slider("🔢 Chọn số trang muốn tải", min_value=1, max_value=10, value=3)

if st.button("🚀 Tải dữ liệu"):
    with st.spinner("Đang tải dữ liệu..."):
        data = scrape_masothue(pages)
        df = pd.DataFrame(data)

        if df.empty:
            st.warning("⚠️ Không lấy được dữ liệu. Có thể đang bị chặn hoặc cấu trúc web thay đổi.")
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
