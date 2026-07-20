import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Determine base path relative to app.py location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "mine_fleet_telemetry.csv")

# Self-healing fallback: If telemetry doesn't exist, run the simulator script live
if not os.path.exists(csv_path):
    st.info("⚙️ Telemetry data not found. Running haul cycle simulator...")
    import haul_cycle_simulator
    if hasattr(haul_cycle_simulator, 'main'):
        haul_cycle_simulator.main()

df = pd.read_csv(csv_path)

# Set page layout to wide and title the dashboard professionally
st.set_page_config(page_title="Project Horizon | Fleet Electrification Dashboard", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { color: #0f172a !important; font-family: 'Poppins', sans-serif; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-left: 5px solid #3b82f6; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Project Horizon: Fleet Electrification Analytics")
st.subheader("Interactive Operational & Financial Decision Matrix")
st.markdown("---")

# Load data
try:
    df = pd.read_csv("mine_fleet_telemetry.csv")
except FileNotFoundError:
    st.error("🚨 'mine_fleet_telemetry.csv' not found! Run 'python3 haul_cycle_simulator.py' first.")
    st.stop()

# --- SIDEBAR INTERACTIVE SCENARIO INPUTS ---
st.sidebar.header("🎛️ Live Scenario Controls")
st.sidebar.markdown("Modify variables to test financial sensitivity.")

carbon_tax = st.sidebar.slider("Projected Carbon Tax ($/Tonne)", min_value=0, max_value=250, value=100, step=10)
diesel_price = st.sidebar.slider("Commercial Diesel Cost ($/Liter)", min_value=0.50, max_value=2.50, value=1.20, step=0.05)
electricity_price = st.sidebar.slider("Grid Power Tariff ($/kWh)", min_value=0.02, max_value=0.30, value=0.10, step=0.01)
ramp_length = st.sidebar.slider("Total Main Ramp Length (km)", min_value=1.0, max_value=7.0, value=3.5, step=0.5)

# Fixed Logic Constants
DIESEL_EMISSIONS_FACTOR = 2.68
CAPEX_PER_KM = 5000000.0

# --- CORE MATH CALCULATION ENGINE ---
total_diesel_consumed = df["Total_Diesel_Consumed_L"].sum()
total_diesel_saved = df["Ramp_Diesel_Displaced_L"].sum()
total_electricity_bought = df["Grid_Electricity_Drawn_kWh"].sum()

# Dynamic Financials
gross_diesel_savings_usd = total_diesel_saved * diesel_price
co2_abated_tonnes = (total_diesel_saved * DIESEL_EMISSIONS_FACTOR) / 1000
carbon_tax_saved_usd = co2_abated_tonnes * carbon_tax

total_gross_savings = gross_diesel_savings_usd + carbon_tax_saved_usd
new_electricity_cost_usd = total_electricity_bought * electricity_price
net_annual_opex_savings = total_gross_savings - new_electricity_cost_usd

total_infrastructure_capex = ramp_length * CAPEX_PER_KM
payback_period_years = total_infrastructure_capex / net_annual_opex_savings if net_annual_opex_savings > 0 else 0

# --- TOP ROW: STRATEGIC KPI CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Net Annual OpEx Savings", value=f"${net_annual_opex_savings:,.0f}")
col2.metric(label="Total Project Initial CapEx", value=f"${total_infrastructure_capex:,.0f}")
col3.metric(label="Simple Payback Period", value=f"{payback_period_years:.2f} Years")
col4.metric(label="Annual Carbon Abated", value=f"{co2_abated_tonnes:,.0f} Tonnes")

st.markdown("### 📊 Energy & Emissions Modeling Profiles")

# --- BOTTOM ROW: INTERACTIVE PLOTLY GRAPHS ---
col_graph1, col_graph2 = st.columns([2, 1])

with col_graph1:
    # Process Monthly Data
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Month'] = df['Timestamp'].dt.strftime('%b')
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_summary = df.groupby('Month').agg({'Total_Diesel_Consumed_L': 'sum', 'Ramp_Diesel_Displaced_L': 'sum'}).reindex(months_order)
    monthly_summary['Remaining_Diesel_L'] = monthly_summary['Total_Diesel_Consumed_L'] - monthly_summary['Ramp_Diesel_Displaced_L']
    
    # Strictly Plotly Interactive Stacked Chart
    fig_fuel = go.Figure()
    fig_fuel.add_trace(go.Bar(
        x=monthly_summary.index,
        y=monthly_summary['Remaining_Diesel_L'] / 1e3,
        name='Remaining Diesel (Floor/Surface)',
        marker_color='#64748b'
    ))
    fig_fuel.add_trace(go.Bar(
        x=monthly_summary.index,
        y=monthly_summary['Ramp_Diesel_Displaced_L'] / 1e3,
        name='Displaced Diesel (Trolley Assist)',
        marker_color='#3b82f6'
    ))
    
    fig_fuel.update_layout(
        title="Monthly Fleet Fuel Profile (Thousand Liters)",
        barmode='stack',
        template='plotly_white',
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # st.plotly_chart tells Streamlit to render it natively with web interactions
    st.plotly_chart(fig_fuel, use_container_width=True)

with col_graph2:
    co2_baseline = (total_diesel_consumed * DIESEL_EMISSIONS_FACTOR) / 1000
    co2_post = co2_baseline - co2_abated_tonnes
    
    # Strictly Plotly Interactive Bar Chart
    fig_co2 = go.Figure()
    fig_co2.add_trace(go.Bar(
        x=['Baseline Status Quo', 'Post-Electrification'],
        y=[co2_baseline, co2_post],
        marker_color=['#dc2626', '#16a34a'],
        text=[f"{co2_baseline:,.0f} t", f"{co2_post:,.0f} t"],
        textposition='auto',
        width=0.5
    ))
    
    fig_co2.update_layout(
        title="Annual CO2 Footprint (Metric Tonnes)",
        template='plotly_white',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    st.plotly_chart(fig_co2, use_container_width=True)

st.markdown("🔒 *Advisory Engine powered by dynamic telemetry pipelines. Data processed via interactive web rendering components.*")
