import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. KONFIGURASI HALAMAN & TEMA DARK MODE VIA CSS
st.set_page_config(page_title="HVAC Pump Performance Analyzer", layout="wide")

st.markdown("""
    <style>
        /* Mengubah background utama menjadi gelap ala dashboard */
        .main { background-color: #0f172a; color: #f8fafc; }
        div[data-testid="stSidebarUserContent"] { background-color: #1e293b; }
        
        /* Gaya kartu (Card) untuk Metrik */
        .metric-card {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            border: 1px solid #334155;
            text-align: center;
        }
        .metric-title { color: #94a3b8; font-size: 14px; font-weight: 500; margin-bottom: 5px; }
        .metric-value { color: #f8fafc; font-size: 28px; font-weight: 700; }
        .metric-sub { color: #10b981; font-size: 12px; margin-top: 5px; }
        
        /* Gaya Panel Samping (Insights & Alerts) */
        .insight-card {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #334155;
            height: 100%;
        }
        .alert-box {
            background-color: #451a03;
            border-left: 4px solid #f97316;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            color: #fed7aa;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True) # Perbaikan di sini

# --- SIDEBAR: FUNGSI INPUT DATA ---
st.sidebar.title("🎮 Panel Kontrol & Input")
st.sidebar.markdown("Sesuaikan parameter operasional pompa di bawah ini:")

st.sidebar.subheader("🎯 Titik Kerja Aktual (Hasil Ukur)")
q_actual = st.sidebar.slider("System Flow Rate (m³/h)", min_value=0.0, max_value=400.0, value=246.0, step=1.0)
h_actual = st.sidebar.slider("Total Head (m)", min_value=0.0, max_value=80.0, value=34.0, step=0.5)
p_cons = st.sidebar.slider("Power Consumption (kW)", min_value=0.0, max_value=15.0, value=3.7, step=0.1)
pump_eff = st.sidebar.slider("Pump Efficiency (%)", min_value=0.0, max_value=100.0, value=87.3, step=0.1)

st.sidebar.subheader("⚙️ Kondisi Sensor")
motor_rpm = st.sidebar.number_input("Motor RPM", value=1450, step=10)
vibration = st.sidebar.slider("Vibration Level (mm/s)", min_value=0.0, max_value=10.0, value=2.4, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Data Kurva Pabrikan (Edit Tabel)")
df_curves = pd.DataFrame({
    'Flow (m³/h)': [0, 100, 200, 300, 360],
    'Head (m)': [70, 65, 56, 38, 20]
})
edited_df = st.sidebar.data_editor(df_curves, num_rows="dynamic")

# --- MAIN DASHBOARD INTERFACE ---
# Header Utama
st.markdown("<h2 style='color:#f8fafc; margin-bottom:20px;'>📊 Pump Performance Analysis</h2>", unsafe_allow_html=True) # Perbaikan di sini

# Baris 1: 4 buah Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>System Flow Rate (m³/h)</div><div class='metric-value'>{q_actual}</div><div class='metric-sub'>▲ +15.3% vs Target</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Head (m)</div><div class='metric-value'>{h_actual:.1f}</div><div class='metric-sub'>▲ +15.8% vs Target</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Pump Efficiency (%)</div><div class='metric-value'>{pump_eff}%</div><div class='metric-sub' style='color:#ef4444;'>▼ -15.6% vs BEP</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Power Consumption (kW)</div><div class='metric-value'>{p_cons} kW</div><div class='metric-sub' style='color:#ef4444;'>▼ -15.8% Overload</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # Perbaikan di sini

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
    
    # Membuat Sistem Kurva Parabola (System Curve)
    h_system = 0.0005 * (q_plot**2)
    
    # Plotly Graph
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=q_plot, y=h_plot, mode='lines', name="Manufacturer's Curve", line=dict(color='#1f77b4', width=3)))
    fig.add_trace(go.Scatter(x=q_plot, y=h_system, mode='lines', name="System Curve", line=dict(color='#64748b', width=2)))
    fig.add_trace(go.Scatter(x=[q_actual], y=[h_actual], mode='markers', name="Actual Operating Point", marker=dict(color='#22d3ee', size=14, symbol='star')))
    
    fig.add_shape(type="line", x0=q_actual, y0=0, x1=q_actual, y1=h_actual, line=dict(color="#22d3ee", width=1.5, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=h_actual, x1=q_actual, y1=h_actual, line=dict(color="#22d3ee", width=1.5, dash="dash"))

    fig.update_layout(
        title="Professional Pump Curve",
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(title="Flow (m³/h)", range=[0, 400], gridcolor="#334155"),
        yaxis=dict(title="Head (m)", range=[0, 80], gridcolor="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with layout_col2:
    st.markdown("<div style='background-color:#1e293b; padding:15px; border-radius:10px; border: 1px solid #334155;'>", unsafe_allow_html=True) # Perbaikan di sini
    
    # Gauge 1: Motor RPM
    fig_rpm = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = motor_rpm,
        title = {'text': "Motor RPM", 'font': {'size': 14, 'color': '#94a3b8'}},
        gauge = {'axis': {'range': [0, 3000]}, 'bar': {'color': "#3b82f6"}},
        number = {'font': {'color': '#f8fafc', 'size': 20}}
    ))
    fig_rpm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=140, margin=dict(l=20, r=20, t=30, b=10))
    st.plotly_chart(fig_rpm, use_container_width=True)
    
    # Gauge 2: Vibration Level
    fig_vib = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = vibration,
        title = {'text': "Vibration Level (mm/s)", 'font': {'size': 14, 'color': '#94a3b8'}},
        gauge = {
            'axis': {'range': [0, 10]},
            'bar': {'color': "#eab308"},
            'steps': [
                {'range': [0, 4], 'color': "green"},
                {'range': [4, 7], 'color': "yellow"},
                {'range': [7, 10], 'color': "red"}]
        },
        number = {'font': {'color': '#f8fafc', 'size': 20}}
    ))
    fig_vib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=140, margin=dict(l=20, r=20, t=30, b=10))
    st.plotly_chart(fig_vib, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True) # Perbaikan di sini

with layout_col3:
    st.markdown(f"""
        <div class='insight-card'>
            <h4 style='color:#f8fafc; margin-top:0;'>Analysis & Insights</h4>
            <ul style='font-size:13px; color:#cbd5e1; padding-left:20px;'>
                <li>🟢 <b>BEP Deviation:</b> 3% (Good Condition)</li>
                <li>🟢 <b>Impeller Wear Risk:</b> Low Risk</li>
                <li>🔵 <b>Potential Savings:</b> 12% via VFD Optimization</li>
            </ul>
            <div class='alert-box'>
                <b>⚠️ Alerts:</b><br>Centrifugal Pump parameters indicate stable flow, but watch out for micro-vibration trends.
            </div>
            <br>
            <h4 style='color:#f8fafc;'>Recommendations</h4>
            <p style='font-size:12px; color:#cbd5e1;'>Maintain current VFD scheduling window to capture maximum savings of 12% during off-peak HVAC loads.</p>
        </div>
    """, unsafe_allow_html=True) # Perbaikan di sini
