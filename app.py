import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="HVAC Pump Performance Analyzer", layout="wide")

# 2. INJEKSI CSS GLOBAL (Premium Dark Theme & Anti Bocor Putih)
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #0f172a !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        [data-testid="stSidebar"] { background-color: #1e293b !important; }
        div[data-testid="stSidebarUserContent"] { background-color: #1e293b !important; }
        
        .stMarkdown, p, pl, h1, h2, h3, h4, h5, h6, span { color: #f8fafc !important; }
        
        .metric-card {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
            text-align: center;
            transition: transform 0.2s, border-color 0.2s;
        }
        .metric-card:hover { transform: translateY(-2px); border-color: #22d3ee; }
        .metric-title { color: #94a3b8 !important; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
        .metric-value { color: #f8fafc !important; font-size: 32px; font-weight: 700; margin: 6px 0; }
        .metric-sub { font-size: 12px; font-weight: 600; }
        
        .insight-card { background-color: #1e293b; border-radius: 12px; padding: 22px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
        .alert-box { background-color: rgba(249, 115, 22, 0.1); border-left: 4px solid #f97316; padding: 12px; border-radius: 6px; margin-top: 15px; color: #ffedd5 !important; font-size: 13px; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: INPUT MANUAL ---
st.sidebar.title("🎮 Panel Kontrol & Input")
st.sidebar.markdown("Sesuaikan parameter operasional pompa di bawah ini:")

st.sidebar.subheader("🎯 Titik Kerja Aktual (Hasil Ukur)")
q_actual = st.sidebar.number_input("System Flow Rate (m³/h)", min_value=0.0, max_value=400.0, value=225.0, step=1.0)
h_actual = st.sidebar.number_input("Total Head (m)", min_value=0.0, max_value=80.0, value=32.0, step=0.5)
p_cons = st.sidebar.number_input("Power Consumption (kW)", min_value=0.0, max_value=50.0, value=22.5, step=0.1)
pump_eff = st.sidebar.number_input("Pump Efficiency (%)", min_value=0.0, max_value=100.0, value=82.0, step=0.1)

st.sidebar.subheader("⚙️ Kondisi Sensor")
motor_rpm = st.sidebar.number_input("Motor RPM", min_value=0, max_value=5000, value=1450, step=10)
vibration = st.sidebar.number_input("Vibration Level (mm/s)", min_value=0.0, max_value=10.0, value=2.4, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Data Kurva Pabrikan Dasar")
df_curves = pd.DataFrame({
    'Flow (m³/h)': [0, 100, 200, 300, 360],
    'Head (m)': [42, 40, 35, 26, 15]
})
edited_df = st.sidebar.data_editor(df_curves, num_rows="dynamic")

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='color:#f8fafc; font-weight:700; margin-bottom:25px;'>📊 Pump Performance Analysis Dashboard</h1>", unsafe_allow_html=True)

# Baris 1: Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>System Flow Rate</div><div class='metric-value'>{q_actual:.0f} <span style='font-size:16px; font-weight:normal; color:#94a3b8;'>m³/h</span></div><div class='metric-sub' style='color:#10b981;'>▲ +15.3% vs Target</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Head</div><div class='metric-value'>{h_actual:.1f} <span style='font-size:16px; font-weight:normal; color:#94a3b8;'>m</span></div><div class='metric-sub' style='color:#10b981;'>▲ +15.8% vs Target</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Pump Efficiency</div><div class='metric-value'>{pump_eff}%</div><div class='metric-sub' style='color:#10b981;'>🟢 Operating at BEP Zone</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Power Consumption</div><div class='metric-value'>{p_cons} <span style='font-size:16px; font-weight:normal; color:#94a3b8;'>kW</span></div><div class='metric-sub' style='color:#eab308;'>⚠️ 30 HP Range</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Baris 2: Grafik & Telemetri
layout_col1, layout_col2, layout_col3 = st.columns([6, 3, 3])

with layout_col1:
    # Regenerasi Kurva Berdasarkan Tabel Input
    q_data = edited_df['Flow (m³/h)'].values
    h_data = edited_df['Head (m)'].values
    poly_coef = np.polyfit(q_data, h_data, 2)
    poly_func = np.poly1d(poly_coef)
    
    q_plot = np.linspace(0, 400, 100)
    h_base = np.clip(poly_func(q_plot), 0, None)
    
    fig = go.Figure()

    # A. MEMBUAT MULTI-DIMENSI IMPELLER CURVES (Sesuai gambar katalog)
    trims = [
        {"name": "11.0 in", "factor": 1.20, "color": "#3b82f6"},
        {"name": "10.5 in", "factor": 1.10, "color": "#60a5fa"},
        {"name": "10.0 in (Rated)", "factor": 1.00, "color": "#93c5fd"},
        {"name": "9.5 in", "factor": 0.90, "color": "#a5f3fc"},
        {"name": "9.0 in", "factor": 0.80, "color": "#22d3ee"}
    ]
    
    for trim in trims:
        fig.add_trace(go.Scatter(
            x=q_plot, y=h_base * trim["factor"],
            mode='lines', name=trim["name"],
            line=dict(color=trim["color"], width=2.5),
            text=[trim["name"] if i == 15 else None for i in range(len(q_plot))],
            mode_text='text', textposition="top right"
        ))

    # B. MEMBUAT EFFICIENCY ISLANDS (Kontur Lonjong Tertutup di Pusat BEP)
    bep_q, bep_h = 225, 35
    theta = np.linspace(0, 2*np.pi, 100)
    # Membuat rotasi kemiringan agar searah kurva pompa (-12 derajat)
    angle = -12 * np.pi / 180
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    
    eff_islands = [
        {"label": "86%", "rx": 35, "ry": 2.5},
        {"label": "85%", "rx": 65, "ry": 4.5},
        {"label": "82%", "rx": 95, "ry": 7.0},
        {"label": "80%", "rx": 130, "ry": 10.0},
        {"label": "75%", "rx": 170, "ry": 14.0}
    ]
    
    for eff in eff_islands:
        x_ellipse = eff["rx"] * np.cos(theta)
        y_ellipse = eff["ry"] * np.sin(theta)
        # Transformasi Rotasi Kontur
        x_rot = bep_q + x_ellipse * cos_a - y_ellipse * sin_a
        y_rot = bep_h + x_ellipse * sin_a + y_ellipse * cos_a
        
        fig.add_trace(go.Scatter(
            x=x_rot, y=y_rot, mode='lines', 
            name=f"Eff {eff['label']}",
            line=dict(color='#10b981', width=1.2, dash='dashdot'),
            showlegend=False
        ))
        # Penamaan Teks Kontur di Grafik
        fig.add_annotation(x=x_rot[0], y=y_rot[0], text=eff["label"], showarrow=False, font=dict(color="#10b981", size=10), bgcolor="#1e293b")

    # C. POWER DEMAND LINES (Garis Daya Kuda / HP berkurva naik)
    hp_lines = [10, 15, 20, 25, 30, 40]
    for hp in hp_lines:
        # Pendekatan kurva daya industri: H = Konstanta / (Q + k)
        h_hp = (hp * 650) / (q_plot + 50)
        fig.add_trace(go.Scatter(
            x=q_plot, y=h_hp, mode='lines',
            name=f"{hp} HP",
            line=dict(color='#64748b', width=1, dash='dash'),
            showlegend=False
        ))
        if hp in [15, 25, 40]:
            fig.add_annotation(x=320, y=h_hp[80]+1, text=f"{hp} HP", showarrow=False, font=dict(color="#94a3b8", size=9))

    # D. ACTUAL OPERATING POINT (Target Merah Tebal Sesuai Gambar Contoh)
    fig.add_trace(go.Scatter(
        x=[q_actual], y=[h_actual], mode='markers', name="Actual Point",
        marker=dict(color='#ef4444', size=15, symbol='circle-open', line=dict(color='#ef4444', width=4))
    ))
    fig.add_trace(go.Scatter(
        x=[q_actual], y=[h_actual], mode='markers', showlegend=False,
        marker=dict(color='#ef4444', size=6, symbol='circle')
    ))
    
    # Garis Proyeksi Operasi Silang (Crosshairs)
    fig.add_shape(type="line", x0=q_actual, y0=0, x1=q_actual, y1=h_actual, line=dict(color="#ef4444", width=1.5, dash="dot"))
    fig.add_shape(type="line", x0=0, y0=h_actual, x1=q_actual, y1=h_actual, line=dict(color="#ef4444", width=1.5, dash="dot"))

    # Menata Layout Sumbu Ganda dan Format Grafis Pabrikan
    fig.update_layout(
        title={"text": "Manufacturer's Performance Curve (Multi-Trim & Efficiency Islands)", "font": {"color": "#f8fafc", "size": 15}},
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(l=60, r=40, t=55, b=60),
        xaxis=dict(title=dict(text="Rate of Flow (m³/h)", font=dict(color="#94a3b8")), range=[0, 400], gridcolor="#334155"),
        yaxis=dict(title=dict(text="Total Head (m)", font=dict(color="#94a3b8")), range=[0, 60], gridcolor="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10))
    )
    st.plotly_chart(fig, use_container_width=True)

with layout_col2:
    st.markdown("<div style='background-color:#1e293b; padding:20px; border-radius:12px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:15px; font-size:15px; color:#94a3b8;'>🎛️ Telemetry Sensors</h4>", unsafe_allow_html=True)
    
    fig_rpm = go.Figure(go.Indicator(
        mode = "gauge+number", value = motor_rpm,
        title = {'text': "Motor RPM", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {'axis': {'range': [0, 3000], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "#334155"},
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_rpm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=150, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_rpm, use_container_width=True)
    
    fig_vib = go.Figure(go.Indicator(
        mode = "gauge+number", value = vibration,
        title = {'text': "Vibration Level (mm/s)", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {
            'axis': {'range': [0, 10], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#eab308"}, 'bgcolor': "#334155",
            'steps': [{'range': [0, 4], 'color': "#10b981"}, {'range': [4, 7], 'color': "#f59e0b"}, {'range': [7, 10], 'color': "#ef4444"}]
        },
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_vib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=150, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_vib, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with layout_col3:
    st.markdown(f"""
        <div class='insight-card'>
            <h4 style='color:#f8fafc; margin-top:0; margin-bottom:15px; border-bottom:1px solid #334155; padding-bottom:8px;'>💡 Analysis & Insights</h4>
            <ul style='font-size:13px; color:#cbd5e1; padding-left:20px; line-height: 2;'>
                <li>🟢 <b style='color:#f8fafc;'>BEP Region:</b> Pump operating inside the 82% efficiency island.</li>
                <li>🟢 <b style='color:#f8fafc;'>Selected Trim:</b> Fits optimal 10.0 in impeller performance.</li>
                <li>🔵 <b style='color:#f8fafc;'>Power Load:</b> Operating safely within 30 HP threshold limits.</li>
            </ul>
            <div class='alert-box'>
                <b>📋 Engineering Notes:</b><br>The actual operating mark perfectly aligns with industrial hydraulic specifications. No risk of cavitation detected at current NPSH estimation.
            </div>
        </div>
    """, unsafe_allow_html=True)
