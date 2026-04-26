import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── Cấu hình trang ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LoL Data Insights",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Space+Grotesk:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Background */
    .stApp {
        background: #0a0a0f;
        color: #f0f0f5;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111118;
        border-right: 1px solid rgba(108,99,255,0.2);
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1a1a24;
        border: 1px solid rgba(108,99,255,0.25);
        border-radius: 12px;
        padding: 1rem;
    }

    [data-testid="stMetricValue"] {
        color: #6c63ff !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #8888aa !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    [data-testid="stMetricDelta"] svg { display: none; }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Sora', sans-serif !important;
        color: #f0f0f5 !important;
    }

    /* Divider */
    hr { border-color: rgba(108,99,255,0.2) !important; }

    /* Info box */
    .stAlert {
        background: rgba(108,99,255,0.1) !important;
        border: 1px solid rgba(108,99,255,0.3) !important;
        border-radius: 10px !important;
        color: #f0f0f5 !important;
    }

    /* Selectbox & slider */
    .stSelectbox label, .stSlider label, .stRadio label {
        color: #8888aa !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #111118;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #8888aa;
        border-radius: 8px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: #6c63ff !important;
        color: #fff !important;
    }

    /* Dataframe */
    .stDataFrame { border: 1px solid rgba(108,99,255,0.2); border-radius: 10px; }

    /* Progress bar */
    .stProgress > div > div { background: #6c63ff !important; }
</style>
""", unsafe_allow_html=True)

# ─── Màu sắc ──────────────────────────────────────────────────────────────────
COLORS = {
    'win': '#00CC96',
    'loss': '#EF553B',
    'blue': '#4d9de0',
    'red': '#e15554',
    'accent': '#6c63ff',
    'bg': '#0a0a0f',
    'card': '#1a1a24',
    'text': '#f0f0f5',
    'muted': '#8888aa',
}

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(26,26,36,0.8)',
    font=dict(color='#f0f0f5', family='Space Grotesk'),
    title_font=dict(family='Sora', size=16, color='#f0f0f5'),
    xaxis=dict(gridcolor='rgba(108,99,255,0.1)', linecolor='rgba(108,99,255,0.2)'),
    yaxis=dict(gridcolor='rgba(108,99,255,0.1)', linecolor='rgba(108,99,255,0.2)'),
    legend=dict(bgcolor='rgba(26,26,36,0.8)', bordercolor='rgba(108,99,255,0.2)', borderwidth=1),
    margin=dict(t=50, b=30, l=20, r=20),
)

# ─── Dữ liệu ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data(n_matches=500):
    np.random.seed(42)
    champions = ['Jinx', 'Thresh', 'Ahri', 'Yasuo', 'Lux',
                 'Zed', 'Ezreal', 'Leona', 'Orianna', 'Lee Sin']
    lanes = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
    patches = ['14.8', '14.9', '14.10', '14.11']

    data = {
        'Gold_Diff_15m': np.random.normal(500, 2000, n_matches),
        'First_Blood': np.random.choice(['Blue', 'Red'], n_matches, p=[0.52, 0.48]),
        'First_Tower': np.random.choice(['Blue', 'Red'], n_matches, p=[0.55, 0.45]),
        'Dragons_Secured': np.random.randint(0, 5, n_matches),
        'Barons_Secured': np.random.randint(0, 3, n_matches),
        'Result': np.random.choice(['Win', 'Loss'], n_matches, p=[0.5, 0.5]),
        'Game_Duration': np.random.randint(18, 52, n_matches),
        'Kills': np.random.randint(5, 40, n_matches),
        'Deaths': np.random.randint(5, 35, n_matches),
        'Assists': np.random.randint(10, 60, n_matches),
        'Champion': np.random.choice(champions, n_matches),
        'Lane': np.random.choice(lanes, n_matches),
        'Patch': np.random.choice(patches, n_matches),
        'CS_Per_Min': np.round(np.random.normal(7.5, 1.5, n_matches), 1),
        'Vision_Score': np.random.randint(10, 80, n_matches),
        'Damage_Dealt': np.random.randint(15000, 85000, n_matches),
    }

    df = pd.DataFrame(data)
    df.loc[df['Gold_Diff_15m'] > 2000, 'Result'] = np.random.choice(
        ['Win', 'Loss'], len(df[df['Gold_Diff_15m'] > 2000]), p=[0.82, 0.18]
    )
    df.loc[df['Gold_Diff_15m'] < -2000, 'Result'] = np.random.choice(
        ['Win', 'Loss'], len(df[df['Gold_Diff_15m'] < -2000]), p=[0.15, 0.85]
    )
    df['KDA'] = np.round((df['Kills'] + df['Assists']) / df['Deaths'].clip(lower=1), 2)
    return df

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 LoL Analytics")
    st.markdown("---")

    st.markdown("### Bộ lọc dữ liệu")

    n_matches = st.slider("Số trận phân tích", 100, 1000, 500, step=50)
    df_full = get_data(n_matches)

    selected_patch = st.multiselect(
        "Patch version",
        options=sorted(df_full['Patch'].unique()),
        default=sorted(df_full['Patch'].unique())
    )

    selected_lanes = st.multiselect(
        "Lane",
        options=df_full['Lane'].unique(),
        default=list(df_full['Lane'].unique())
    )

    selected_result = st.radio("Kết quả", ["Tất cả", "Win", "Loss"], horizontal=True)

    st.markdown("---")
    st.markdown("### Thông tin")
    st.markdown("""
    <div style='color:#8888aa; font-size:0.8rem; line-height:1.8;'>
    📌 Dữ liệu mô phỏng 500 trận<br>
    🔧 Python · Streamlit · Plotly<br>
    📊 Data Analytics Project<br>
    🎓 HCMUE · CNTT
    </div>
    """, unsafe_allow_html=True)

# ─── Lọc dữ liệu ─────────────────────────────────────────────────────────────
df = df_full[
    (df_full['Patch'].isin(selected_patch)) &
    (df_full['Lane'].isin(selected_lanes))
].copy()

if selected_result != "Tất cả":
    df = df[df['Result'] == selected_result]

if df.empty:
    st.warning("Không có dữ liệu với bộ lọc hiện tại.")
    st.stop()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='font-family:Sora; font-size:2.2rem; letter-spacing:-1px; margin-bottom:0;'>
🎮 League of Legends — Match Analytics
</h1>
<p style='color:#8888aa; margin-top:4px; margin-bottom:1.5rem;'>
Phân tích dữ liệu trận đấu · Mô phỏng từ {} trận
</p>
""".format(len(df)), unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("Tổng trận", f"{len(df):,}")
with k2:
    wr = (df['Result'] == 'Win').mean()
    st.metric("Win Rate", f"{wr:.1%}", delta=f"{wr - 0.5:+.1%}")
with k3:
    avg_dur = df['Game_Duration'].mean()
    st.metric("Thời gian TB", f"{avg_dur:.1f} phút")
with k4:
    avg_kda = df['KDA'].mean()
    st.metric("KDA trung bình", f"{avg_kda:.2f}")
with k5:
    dragon_wr = df[df['Dragons_Secured'] >= 3]['Result'].eq('Win').mean() if len(df[df['Dragons_Secured'] >= 3]) > 0 else 0
    st.metric("Win Rate ≥3 Rồng", f"{dragon_wr:.1%}")

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "⚔️ Objectives", "🏆 Champion", "📋 Dữ liệu thô"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TỔNG QUAN
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(
            df, x="Gold_Diff_15m", color="Result",
            nbins=40,
            title="Chênh lệch vàng phút 15 vs Kết quả",
            color_discrete_map={'Win': COLORS['win'], 'Loss': COLORS['loss']},
            barmode='overlay', opacity=0.75,
            labels={'Gold_Diff_15m': 'Gold Difference @ 15min', 'count': 'Số trận'}
        )
        fig.update_layout(**PLOT_LAYOUT)
        fig.add_vline(x=0, line_dash="dash", line_color=COLORS['muted'], opacity=0.5)
        fig.add_vline(x=2000, line_dash="dot", line_color=COLORS['win'], opacity=0.5,
                      annotation_text="80% WR", annotation_font_color=COLORS['win'])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        dur_bins = pd.cut(df['Game_Duration'], bins=[0, 25, 30, 35, 40, 60],
                          labels=['<25p', '25-30p', '30-35p', '35-40p', '>40p'])
        dur_wr = df.groupby(dur_bins, observed=True)['Result'].apply(
            lambda x: (x == 'Win').mean() * 100
        ).reset_index()
        dur_wr.columns = ['Duration', 'WinRate']
        fig2 = px.bar(
            dur_wr, x='Duration', y='WinRate',
            title="Win Rate theo thời lượng trận đấu",
            color='WinRate',
            color_continuous_scale=[[0, COLORS['loss']], [0.5, '#f5c518'], [1, COLORS['win']]],
            labels={'WinRate': 'Win Rate (%)', 'Duration': 'Thời lượng'}
        )
        fig2.update_layout(**PLOT_LAYOUT)
        fig2.update_coloraxes(showscale=False)
        fig2.add_hline(y=50, line_dash="dash", line_color=COLORS['muted'], opacity=0.5,
                       annotation_text="50%")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        result_counts = df['Result'].value_counts().reset_index()
        fig3 = px.pie(
            result_counts, values='count', names='Result',
            title="Phân phối Thắng / Thua",
            color='Result',
            color_discrete_map={'Win': COLORS['win'], 'Loss': COLORS['loss']},
            hole=0.55
        )
        fig3.update_layout(**PLOT_LAYOUT)
        fig3.update_traces(textinfo='percent+label', textfont_size=13)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = px.scatter(
            df.sample(min(200, len(df))),
            x='Game_Duration', y='KDA',
            color='Result', size='Damage_Dealt',
            title="KDA vs Thời lượng trận đấu",
            color_discrete_map={'Win': COLORS['win'], 'Loss': COLORS['loss']},
            opacity=0.7,
            labels={'Game_Duration': 'Thời lượng (phút)', 'KDA': 'KDA'}
        )
        fig4.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

    st.info("💡 **Insight:** Đội dẫn trước >2000 vàng ở phút 15 có win rate ~80%. Trận dài >40 phút có xu hướng win rate thấp hơn do comeback potential tăng cao.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OBJECTIVES
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        fig = px.box(
            df, x="Result", y="Dragons_Secured",
            title="Số Rồng kiểm soát theo Kết quả",
            color="Result",
            color_discrete_map={'Win': COLORS['win'], 'Loss': COLORS['loss']},
            points='outliers'
        )
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        dragon_wr_data = df.groupby('Dragons_Secured')['Result'].apply(
            lambda x: (x == 'Win').mean() * 100
        ).reset_index()
        dragon_wr_data.columns = ['Dragons', 'WinRate']
        fig2 = px.line(
            dragon_wr_data, x='Dragons', y='WinRate',
            title="Win Rate theo số Rồng kiểm soát",
            markers=True,
            labels={'Dragons': 'Số Rồng', 'WinRate': 'Win Rate (%)'}
        )
        fig2.update_traces(line_color=COLORS['accent'], marker_color=COLORS['win'],
                           marker_size=10, line_width=3)
        fig2.update_layout(**PLOT_LAYOUT)
        fig2.add_hline(y=50, line_dash="dash", line_color=COLORS['muted'], opacity=0.5)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        fb_wr = df.groupby('First_Blood')['Result'].apply(
            lambda x: (x == 'Win').mean() * 100
        ).reset_index()
        fb_wr.columns = ['Side', 'WinRate']
        fig3 = px.bar(
            fb_wr, x='Side', y='WinRate',
            title="Win Rate theo đội lấy First Blood",
            color='Side',
            color_discrete_map={'Blue': COLORS['blue'], 'Red': COLORS['red']},
            labels={'WinRate': 'Win Rate (%)', 'Side': 'Đội'}
        )
        fig3.update_layout(**PLOT_LAYOUT)
        fig3.add_hline(y=50, line_dash="dash", line_color=COLORS['muted'], opacity=0.5)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        obj_matrix = df.groupby(['Dragons_Secured', 'Barons_Secured'])['Result'].apply(
            lambda x: (x == 'Win').mean() * 100
        ).reset_index()
        obj_matrix.columns = ['Dragons', 'Barons', 'WinRate']
        pivot = obj_matrix.pivot(index='Dragons', columns='Barons', values='WinRate').fillna(0)
        fig4 = px.imshow(
            pivot,
            title="Win Rate: Rồng × Baron",
            color_continuous_scale=[[0, COLORS['loss']], [0.5, '#f5c518'], [1, COLORS['win']]],
            labels=dict(x="Baron Secured", y="Dragons Secured", color="Win Rate %"),
            aspect='auto'
        )
        fig4.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)

    st.info("💡 **Insight:** First Blood tăng win rate thêm ~5-8%. Kiểm soát được 3+ rồng kết hợp 1+ baron gần như đảm bảo chiến thắng.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHAMPION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        champ_stats = df.groupby('Champion').agg(
            Games=('Result', 'count'),
            WinRate=('Result', lambda x: (x == 'Win').mean() * 100),
            AvgKDA=('KDA', 'mean'),
            AvgDamage=('Damage_Dealt', 'mean')
        ).reset_index().round(2)

        fig = px.scatter(
            champ_stats, x='WinRate', y='AvgKDA',
            size='Games', color='WinRate',
            text='Champion',
            title="Win Rate vs KDA theo Champion",
            color_continuous_scale=[[0, COLORS['loss']], [0.5, '#f5c518'], [1, COLORS['win']]],
            labels={'WinRate': 'Win Rate (%)', 'AvgKDA': 'KDA trung bình'}
        )
        fig.update_traces(textposition='top center', textfont_size=10)
        fig.update_layout(**PLOT_LAYOUT)
        fig.add_vline(x=50, line_dash="dash", line_color=COLORS['muted'], opacity=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        lane_wr = df.groupby('Lane')['Result'].apply(
            lambda x: (x == 'Win').mean() * 100
        ).reset_index()
        lane_wr.columns = ['Lane', 'WinRate']
        lane_wr = lane_wr.sort_values('WinRate', ascending=True)

        fig2 = px.bar(
            lane_wr, x='WinRate', y='Lane',
            orientation='h',
            title="Win Rate theo Lane",
            color='WinRate',
            color_continuous_scale=[[0, COLORS['loss']], [0.5, '#f5c518'], [1, COLORS['win']]],
            labels={'WinRate': 'Win Rate (%)', 'Lane': ''}
        )
        fig2.update_layout(**PLOT_LAYOUT)
        fig2.update_coloraxes(showscale=False)
        fig2.add_vline(x=50, line_dash="dash", line_color=COLORS['muted'], opacity=0.5)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📋 Bảng thống kê Champion")
    champ_display = champ_stats.sort_values('WinRate', ascending=False).copy()
    champ_display['WinRate'] = champ_display['WinRate'].apply(lambda x: f"{x:.1f}%")
    champ_display['AvgKDA'] = champ_display['AvgKDA'].apply(lambda x: f"{x:.2f}")
    champ_display['AvgDamage'] = champ_display['AvgDamage'].apply(lambda x: f"{x:,.0f}")
    champ_display.columns = ['Champion', 'Số trận', 'Win Rate', 'KDA TB', 'Damage TB']
    st.dataframe(champ_display, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Dữ liệu thô")
    col_filter, col_download = st.columns([3, 1])
    with col_filter:
        show_cols = st.multiselect(
            "Chọn cột hiển thị",
            options=df.columns.tolist(),
            default=['Champion', 'Lane', 'Result', 'Gold_Diff_15m',
                     'Dragons_Secured', 'KDA', 'Game_Duration', 'Patch']
        )
    with col_download:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Tải CSV",
            data=csv,
            file_name='lol_analytics_data.csv',
            mime='text/csv',
            use_container_width=True
        )

    if show_cols:
        st.dataframe(df[show_cols], use_container_width=True, height=400)

    st.markdown("#### Thống kê mô tả")
    st.dataframe(df[['Gold_Diff_15m', 'Dragons_Secured', 'KDA',
                      'Game_Duration', 'Damage_Dealt']].describe().round(2),
                 use_container_width=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#8888aa; font-size:0.82rem; padding:1rem 0;'>
🎮 LoL Analytics · Vũ Huy Minh · HCMUE CNTT · 2026 &nbsp;|&nbsp;
Built with Python · Streamlit · Plotly
</div>
""", unsafe_allow_html=True)
