import streamlit as st
import numpy as npimport streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Centrifugal Pump Performance Curve - HVAC T3", layout="wide")

# 2. INJEKSI CSS GLOBAL
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
        .metric-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
        .metric-title { color: #94a3b8 !important; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
        .metric-value { color: #f8fafc !important; font-size: 30px; font-weight: 700; margin: 6px 0; }
        .metric-sub { font-size: 12px; font-weight: 600; }
        
        .insight-card { background-color: #1e293b; border-radius: 12px; padding: 22px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
        .alert-box { background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 12px; border-radius: 6px; margin-top: 15px; color: #d9f99d !important; font-size: 13px; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: INPUT PARAMETER ---
st.sidebar.title("🎮 Panel Kontrol & Input")
st.sidebar.subheader("🎯 Titik Kerja Aktual (GPM - FT)")
q_actual = st.sidebar.number_input("Capacity (GPM)", min_value=10.0, max_value=20000.0, value=8000.0, step=100.0)
h_actual = st.sidebar.number_input("Total Head (FT)", min_value=10.0, max_value=1000.0, value=260.0, step=5.0)
p_cons = st.sidebar.number_input("Brake Horsepower (BHP)", min_value=10.0, max_value=5000.0, value=510.0, step=10.0)
pump_eff = st.sidebar.number_input("Pump Efficiency (%)", min_value=5.0, max_value=100.0, value=80.0, step=1.0)

st.sidebar.subheader("⚙️ Kondisi Sensor")
motor_rpm = st.sidebar.number_input("Motor RPM", min_value=0, max_value=5000, value=1450, step=10)
vibration = st.sidebar.number_input("Vibration Level (mm/s)", min_value=0.0, max_value=10.0, value=1.8, step=0.1)

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='color:#f8fafc; font-weight:700; margin-bottom:25px;'>📊 Centrifugal Pump Performance Analyzer - HVAC T3</h1>", unsafe_allow_html=True)

# Baris 1: Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Pump Capacity</div><div class='metric-value'>{q_actual:.0f} <span style='font-size:14px; font-weight:normal; color:#94a3b8;'>GPM</span></div><div class='metric-sub' style='color:#10b981;'>🟢 Target Operating Point</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Head</div><div class='metric-value'>{h_actual:.0f} <span style='font-size:14px; font-weight:normal; color:#94a3b8;'>FT</span></div><div class='metric-sub' style='color:#10b981;'>🟢 Design Balanced</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Efficiency (η)</div><div class='metric-value'>{pump_eff}%</div><div class='metric-sub' style='color:#10b981;'>🎯 At Peak BEP Zone</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Brake Power</div><div class='metric-value'>{p_cons:.0f} <span style='font-size:14px; font-weight:normal; color:#94a3b8;'>BHP</span></div><div class='metric-sub' style='color:#60a5fa;'>⚡ Motor Load Nominal</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Baris 2: Layout Grafik & Analisis Telemetri
layout_col1, layout_col2 = st.columns([8, 4])

with layout_col1:
    # --- FORMULA MATEMATIKA KURVA DINAMIS ---
    q_ref = max(1.0, q_actual)
    h_ref = max(1.0, h_actual)
    eff_ref = max(5.0, pump_eff)
    p_ref = max(1.0, p_cons)

    # 1. Rentang Kapasitas Sumbu X Dinamis
    q_max_plot = q_ref * 1.4
    q_plot = np.linspace(0, q_max_plot, 100)

    # 2. Kurva Q-H Dinamis
    h_shutoff = 1.35 * h_ref
    a_coeff = (0.35 * h_ref) / (q_ref ** 2)
    h_plot = h_shutoff - (a_coeff * (q_plot ** 2))
    h_plot = np.clip(h_plot, 0, None)

    # 3. Kurva Efisiensi Dinamis
    b_coeff = (eff_ref - 10) / (q_ref ** 2)
    eff_plot = eff_ref - b_coeff * (q_plot - q_ref) ** 2
    eff_plot = np.clip(eff_plot, 0, 100)

    # 4. Kurva BHP Dinamis
    bhp_plot = p_ref * (0.4 + 0.7 * (q_plot / q_ref) - 0.1 * (q_plot / q_ref) ** 2)
    bhp_plot = np.clip(bhp_plot, 0, None)

    # 5. Kurva NPSHr Dinamis
    npsh_plot = 4 + 12 * (q_plot / q_ref) ** 1.5

    # --- RENDERING PLOTLY ---
    fig = go.Figure()

    # Trace 1: Q-H Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=h_plot, mode='lines', name='Q-H CURVE',
        line=dict(color='black', width=3.5), yaxis='y1'
    ))
    
    # Trace 2: Efficiency Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=eff_plot, mode='lines', name='EFFICIENCY (η) CURVE',
        line=dict(color='#16a34a', width=3), yaxis='y2'
    ))
    
    # Trace 3: BHP Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=bhp_plot, mode='lines', name='BHP CURVE',
        line=dict(color='#dc2626', width=3), yaxis='y3'
    ))
    
    # Trace 4: NPSHr Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=npsh_plot, mode='lines', name='NPSHr CURVE',
        line=dict(color='#ea580c', width=2.5), yaxis='y1'
    ))

    # Titik Kerja Aktual (Duty Point)
    fig.add_trace(go.Scatter(
        x=[q_actual], y=[h_actual], mode='markers', name='DUTY POINT',
        marker=dict(symbol='x', size=18, line=dict(width=4), color='#1d4ed8'),
        yaxis='y1', showlegend=False
    ))

    # Garis Silang Proyeksi Desain
    fig.add_shape(type="line", x0=q_actual, y0=0, x1=q_actual, y1=h_shutoff * 1.05, line=dict(color="#1d4ed8", width=2, dash="dash"), yref="y1")
    fig.add_shape(type="line", x0=0, y0=h_actual, x1=q_actual, y1=h_actual, line=dict(color="#1d4ed8", width=2, dash="dash"), yref="y1")

    # Anotasi Teks Grafik Dinamis
    fig.add_annotation(
        x=q_actual + (q_max_plot * 0.02), y=h_actual + (h_shutoff * 0.04), 
        text=f"DUTY POINT:<br>{q_actual:.0f} GPM @ {h_actual:.0f} FT HEAD",
        showarrow=False, font=dict(color="#1d4ed8", size=11, family="Arial"), align="left"
    )

    # Konfigurasi Layout Multi-Sumbu
    fig.update_layout(
        title={"text": "LIVE DYNAMIC CENTRIFUGAL PUMP PERFORMANCE CURVE", "font": {"color": "#000000", "size": 13}},
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=70, r=130, t=60, b=65),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="black")),
        
        xaxis=dict(
            title=dict(text="CAPACITY IN GALLONS PER MINUTE (GPM)", font=dict(color="black", size=11)),
            range=[0, q_max_plot], gridcolor="#e2e8f0", linecolor="black", linewidth=2, ticks="outside",
            domain=[0, 0.80]
        ),
        yaxis=dict(
            title=dict(text="HEAD IN FEET (FT)", font=dict(color="black", size=11)),
            range=[0, h_shutoff * 1.08], gridcolor="#e2e8f0", linecolor="black", linewidth=2, ticks="outside"
        ),
        yaxis2=dict(
            title=dict(text="EFFICIENCY % (η)", font=dict(color="#16a34a", size=11)),
            range=[0, 110], side="right", overlaying="y", ticks="outside",
            linecolor="#16a34a", linewidth=2, showgrid=False
        ),
        yaxis3=dict(
            title=dict(text="BRAKE HORSEPOWER (BHP)", font=dict(color="#dc2626", size=11)),
            range=[0, p_ref * 1.4], side="right", overlaying="y", ticks="outside",
            linecolor="#dc2626", linewidth=2, showgrid=False,
            anchor="free", position=0.93
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with layout_col2:
    st.markdown("<div style='background-color:#1e293b; padding:22px; border-radius:12px; border: 1px solid #334155;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:15px; font-size:15px; color:#94a3b8;'>🎛️ Live Field Telemetry</h4>", unsafe_allow_html=True)
    
    fig_rpm = go.Figure(go.Indicator(
        mode = "gauge+number", value = motor_rpm,
        title = {'text': "Motor RPM", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {'axis': {'range': [0, 3000], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "#334155"},
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_rpm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=140, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_rpm, use_container_width=True)
    
    fig_vib = go.Figure(go.Indicator(
        mode = "gauge+number", value = vibration,
        title = {'text': "Vibration Level (mm/s)", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {
            'axis': {'range': [0, 10], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#10b981"}, 'bgcolor': "#334155",
            'steps': [{'range': [0, 4], 'color': "rgba(16, 185, 129, 0.2)"}, {'range': [4, 10], 'color': "rgba(239, 68, 68, 0.2)"}]
        },
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_vib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=140, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_vib, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='insight-card'>
            <h4 style='color:#f8fafc; margin-top:0; margin-bottom:12px; border-bottom:1px solid #334155; padding-bottom:8px;'>📋 Engineering Verification</h4>
            <ul style='font-size:13px; color:#cbd5e1; padding-left:18px; line-height: 1.8;'>
                <li>🎯 <b style='color:#f8fafc;'>Optimal BEP Alignment:</b> Kurva efisiensi dan titik kerja didesain mengunci otomatis pada nilai puncak parameter aktual.</li>
                <li>🛡️ <b style='color:#f8fafc;'>Auto-Scaling Sumbu:</b> Batas atas pengamatan grafik dikalkulasi real-time agar fluktuasi input ekstrem tidak memotong visualisasi kurva.</li>
            </ul>
            <div class='alert-box'>
                <b>💡 Catatan Dashboard:</b> Modul kalkulasi matematika di atas mengadaptasi rasio empiris pompa sentrifugal nyata untuk mensimulasikan hukum afinitas dasar secara visual.
            </div>
        </div>
    """, unsafe_allow_html=True)
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Centrifugal Pump Performance Curve - HVAC T3", layout="wide")

# 2. INJEKSI CSS GLOBAL
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
        .metric-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
        .metric-title { color: #94a3b8 !important; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
        .metric-value { color: #f8fafc !important; font-size: 30px; font-weight: 700; margin: 6px 0; }
        .metric-sub { font-size: 12px; font-weight: 600; }
        
        .insight-card { background-color: #1e293b; border-radius: 12px; padding: 22px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
        .alert-box { background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 12px; border-radius: 6px; margin-top: 15px; color: #d9f99d !important; font-size: 13px; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: INPUT PARAMETER ---
st.sidebar.title("🎮 Panel Kontrol & Input")
st.sidebar.subheader("🎯 Titik Kerja Aktual (GPM - FT)")
q_actual = st.sidebar.number_input("Capacity (GPM)", min_value=10.0, max_value=20000.0, value=8000.0, step=100.0)
h_actual = st.sidebar.number_input("Total Head (FT)", min_value=10.0, max_value=1000.0, value=260.0, step=5.0)
p_cons = st.sidebar.number_input("Brake Horsepower (BHP)", min_value=10.0, max_value=5000.0, value=510.0, step=10.0)
pump_eff = st.sidebar.number_input("Pump Efficiency (%)", min_value=5.0, max_value=100.0, value=80.0, step=1.0)

st.sidebar.subheader("⚙️ Kondisi Sensor")
motor_rpm = st.sidebar.number_input("Motor RPM", min_value=0, max_value=5000, value=1450, step=10)
vibration = st.sidebar.number_input("Vibration Level (mm/s)", min_value=0.0, max_value=10.0, value=1.8, step=0.1)

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='color:#f8fafc; font-weight:700; margin-bottom:25px;'>📊 Centrifugal Pump Performance Analyzer</h1>", unsafe_allow_html=True)

# Baris 1: Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Pump Capacity</div><div class='metric-value'>{q_actual:.0f} <span style='font-size:14px; font-weight:normal; color:#94a3b8;'>GPM</span></div><div class='metric-sub' style='color:#10b981;'>🟢 Target Operating Point</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Total Head</div><div class='metric-value'>{h_actual:.0f} <span style='font-size:14px; font-weight:normal; color:#94a3b8;'>FT</span></div><div class='metric-sub' style='color:#10b981;'>🟢 Design Balanced</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Efficiency (η)</div><div class='metric-value'>{pump_eff}%</div><div class='metric-sub' style='color:#10b981;'>🎯 At Peak BEP Zone</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Brake Power</div><div class='metric-value'>{p_cons:.0f} <span style='font-size:14px; font-weight:normal; color:#94a3b8;'>BHP</span></div><div class='metric-sub' style='color:#60a5fa;'>⚡ Motor Load Nominal</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Baris 2: Layout Grafik & Analisis Telemetri
layout_col1, layout_col2 = st.columns([8, 4])

with layout_col1:
    # --- 🧮 FORMULA MATEMATIKA KURVA DINAMIS ---
    # Pencegahan error jika user memasukkan angka nol/negatif
    q_ref = max(1.0, q_actual)
    h_ref = max(1.0, h_actual)
    eff_ref = max(5.0, pump_eff)
    p_ref = max(1.0, p_cons)

    # 1. Rentang Kapasitas Sumbu X Dinamis (Selalu meluas sampai 140% dari kapasitas aktual)
    q_max_plot = q_ref * 1.4
    q_plot = np.linspace(0, q_max_plot, 100)

    # 2. Kurva Q-H Dinamis (Menjamin kurva melengkung mulus melewati titik input actual)
    # Asumsi karakteristik standard: Shut-off Head berada di ~1.35x dari Head aktual
    h_shutoff = 1.35 * h_ref
    a_coeff = (0.35 * h_ref) / (q_ref ** 2)
    h_plot = h_shutoff - (a_coeff * (q_plot ** 2))
    h_plot = np.clip(h_plot, 0, None)

    # 3. Kurva Efisiensi Dinamis (Puncak BEP bergeser otomatis mengikuti q_actual & pump_eff)
    # Asumsi efisiensi drop ke batas 10% di area ekstrim ujung kiri/kanan kapasitas
    b_coeff = (eff_ref - 10) / (q_ref ** 2)
    eff_plot = eff_ref - b_coeff * (q_plot - q_ref) ** 2
    eff_plot = np.clip(eff_plot, 0, 100)

    # 4. Kurva BHP Dinamis (BHP naik seiring peningkatan debit, mengunci nilai p_cons aktual)
    bhp_plot = p_ref * (0.4 + 0.7 * (q_plot / q_ref) - 0.1 * (q_plot / q_ref) ** 2)
    bhp_plot = np.clip(bhp_plot, 0, None)

    # 5. Kurva NPSHr Dinamis (Naik secara eksponensial terhadap debit fluida)
    npsh_plot = 4 + 12 * (q_plot / q_ref) ** 1.5

    # --- 📊 RENDERING PLOTLY ---
    fig = go.Figure()

    # Trace 1: Q-H Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=h_plot, mode='lines', name='Q-H CURVE',
        line=dict(color='black', width=3.5), yaxis='y1'
    ))
    
    # Trace 2: Efficiency Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=eff_plot, mode='lines', name='EFFICIENCY (η) CURVE',
        line=dict(color='#16a34a', width=3), yaxis='y2'
    ))
    
    # Trace 3: BHP Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=bhp_plot, mode='lines', name='BHP CURVE',
        line=dict(color='#dc2626', width=3), yaxis='y3'
    ))
    
    # Trace 4: NPSHr Curve
    fig.add_trace(go.Scatter(
        x=q_plot, y=npsh_plot, mode='lines', name='NPSHr CURVE',
        line=dict(color='#ea580c', width=2.5), yaxis='y1'
    ))

    # Titik Kerja Aktual (Duty Point)
    fig.add_trace(go.Scatter(
        x=[q_actual], y=[h_actual], mode='markers', name='DUTY POINT',
        marker=dict(symbol='x', size=18, line=dict(width=4), color='#1d4ed8'),
        yaxis='y1', showlegend=False
    ))

    # Garis Silang Proyeksi Desain (Mengikuti batas atas skala dinamis secara proporsional)
    fig.add_shape(type="line", x0=q_actual, y0=0, x1=q_actual, y1=h_shutoff * 1.05, line=dict(color="#1d4ed8", width=2, dash="dash"), yref="y1")
    fig.add_shape(type="line", x0=0, y0=h_actual, x1=q_actual, y1=h_actual, line=dict(color="#1d4ed8", width=2, dash="dash"), yref="y1")

    # Anotasi Teks Grafik Dinamis
    fig.add_annotation(
        x=q_actual + (q_max_plot * 0.02), y=h_actual + (h_shutoff * 0.04), 
        text=f"DUTY POINT:<br>{q_actual:.0f} GPM @ {h_actual:.0f} FT HEAD",
        showarrow=False, font=dict(color="#1d4ed8", size=11, family="Arial"), align="left"
    )

    # Konfigurasi Layout Multi-Sumbu Berbasis Skala Pengguna
    fig.update_layout(
        title={"text": "LIVE DYNAMIC CENTRIFUGAL PUMP PERFORMANCE CURVE", "font": {"color": "#000000", "size": 13}},
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=70, r=130, t=60, b=65),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="black")),
        
        xaxis=dict(
            title=dict(text="CAPACITY IN GALLONS PER MINUTE (GPM)", font=dict(color="black", size=11)),
            range=[0, q_max_plot], gridcolor="#e2e8f0", linecolor="black", linewidth=2, ticks="outside",
            domain=[0, 0.80]
        ),
        yaxis=dict(
            title=dict(text="HEAD IN FEET (FT)", font=dict(color="black", size=11)),
            range=[0, h_shutoff * 1.08], gridcolor="#e2e8f0", linecolor="black", linewidth=2, ticks="outside"
        ),
        yaxis2=dict(
            title=dict(text="EFFICIENCY % (η)", font=dict(color="#16a34a", size=11)),
            range=[0, 110], side="right", overlaying="y", ticks="outside",
            linecolor="#16a34a", linewidth=2, showgrid=False
        ),
        yaxis3=dict(
            title=dict(text="BRAKE HORSEPOWER (BHP)", font=dict(color="#dc2626", size=11)),
            range=[0, p_ref * 1.4], side="right", overlaying="y", ticks="outside",
            linecolor="#dc2626", linewidth=2, showgrid=False,
            anchor="free", position=0.93
        )
    )
    st.plotly_chart(fig, use_container_width=True)

with layout_col2:
    st.markdown("<div style='background-color:#1e293b; padding:22px; border-radius:12px; border: 1px solid #334155;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:15px; font-size:15px; color:#94a3b8;'>🎛️ Live Field Telemetry</h4>", unsafe_allow_html=True)
    
    fig_rpm = go.Figure(go.Indicator(
        mode = "gauge+number", value = motor_rpm,
        title = {'text': "Motor RPM", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {'axis': {'range': [0, 3000], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "#334155"},
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_rpm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=140, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_rpm, use_container_width=True)
    
    fig_vib = go.Figure(go.Indicator(
        mode = "gauge+number", value = vibration,
        title = {'text': "Vibration Level (mm/s)", 'font': {'size': 13, 'color': '#94a3b8'}},
        gauge = {
            'axis': {'range': [0, 10], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#10b981"}, 'bgcolor': "#334155",
            'steps': [{'range': [0, 4], 'color': "rgba(16, 185, 129, 0.2)"}, {'range': [4, 10], 'color': "rgba(239, 68, 68, 0.2)"}]
        },
        number = {'font': {'color': '#f8fafc', 'size': 22}}
    ))
    fig_vib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=140, margin=dict(l=25, r=25, t=35, b=5))
    st.plotly_chart(fig_vib, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='insight-card'>
            <h4 style='color:#f8fafc; margin-top:0; margin-bottom:12px; border-bottom:1px solid #334155; padding-bottom:8px;'>📋 Engineering Verification</h4>
            <ul style='font-size:13px; color:#cbd5e1; padding-left:18px; line-height: 1.8;'>
                <li>🎯 <b style='color:#f8fafc;'>Optimal BEP Alignment:</b> Kurva efisiensi dan titik kerja didesain mengunci otomatis pada nilai puncak parameter aktual.</li>
                <li>🛡️ <b style='color:#f8fafc;'>Auto-Scaling Sumbu:</b> Batas atas pengamatan grafik dikalkulasi real-time agar fluktuasi input ekstrem tidak memotong visualisasi kurva.</li>
            </ul>
            <div class='alert-box'>
                <b>💡 Catatan Dashboard:</b> Modul kalkulasi matematika di atas mengadaptasi rasio empiris pompa sentrifugal nyata untuk mensimulasikan hukum afinitas (*affinity laws*) dasar secara visual.
            </div>
        </div>
    """, unsafe_allow_html=True)
