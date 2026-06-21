App.py
import plotly.graph_objects as go

# --- PROSES GRAFIK INTERAKTIF DENGAN PLOTLY (Gaya Dark Mode) ---
fig = go.Figure()

# 1. Kurva Pabrikan
fig.add_trace(go.Scatter(
x=q_plot, y=h_plot,
mode='lines',
name='Kurva Desain Pabrikan',
line=dict(color='#1f77b4', width=3, dash='dash')
))

# 2. Titik Kerja Aktual
fig.add_trace(go.Scatter(
x=[q_actual], y=[h_actual],
mode='markers',
name='Titik Kerja Aktual',
marker=dict(color='#00ffcc', size=15, symbol='star', line=dict(color='white', width=2))
))

# 3. Garis Proyeksi (Gaya Neon)
fig.add_shape(type="line", x0=q_actual, y0=0, x1=q_actual, y1=h_actual, line=dict(color="#00ffcc", width=1, dash="dot"))
fig.add_shape(type="line", x0=0, y0=h_actual, x1=q_actual, y1=h_actual, line=dict(color="#00ffcc", width=1, dash="dot"))

# Layout Styling (Dark Theme ala Dashboard)
fig.update_layout(
title="Professional Pump Performance Curve",
template="plotly_dark",
paper_bgcolor="rgba(17,24,39,1)", # Warna background card
plot_bgcolor="rgba(17,24,39,1)",
xaxis=dict(title="Flow Rate (m³/h)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
yaxis=dict(title="Total Head (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
hovermode="x unified"
)

# Tampilkan di Streamlit
str.plotly_chart(fig, use_container_width=True)
