import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Cấu hình giao diện
st.set_page_config(page_title="LoL Data Insights", layout="wide")

# Tạo dữ liệu mẫu chuyên nghiệp
def get_data():
    np.random.seed(42)
    n_matches = 500
    data = {
        'Gold_Diff_15m': np.random.normal(500, 2000, n_matches),
        'First_Blood': np.random.choice(['Blue', 'Red'], n_matches),
        'Dragons_Secured': np.random.randint(0, 5, n_matches),
        'Result': np.random.choice(['Win', 'Loss'], n_matches, p=[0.5, 0.5]),
        'Game_Duration': np.random.randint(20, 45, n_matches)
    }
    df = pd.DataFrame(data)
    # Điều chỉnh dữ liệu để hợp lý thực tế: Nếu Gold_Diff > 2000 thì tỉ lệ Win cao hơn
    df.loc[df['Gold_Diff_15m'] > 2000, 'Result'] = np.random.choice(['Win', 'Loss'], len(df[df['Gold_Diff_15m'] > 2000]), p=[0.8, 0.2])
    return df

df = get_data()

# Giao diện chính
st.title("🎮 League of Legends Match Analytics")
st.markdown("---")

# Hàng 1: Các chỉ số quan trọng (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tổng trận đấu phân tích", len(df))
with col2:
    win_rate = (df['Result'] == 'Win').mean()
    st.metric("Tỉ lệ thắng trung bình", f"{win_rate:.1%}")
with col3:
    avg_time = df['Game_Duration'].mean()
    st.metric("Thời gian trận đấu TB", f"{avg_time:.1f} phút")

st.markdown("### 📊 Phân tích chuyên sâu")

# Hàng 2: Biểu đồ
c1, c2 = st.columns(2)
with c1:
    fig_gold = px.histogram(df, x="Gold_Diff_15m", color="Result", 
                             title="Tương quan giữa Chênh lệch vàng (15p) và Kết quả",
                             color_discrete_map={'Win': '#00CC96', 'Loss': '#EF553B'})
    st.plotly_chart(fig_gold, use_container_width=True)

with c2:
    fig_drag = px.box(df, x="Result", y="Dragons_Secured", 
                       title="Số lượng Rồng kiểm soát theo Kết quả",
                       color="Result")
    st.plotly_chart(fig_drag, use_container_width=True)

st.info("💡 **Insight:** Dữ liệu cho thấy các đội dẫn trước trên 2000 vàng ở phút 15 có tỉ lệ thắng lên tới 80%.")
