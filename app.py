import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. KONFIGURASI HALAMAN (Wajib di baris pertama setelah import)
st.set_page_config(page_title="HVAC Pump Performance Analyzer", layout="wide")

# 2. INJEKSI CSS GLOBAL (Mengunci Dark Mode Total & Menghilangkan Bocor Putih)
st.markdown("""
    <style>
        /* Memaksa seluruh canvas luar, header, dan sidebar menjadi Gelap */
        [data-testid="stAppViewContainer"] {
            background-color: #0f172a !important;
        }
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        [data-testid="stSidebar"] {
            background-color: #1e293b !important;
        }
        div[data-testid="stSidebarUserContent"] {
            background-color: #1e293b !important;
        }
        
        /* Memperbaiki warna font default aplikasi agar kontras */
        .stMarkdown, p, pl, h1, h2, h3, h4, h5, h6, span {
            color: #f8fafc !important;
        }
        
        /* Gaya Kartu Metrik (Metric Card) Premium */
        .metric-card {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
            text-align: center;
            transition: transform 0.2s, border-color 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #22d3ee;
        }
        .metric-title { 
            color: #94a3b8 !important; 
            font-size: 12px; 
            font-weight: 600; 
            text-transform: uppercase; 
            letter-spacing: 0.05em; 
        }
        .metric-value { 
            color: #f8fafc !important; 
            font-size: 32px; 
            font-weight: 700; 
            margin: 6px 0; 
        }
        .metric-sub { 
            font-size: 12px; 
            font-weight: 600; 
        }
        
        /* Gaya Panel Samping (Insights & Alerts) */
        .insight-card {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 22px;
            border: 1px solid #334155;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }
        .alert-box {
            background-color: rgba(249, 115, 22, 0.1);
            border-left: 4px solid #f97316;
            padding: 12px;
            border-radius: 6px;
            margin-top: 15px;
            color: #ffedd5 !important;
            font-size: 13px;
            line-height: 1.5;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: FUNGSI INPUT DATA (Perubahan: Menggunakan Ketik Manual) ---
st.sidebar.title("🎮 Panel Kontrol & Input")
st.sidebar.markdown("Sesuaikan parameter operasional pompa di bawah ini:")

st.sidebar.subheader("🎯 Titik Kerja Aktual (Hasil Ukur)")
# Mengubah slider menjadi number_input agar bisa diketik langsung secara manual
q_actual = st.sidebar.number_input("System Flow Rate (m³/h)", min_value=0.0, max_value=400.0, value=246.0, step=1.0)
h_actual = st.sidebar.number_input("Total Head (m)", min_value=0.0, max_value=80.0, value=34.0, step=0.5)
p_cons = st.sidebar.number_input("Power Consumption (kW)", min_value=0.0, max_value=15.0, value=3.7, step=0.1)
pump_eff = st.sidebar.number_input("Pump Efficiency (%)", min_value=0.0, max_value=100.0, value=87.3, step=0.1)

st.sidebar.subheader("⚙️ Kondisi Sensor")
motor_rpm = st.sidebar.number_input("Motor RPM", min_value=0, max_value=5000, value=1450, step=10)
vibration = st.sidebar.number_input("Vibration Level (mm/s)", min_value=0.0, max_value=10.0, value=2.4, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Data Kurva Pabrikan (Edit Tabel)")
df_curves = pd.DataFrame({
    'Flow (m³/h)': [0, 100, 200, 300, 360],
    'Head (m)': [70, 65, 56, 38, 20]
})
edited_df = st.sidebar.data_editor(df_curves, num_rows="dynamic")

# --- MAIN DASHBOARD INTERFACE ---
st.markdown("<h1 style='color:#f8fafc; font-weight:700; margin-bottom:25px;'>📊 Pump Performance Analysis Dashboard</h1>", unsafe_allow_html=True)

# Baris 1: 4 buah Metric Cards Premium
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>System Flow Rate</div><div class='metric-value'>{q_actual:.0f} <span style='font-size:16px; font-weight:normal; color:#94a3b8;'>m³/h</span></div><div class='metric-sub' style='color:#10b981;'>▲ +15.3% vs Target</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Head</div><div class='metric-value'>{h_actual:.1f} <span style='font-size:16px; font-weight:normal; color:#94a3b8;'>m</span></div><div class='metric-sub' style='color:#10b981;'>▲ +15.8% vs Target</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Pump Efficiency</div><div class='metric-value'>{pump_eff}%</div><div class='metric-sub' style='color:#ef4444;'>▼ -15.6% vs BEP</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Power Consumption</div><div class='metric-value'>{p_cons} <span style='font-size:16px; font-weight:normal; color:#94a3b8;'>kW</span></div><div class='metric-sub' style='color:#ef4444;'>⚠️ Overload Risk</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Baris 2: Grafik Utama & Gauge & Insights
layout_col1, layout_col2, layout_col3 = st.columns([5, 3, 3])

with layout_col1:
    # Perhitungan matematika kurva
    q_data = edited_df['Flow (m³/h)'].values
    h_data = edited_df['Head (m)'].values
    poly_coef = np.polyfit(q_data, h_data, 2)
    poly_func = np.poly1d(poly_coef)
    
    q_plot = np.linspace(0, 400, 100)
    h_plot = np.clip(poly_func(q_plot), 0, None)
    h_system = 0.0005 * (q_plot**2)
    
    # Plotly Graph (Professional Pump Curve)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=q_plot, y=h_plot, mode='lines', name="Manufacturer's Curve", line=dict(color='#3b82f6', width=3)))
    fig.add_trace(go.Scatter(x=q_plot, y=h_system, mode='lines', name="System Curve", line=dict(color='#64748b', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=[q_actual], y=[h_actual], mode='markers', name="Actual Operating Point", marker=dict(color='#22d3ee', size=14, symbol='star', line=dict(color='white', width=1.5))))
    
    # Garis Proyeksi Neon
    fig.add_shape(type="line", x0=q_actual, y0=0, x1=q_actual, y1=h_actual, line=dict(color="#22d3ee", width=1.5, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=h_actual, x1=q_actual, y1=h_actual, line=dict(color="#22d3ee", width=1.5, dash="dash"))

    # PERBAIKAN VALUEERROR: Menata ulang title font agar didukung penuh oleh Plotly terbaru
    fig.update_layout(
        title={"text": "Professional Pump Curve", "font": {"color": "#f8fafc", "size": 16}},
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(l=50, r=30, t=50, b=50),
        xaxis=dict(
            title=dict(text="Flow (m³/h)", font=dict(color="#94a3b8")),
            range=[0, 400], 
            gridcolor="#334155"
        ),
        yaxis=dict(
            title=dict(text="Head (m)", font=dict(color="#94a3b8")),
            range=[0, 80], 
            gridcolor="#334155"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11))
    )
    st.plotly_chart(fig, use_container_width=True)

with layout_col2:
    st.markdown("<div style='background-color:#1e293b; padding:20px; border-radius:12px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:15px; font-size:15px; color:#94a3b8;'>🎛️ Telemetry Sensors</h4>", unsafe_allow_html=True)
    
    # Gauge 1: Motor RPM
    fig_rpm = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = motor_rpm,
        title = {'text': "Motor RPM", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {'axis': {'range': [0, 3000], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "#334155"},
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_rpm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=150, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_rpm, use_container_width=True)
    
    # Gauge 2: Vibration Level
    fig_vib = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = vibration,
        title = {'text': "Vibration Level (mm/s)", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {
            'axis': {'range': [0, 10], 'tickcolor': "#94a3b8"},
            'bar': {'color': "#eab308"},
            'bgcolor': "#334155",
            'steps': [
                {'range': [0, 4], 'color': "#10b981"},
                {'range': [4, 7], 'color': "#f59e0b"},
                {'range': [7, 10], 'color': "#ef4444"}]
        },
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_vib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=150, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_vib, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with layout_col3:
    # Panel Samping Kanan: Analysis & Insights
    st.markdown(f"""
        <div class='insight-card'>
            <h4 style='color:#f8fafc; margin-top:0; margin-bottom:15px; border-bottom:1px solid #334155; padding-bottom:8px;'>💡 Analysis & Insights</h4>
            <ul style='font-size:13px; color:#cbd5e1; padding-left:20px; line-height: 2;'>
                <li>🟢 <b style='color:#f8fafc;'>BEP Deviation:</b> 3% (Good Condition)</li>
                <li>🟢 <b style='color:#f8fafc;'>Impeller Wear Risk:</b> Low Risk</li>
                <li>🔵 <b style='color:#f8fafc;'>Potential Savings:</b> 12% via VFD Optimization</li>
            </ul>
            <div class='alert-box'>
                <b>⚠️ Alerts:</b><br>Centrifugal Pump parameters indicate stable flow, but watch out for micro-vibration trends.
            </div>
            <br>
            <h4 style='color:#f8fafc; margin-top:10px; margin-bottom:10px;'>📋 Recommendations</h4>
            <p style='font-size:13px; color:#cbd5e1; line-height:1.5;'>Maintain current VFD scheduling window to capture maximum savings of 12% during off-peak HVAC loads.</p>
        </div>
    """, unsafe_allow_html=True)
