"""
Streamlit Frontend for Supply Chain AI Demo
Compelling interface with interactive sections and real data
"""

import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from agents import Runner
from supply_chain_agents import (
    orchestrator_agent,
    risk_agent,
    demand_agent,
    supplier_agent,
    inventory_agent,
    logistics_agent,
    reporting_agent
)
from demo.scenarios import get_scenario, list_scenarios
from tools.data_loader import get_data_loader
from tools.data_uploader import DataUploader
from utils.helpers import validate_api_keys
from ml_models.rl_inventory_optimizer import train_rl_model, get_optimal_action, QLearningAgent, HumanFeedbackReward
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Supply Chain Intelligence — Multi-Agent Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with beautiful professional styling
st.markdown("""
    <style>
    /* Main Header with Gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
        letter-spacing: 2px;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Tagline Container */
    .tagline-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    }
    
    .tagline-main {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2d3748;
        text-align: center;
        margin-bottom: 0.8rem;
        line-height: 1.6;
    }
    
    .tagline-sub {
        font-size: 1.1rem;
        color: #4a5568;
        text-align: center;
        font-weight: 500;
        line-height: 1.5;
    }
    
    /* Feature Pills */
    .feature-pills {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.8rem;
        margin: 1.5rem 0;
    }
    
    .pill {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s;
    }
    
    .pill:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Sub Header */
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Status Boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
    }
    
    /* Icon Styling */
    .icon-large {
        font-size: 2rem;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    
    /* Divider Enhancement */
    .stDivider {
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        height: 2px;
        margin: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_supplier_data():
    """Load supplier data."""
    loader = get_data_loader()
    return loader.load_supplier_data()


@st.cache_data
def load_inventory_data():
    """Load inventory data."""
    loader = get_data_loader()
    return loader.load_inventory_data()


@st.cache_data
def load_demand_data():
    """Load demand data."""
    loader = get_data_loader()
    return loader.load_demand_history(days_back=90)


def run_agent_async(agent, query):
    """Run agent asynchronously."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(Runner.run(agent, query, session=None))
        return result
    finally:
        loop.close()


def main():
    """Main Streamlit application."""
    
    # Beautiful Header with Gradient and Icons
    st.markdown('<div class="main-header">🚀 Supply Chain Intelligence</div>', unsafe_allow_html=True)
    
    # Compelling Taglines
    st.markdown("""
    <div class="tagline-container">
        <div class="tagline-main">
            ⚡ Transform Your Supply Chain with AI-Powered Intelligence
        </div>
        <div class="tagline-sub">
            Real-time risk monitoring • Predictive analytics • Autonomous decision-making • Continuous learning
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Pills with Icons
    st.markdown("""
    <div class="feature-pills">
        <span class="pill">🛡️ Risk Intelligence</span>
        <span class="pill">📊 Demand Forecasting</span>
        <span class="pill">🏭 Supplier Assessment</span>
        <span class="pill">📦 Inventory Optimization</span>
        <span class="pill">🚚 Logistics Planning</span>
        <span class="pill">🤖 Multi-Agent AI</span>
        <span class="pill">📈 Real-Time Analytics</span>
        <span class="pill">🎯 Continuous Learning</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Subtitle
    st.markdown("""
    <p style="text-align: center; color: #667eea; font-size: 1rem; font-weight: 600; margin-top: 1rem;">
        Multi-Agent Orchestration Platform • Powered by OpenAI Agents SDK
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Navigation - Top Left
        st.header("📋 Navigation")
        page = st.radio(
            "Select Section",
            ["Dashboard", "Data Upload & Analysis", "Risk Assessment", "Demand Forecasting", 
             "Supplier Analysis", "Inventory Optimization (RL)", "Logistics Planning", 
             "Human-in-the-Loop Learning", "Comprehensive Analysis", "Demo Scenarios"]
        )
        
        st.divider()
        
        # AI Agents
        st.header("🤖 AI Agents")
        st.markdown("""
        **Orchestrator**  
        Coordinates all agents and workflows
        
        **Risk Intelligence**  
        Monitors geopolitical risks in real-time
        
        **Demand Forecasting**  
        Predicts future demand and shortages
        
        **Supplier Assessment**  
        Evaluates suppliers and finds alternatives
        
        **Inventory Optimization**  
        Optimizes stock using AI learning
        
        **Logistics Planning**  
        Finds best routes and shipping methods
        
        **Executive Reporting**  
        Creates comprehensive supply chain reports
        """)
        
        st.divider()
        
        # Key Functionalities
        st.subheader("🔧 Key Features")
        st.markdown("""
        • Upload your supply chain data (CSV/Excel)
        
        • Real-time risk monitoring and alerts
        
        • AI-powered demand forecasting
        
        • Supplier reliability scoring
        
        • Smart inventory optimization
        
        • Learn from your feedback
        
        • Multi-agent coordination
        
        • Complete supply chain analytics
        """)
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Data Upload & Analysis":
        show_data_upload()
    elif page == "Risk Assessment":
        show_risk_assessment()
    elif page == "Demand Forecasting":
        show_demand_forecasting()
    elif page == "Supplier Analysis":
        show_supplier_analysis()
    elif page == "Inventory Optimization (RL)":
        show_inventory_optimization_rl()
    elif page == "Logistics Planning":
        show_logistics_planning()
    elif page == "Human-in-the-Loop Learning":
        show_human_feedback()
    elif page == "Comprehensive Analysis":
        show_comprehensive_analysis()
    elif page == "Demo Scenarios":
        show_demo_scenarios()


def show_dashboard():
    """Show main dashboard."""
    st.markdown('<div class="sub-header">📊 Supply Chain Dashboard</div>', unsafe_allow_html=True)
    
    # Load real data
    try:
        suppliers_df = load_supplier_data()
        inventory_df = load_inventory_data()
        demand_df = load_demand_data()
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Suppliers", len(suppliers_df))
        
        with col2:
            st.metric("Active Products", len(inventory_df))
        
        with col3:
            avg_reliability = suppliers_df['reliability_score'].mean()
            st.metric("Avg Supplier Reliability", f"{avg_reliability:.2%}")
        
        with col4:
            high_risk_suppliers = len(suppliers_df[suppliers_df['geopolitical_risk'] > 0.5])
            st.metric("High Risk Suppliers", high_risk_suppliers)
        
        st.divider()
        
        # Supplier Risk Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Supplier Risk Distribution")
            risk_counts = suppliers_df['geopolitical_risk'].apply(
                lambda x: 'High' if x > 0.5 else 'Medium' if x > 0.3 else 'Low'
            ).value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Supplier Risk Levels"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Supplier by Country")
            country_counts = suppliers_df['country'].value_counts().head(10)
            fig = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                title="Suppliers by Country",
                labels={'x': 'Country', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Inventory Status
        st.subheader("Inventory Status")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Stock Levels**")
            inventory_display = inventory_df[['product_id', 'current_stock', 'reorder_point']].head(10)
            st.dataframe(inventory_display, use_container_width=True)
        
        with col2:
            st.write("**Products Below Reorder Point**")
            low_stock = inventory_df[inventory_df['current_stock'] < inventory_df['reorder_point']]
            if len(low_stock) > 0:
                st.dataframe(low_stock[['product_id', 'current_stock', 'reorder_point']], use_container_width=True)
            else:
                st.success("All products are above reorder point!")
        
        # Recent Demand Trends
        if len(demand_df) > 0:
            st.subheader("Recent Demand Trends")
            demand_summary = demand_df.groupby('product_id')['demand'].sum().head(10)
            fig = px.line(
                x=demand_summary.index,
                y=demand_summary.values,
                title="Total Demand by Product (Last 90 Days)",
                labels={'x': 'Product ID', 'y': 'Total Demand'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading data: {e}")


def show_risk_assessment():
    """Show risk assessment interface."""
    st.markdown('<div class="sub-header">⚠️ Risk Assessment</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Geopolitical Risk Analysis")
        country = st.selectbox(
            "Select Country",
            ["China", "Vietnam", "India", "Mexico", "Taiwan", "South Korea", "Japan", "Germany"],
            key="risk_country_select"
        )
        product = st.text_input("Product Category (optional)", "Memory Chips")
    
    with col2:
        st.subheader("Actions")
        assess_button = st.button("🔍 Assess Risk", type="primary", use_container_width=True)
        use_cache = st.checkbox("Use Cached Data", value=True)
    
    if assess_button:
        with st.spinner("Assessing geopolitical risks..."):
            query = f"Assess the geopolitical risk for {product} from {country}"
            try:
                result = run_agent_async(risk_agent, query)
                
                if hasattr(result, 'final_output'):
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write("### Risk Assessment Results")
                    st.write(result.final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Supplier Risk Overview
    st.divider()
    st.subheader("Supplier Risk Overview")
    
    try:
        suppliers_df = load_supplier_data()
        
        # Filter by country if selected
        if 'country' in locals():
            country_suppliers = suppliers_df[suppliers_df['country'] == country]
            if len(country_suppliers) > 0:
                st.write(f"**Suppliers in {country}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        country_suppliers.head(10),
                        x='supplier_name',
                        y='geopolitical_risk',
                        title=f"Geopolitical Risk - {country} Suppliers",
                        labels={'geopolitical_risk': 'Risk Score', 'supplier_name': 'Supplier'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.dataframe(
                        country_suppliers[['supplier_name', 'reliability_score', 'geopolitical_risk', 'export_control_status']].head(10),
                        use_container_width=True
                    )
    except Exception as e:
        st.error(f"Error loading supplier data: {e}")


def show_demand_forecasting():
    """Show demand forecasting interface."""
    st.markdown('<div class="sub-header">📈 Demand Forecasting</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Product Demand Forecast")
        try:
            inventory_df = load_inventory_data()
            product_id = st.selectbox(
                "Select Product",
                inventory_df['product_id'].tolist() if len(inventory_df) > 0 else ["Product_1"],
                key="demand_product_select"
            )
        except:
            product_id = st.text_input("Product ID", "Product_1", key="demand_product_text")
        
        forecast_days = st.slider("Forecast Period (days)", 7, 90, 30, key="forecast_days_slider")
    
    with col2:
        st.subheader("Actions")
        forecast_button = st.button("📊 Generate Forecast", type="primary", use_container_width=True)
        detect_shortage_button = st.button("⚠️ Detect Shortages", use_container_width=True)
    
    if forecast_button:
        with st.spinner("Generating demand forecast..."):
            query = f"Forecast demand for {product_id} for the next {forecast_days} days"
            try:
                result = run_agent_async(demand_agent, query)
                
                if hasattr(result, 'final_output'):
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write("### Forecast Results")
                    st.write(result.final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    if detect_shortage_button:
        with st.spinner("Detecting potential shortages..."):
            query = f"Detect potential shortages for {product_id}"
            try:
                result = run_agent_async(demand_agent, query)
                
                if hasattr(result, 'final_output'):
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.write("### Shortage Analysis")
                    st.write(result.final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Historical Demand Visualization
    st.divider()
    st.subheader("Historical Demand Data")
    
    try:
        demand_df = load_demand_data()
        if len(demand_df) > 0:
            product_demand = demand_df[demand_df['product_id'] == product_id] if 'product_id' in demand_df.columns else demand_df
            
            if len(product_demand) > 0:
                fig = px.line(
                    product_demand,
                    x='date',
                    y='demand',
                    title=f"Historical Demand - {product_id}",
                    labels={'date': 'Date', 'demand': 'Demand'}
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Historical demand data not available for visualization")


def show_supplier_analysis():
    """Show supplier analysis interface."""
    st.markdown('<div class="sub-header">🏭 Supplier Analysis</div>', unsafe_allow_html=True)
    
    try:
        suppliers_df = load_supplier_data()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            supplier_id = st.selectbox(
                "Select Supplier",
                suppliers_df['supplier_id'].tolist() if len(suppliers_df) > 0 else ["SUP001"],
                key="supplier_analysis_select"
            )
        
        with col2:
            st.subheader("Actions")
            evaluate_button = st.button("📊 Evaluate Supplier", type="primary", use_container_width=True)
            find_alternatives_button = st.button("🔍 Find Alternatives", use_container_width=True)
        
        if evaluate_button:
            with st.spinner("Evaluating supplier..."):
                query = f"Evaluate supplier {supplier_id} and provide detailed assessment"
                try:
                    result = run_agent_async(supplier_agent, query)
                    
                    if hasattr(result, 'final_output'):
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write("### Supplier Evaluation")
                        st.write(result.final_output)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if find_alternatives_button:
            with st.spinner("Finding alternative suppliers..."):
                query = f"Find alternative suppliers for {supplier_id}"
                try:
                    result = run_agent_async(supplier_agent, query)
                    
                    if hasattr(result, 'final_output'):
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write("### Alternative Suppliers")
                        st.write(result.final_output)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Supplier Comparison
        st.divider()
        st.subheader("Supplier Comparison")
        
        selected_suppliers = st.multiselect(
            "Select Suppliers to Compare",
            suppliers_df['supplier_id'].tolist(),
            default=suppliers_df['supplier_id'].head(5).tolist() if len(suppliers_df) >= 5 else suppliers_df['supplier_id'].tolist()
        )
        
        if selected_suppliers:
            comparison_df = suppliers_df[suppliers_df['supplier_id'].isin(selected_suppliers)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    comparison_df,
                    x='supplier_name',
                    y=['reliability_score', 'on_time_delivery', 'quality_score'],
                    title="Supplier Performance Metrics",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    comparison_df[['supplier_name', 'country', 'reliability_score', 'geopolitical_risk', 'export_control_status']],
                    use_container_width=True
                )
    
    except Exception as e:
        st.error(f"Error loading supplier data: {e}")


def show_inventory_optimization_rl():
    """Show RL-based inventory optimization interface."""
    st.markdown('<div class="sub-header">🤖 Inventory Optimization with Reinforcement Learning</div>', unsafe_allow_html=True)
    
    st.write("""
    **Reinforcement Learning Model** learns optimal inventory policies through:
    - **Q-Learning**: Learns action-value function
    - **Human Feedback**: Incorporates domain expertise
    - **Continuous Improvement**: Gets better over time
    """)
    
    try:
        inventory_df = load_inventory_data()
        demand_df = load_demand_data()
        
        if len(inventory_df) == 0:
            st.warning("No inventory data available. Please upload data first.")
            return
        
        product_id = st.selectbox("Select Product", inventory_df['product_id'].tolist(), key="inventory_rl_product_select")
        
        product_inv = inventory_df[inventory_df['product_id'] == product_id].iloc[0]
        product_demand = demand_df[demand_df['product_id'] == product_id] if len(demand_df) > 0 else pd.DataFrame()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current State")
            st.metric("Current Stock", int(product_inv['current_stock']))
            st.metric("Reorder Point", int(product_inv['reorder_point']))
            st.metric("Lead Time", f"{int(product_inv['lead_time_days'])} days")
            
            if len(product_demand) > 0:
                avg_demand = product_demand['demand'].mean()
                st.metric("Avg Daily Demand", f"{avg_demand:.2f}")
        
        with col2:
            st.subheader("RL Model Actions")
            
            # Prepare product data for RL
            product_data = {
                'product_id': product_id,
                'current_stock': int(product_inv['current_stock']),
                'reorder_point': int(product_inv['reorder_point']),
                'lead_time_days': int(product_inv['lead_time_days']),
                'unit_cost': float(product_inv['unit_cost']),
                'holding_cost_rate': float(product_inv['holding_cost_rate']),
                'avg_demand': float(product_demand['demand'].mean()) if len(product_demand) > 0 else 100,
                'demand_history': product_demand['demand'].tolist() if len(product_demand) > 0 else []
            }
            
            if st.button("🎯 Get RL Recommendation", type="primary"):
                with st.spinner("Getting optimal action from RL model..."):
                    try:
                        from ml_models.rl_inventory_optimizer import InventoryRLEnvironment, QLearningAgent, get_optimal_action
                        
                        env = InventoryRLEnvironment(product_data)
                        agent = QLearningAgent()
                        
                        # Load model if exists
                        model_path = f"ml_models/rl_models/inventory_{product_id}.pkl"
                        if os.path.exists(model_path):
                            agent.load(model_path)
                        
                        state = env.state
                        action_space = env.action_space
                        optimal_action = get_optimal_action(agent, state, action_space)
                        
                        st.success(f"✅ Recommended Order Quantity: **{optimal_action} units**")
                        
                        st.write("**Decision Rationale:**")
                        st.write(f"- Current Stock: {state[0]} units")
                        st.write(f"- Days Until Delivery: {state[1]} days")
                        st.write(f"- Forecasted Demand: {state[2]:.2f} units/day")
                        st.write(f"- Recommended Action: Order {optimal_action} units")
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            episodes = st.slider("Training Episodes", 100, 5000, 1000, key="rl_episodes")
            
            if st.button("🎓 Train RL Model", type="secondary"):
                with st.spinner(f"Training RL model for {episodes} episodes..."):
                    try:
                        from ml_models.rl_inventory_optimizer import train_rl_model
                        agent = train_rl_model(product_data, episodes=episodes)
                        
                        st.success(f"✅ Model trained successfully!")
                        
                        # Show training progress
                        if hasattr(agent, 'training_history') and len(agent.training_history) > 0:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                y=agent.training_history,
                                mode='lines',
                                name='Reward'
                            ))
                            fig.update_layout(
                                title="Training Progress",
                                xaxis_title="Episode",
                                yaxis_title="Total Reward"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Training error: {e}")
        
        # Model Performance
        st.divider()
        st.subheader("Model Performance")
        
        model_path = f"ml_models/rl_models/inventory_{product_id}.pkl"
        if os.path.exists(model_path):
            st.success("✅ Trained model available for this product")
            
            from ml_models.rl_inventory_optimizer import QLearningAgent
            agent = QLearningAgent()
            agent.load(model_path)
            
            st.write(f"**Q-Table Size:** {sum(len(v) for v in agent.q_table.values())} state-action pairs")
            
            if hasattr(agent, 'training_history'):
                st.write(f"**Training Episodes:** {len(agent.training_history)}")
                if len(agent.training_history) > 0:
                    st.write(f"**Latest Reward:** {agent.training_history[-1]:.2f}")
                    st.write(f"**Average Reward:** {sum(agent.training_history[-100:])/min(100, len(agent.training_history)):.2f}")
        else:
            st.info("ℹ️ No trained model yet. Train the model to get recommendations.")
    
    except Exception as e:
        st.error(f"Error: {e}")


def show_inventory_optimization():
    """Show inventory optimization interface (legacy - redirects to RL version)."""
    show_inventory_optimization_rl()


def show_data_upload():
    """Show data upload and preprocessing interface."""
    st.markdown('<div class="sub-header">📤 Data Upload & Analysis</div>', unsafe_allow_html=True)
    
    uploader = DataUploader()
    
    # Tabs for different data types
    tab1, tab2, tab3, tab4 = st.tabs(["Upload Data", "Data Analysis", "Preprocessing", "Data Quality"])
    
    with tab1:
        st.subheader("Upload Your Supply Chain Data")
        
        data_type = st.selectbox(
            "Select Data Type",
            ["suppliers", "inventory", "demand"],
            key="upload_data_type"
        )
        
        uploaded_file = st.file_uploader(
            f"Upload {data_type} data (CSV or Excel)",
            type=['csv', 'xlsx', 'xls'],
            key=f"upload_{data_type}"
        )
        
        if uploaded_file is not None:
            if st.button(f"📥 Process {data_type.title()} Data", type="primary"):
                with st.spinner("Processing uploaded data..."):
                    result = uploader.process_upload(uploaded_file, data_type)
                    
                    if result["success"]:
                        st.success(f"✅ Successfully processed {result['rows']} rows!")
                        st.json({
                            "Rows": result['rows'],
                            "Columns": result['columns'],
                            "File": result['processed_path']
                        })
                        
                        st.subheader("Data Preview")
                        st.dataframe(pd.DataFrame(result['preview']), use_container_width=True)
                        
                        # Clear cache to reload data
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                        if 'errors' in result:
                            for error in result['errors']:
                                st.warning(f"⚠️ {error}")
    
    with tab2:
        st.subheader("Data Analysis & Statistics")
        
        try:
            loader = get_data_loader()
            
            analysis_type = st.selectbox("Select Data Type", ["suppliers", "inventory", "demand"], key="analysis_data_type")
            
            if analysis_type == "suppliers":
                df = loader.load_supplier_data()
                if len(df) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Suppliers", len(df))
                        st.metric("Avg Reliability", f"{df['reliability_score'].mean():.2%}")
                        st.metric("High Risk Suppliers", len(df[df['geopolitical_risk'] > 0.5]))
                    
                    with col2:
                        fig = px.histogram(df, x='reliability_score', title="Reliability Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df.describe(), use_container_width=True)
            
            elif analysis_type == "inventory":
                df = loader.load_inventory_data()
                if len(df) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Total Products", len(df))
                        st.metric("Total Stock Value", f"${(df['current_stock'] * df['unit_cost']).sum():,.2f}")
                        st.metric("Low Stock Items", len(df[df['current_stock'] < df['reorder_point']]))
                    
                    with col2:
                        fig = px.scatter(df, x='current_stock', y='reorder_point', 
                                       title="Stock vs Reorder Point")
                        st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "demand":
                df = loader.load_demand_history(days_back=90)
                if len(df) > 0:
                    st.metric("Total Records", len(df))
                    st.metric("Date Range", f"{df['date'].min()} to {df['date'].max()}")
                    st.metric("Avg Daily Demand", f"{df['demand'].mean():.2f}")
                    
                    fig = px.line(df, x='date', y='demand', title="Demand Over Time")
                    st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error loading data: {e}")
    
    with tab3:
        st.subheader("Data Preprocessing Pipeline")
        
        st.write("""
        **Preprocessing Steps:**
        1. **Data Validation**: Check required columns and data types
        2. **Missing Value Handling**: Fill missing values with defaults or medians
        3. **Data Type Conversion**: Ensure correct data types
        4. **Feature Engineering**: Add derived features (regions, risk scores, etc.)
        5. **Normalization**: Scale numeric values to appropriate ranges
        6. **Data Quality Checks**: Validate ranges and constraints
        """)
        
        if st.button("🔄 Run Preprocessing on All Data", type="primary"):
            with st.spinner("Preprocessing all datasets..."):
                try:
                    loader = get_data_loader()
                    
                    # Preprocess suppliers
                    suppliers = loader.load_supplier_data()
                    suppliers_processed = uploader.preprocess_supplier_data(suppliers)
                    uploader.save_processed_data(suppliers_processed, "suppliers")
                    
                    # Preprocess inventory
                    inventory = loader.load_inventory_data()
                    inventory_processed = uploader.preprocess_inventory_data(inventory)
                    uploader.save_processed_data(inventory_processed, "inventory")
                    
                    # Preprocess demand
                    demand = loader.load_demand_history()
                    demand_processed = uploader.preprocess_demand_data(demand)
                    uploader.save_processed_data(demand_processed, "demand_history")
                    
                    st.success("✅ All data preprocessed successfully!")
                    st.cache_data.clear()
                
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab4:
        st.subheader("Data Quality Report")
        
        try:
            loader = get_data_loader()
            
            quality_type = st.selectbox("Select Dataset", ["suppliers", "inventory", "demand"], key="quality_data_type")
            
            if quality_type == "suppliers":
                df = loader.load_supplier_data()
                st.write("**Data Quality Metrics:**")
                st.write(f"- Total Records: {len(df)}")
                st.write(f"- Missing Values: {df.isnull().sum().sum()}")
                st.write(f"- Duplicates: {df.duplicated().sum()}")
                st.write(f"- Data Types: {df.dtypes.to_dict()}")
                
                st.write("**Column Statistics:**")
                st.dataframe(df.describe(), use_container_width=True)
        
        except Exception as e:
            st.error(f"Error: {e}")


def show_human_feedback():
    """Show human-in-the-loop feedback interface."""
    st.markdown('<div class="sub-header">👤 Human-in-the-Loop Learning</div>', unsafe_allow_html=True)
    
    st.write("""
    **Provide feedback to improve the AI model:**
    - **Approve**: System recommendation was good
    - **Reject**: System recommendation was wrong
    - **Modify**: System recommendation needs adjustment
    
    Your feedback helps the RL model learn and improve over time!
    """)
    
    # Initialize session state for feedback
    if 'feedback_history' not in st.session_state:
        st.session_state.feedback_history = []
    
    if 'feedback_system' not in st.session_state:
        st.session_state.feedback_system = HumanFeedbackReward()
    
    tab1, tab2, tab3 = st.tabs(["Provide Feedback", "Feedback History", "Model Learning Stats"])
    
    with tab1:
        st.subheader("Review System Recommendation")
        
        try:
            inventory_df = load_inventory_data()
            
            if len(inventory_df) == 0:
                st.warning("No inventory data available.")
            else:
                product_id = st.selectbox("Select Product", inventory_df['product_id'].tolist(), key="human_feedback_product_select")
                
                # Get system recommendation
                if st.button("📊 Get System Recommendation", type="primary"):
                    with st.spinner("Getting recommendation..."):
                        try:
                            from ml_models.rl_inventory_optimizer import InventoryRLEnvironment, QLearningAgent, get_optimal_action
                            
                            product_inv = inventory_df[inventory_df['product_id'] == product_id].iloc[0]
                            product_data = {
                                'product_id': product_id,
                                'current_stock': int(product_inv['current_stock']),
                                'reorder_point': int(product_inv['reorder_point']),
                                'lead_time_days': int(product_inv['lead_time_days']),
                                'unit_cost': float(product_inv['unit_cost']),
                                'holding_cost_rate': float(product_inv['holding_cost_rate']),
                                'avg_demand': 100
                            }
                            
                            env = InventoryRLEnvironment(product_data)
                            agent = QLearningAgent()
                            
                            model_path = f"ml_models/rl_models/inventory_{product_id}.pkl"
                            if os.path.exists(model_path):
                                agent.load(model_path)
                            
                            state = env.state
                            optimal_action = get_optimal_action(agent, state, env.action_space)
                            
                            recommendation = {
                                'product_id': product_id,
                                'quantity': optimal_action,
                                'reason': f"Current stock: {state[0]}, Recommended: {optimal_action} units"
                            }
                            
                            st.session_state.current_recommendation = recommendation
                            
                            st.success("**System Recommendation:**")
                            st.json(recommendation)
                        
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                # Feedback interface
                if 'current_recommendation' in st.session_state:
                    st.divider()
                    st.subheader("Your Feedback")
                    
                    feedback_type = st.radio(
                        "How would you rate this recommendation?",
                        ["Approve ✅", "Reject ❌", "Modify 🔧"]
                    )
                    
                    if feedback_type == "Modify 🔧":
                        modified_quantity = st.number_input(
                            "What quantity would you prefer?",
                            min_value=0,
                            value=st.session_state.current_recommendation.get('quantity', 0),
                            step=100
                        )
                    else:
                        modified_quantity = st.session_state.current_recommendation.get('quantity', 0)
                    
                    if st.button("💾 Submit Feedback", type="primary"):
                        feedback_data = {
                            'type': feedback_type.split()[0].lower(),
                            'product_id': st.session_state.current_recommendation['product_id'],
                            'original': st.session_state.current_recommendation,
                            'action': {'quantity': modified_quantity},
                            'timestamp': pd.Timestamp.now().isoformat()
                        }
                        
                        # Calculate reward
                        reward = st.session_state.feedback_system.calculate_reward(
                            feedback_data['type'],
                            feedback_data['original'],
                            feedback_data['action']
                        )
                        
                        feedback_data['reward'] = reward
                        st.session_state.feedback_history.append(feedback_data)
                        
                        st.success(f"✅ Feedback submitted! Reward: {reward:.2f}")
                        
                        # Update RL model with feedback
                        try:
                            product_inv = inventory_df[inventory_df['product_id'] == product_id].iloc[0]
                            product_data = {
                                'product_id': product_id,
                                'current_stock': int(product_inv['current_stock']),
                                'reorder_point': int(product_inv['reorder_point']),
                                'lead_time_days': int(product_inv['lead_time_days']),
                                'unit_cost': float(product_inv['unit_cost']),
                                'holding_cost_rate': float(product_inv['holding_cost_rate']),
                                'avg_demand': 100
                            }
                            
                            # Retrain with feedback
                            from ml_models.rl_inventory_optimizer import train_rl_model
                            agent = train_rl_model(product_data, episodes=100, human_feedback=[feedback_data])
                            st.info("🔄 Model updated with your feedback!")
                        
                        except Exception as e:
                            st.warning(f"Could not update model: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Feedback History")
        
        if len(st.session_state.feedback_history) > 0:
            feedback_df = pd.DataFrame(st.session_state.feedback_history)
            
            st.metric("Total Feedback", len(feedback_df))
            st.metric("Average Reward", f"{feedback_df['reward'].mean():.2f}")
            
            st.dataframe(feedback_df, use_container_width=True)
            
            # Feedback distribution
            if 'type' in feedback_df.columns:
                fig = px.pie(
                    feedback_df,
                    names='type',
                    title="Feedback Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No feedback submitted yet.")
    
    with tab3:
        st.subheader("Model Learning Statistics")
        
        stats = st.session_state.feedback_system.get_feedback_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Feedback", stats.get('total', 0))
        with col2:
            st.metric("Approved", stats.get('approve', 0))
        with col3:
            st.metric("Rejected", stats.get('reject', 0))
        with col4:
            st.metric("Modified", stats.get('modify', 0))
        
        if stats.get('total', 0) > 0:
            st.metric("Average Reward", f"{stats.get('avg_reward', 0):.2f}")
            
            st.write("**Learning Progress:**")
            st.write("The model improves as you provide more feedback. Each approval, rejection, or modification helps the model learn your preferences and business rules.")
    
    try:
        inventory_df = load_inventory_data()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            product_id = st.selectbox(
                "Select Product",
                inventory_df['product_id'].tolist() if len(inventory_df) > 0 else ["Product_1"],
                key="logistics_product_select"
            )
            service_level = st.slider("Service Level", 0.90, 0.99, 0.95, 0.01, key="service_level_slider")
        
        with col2:
            st.subheader("Actions")
            optimize_button = st.button("⚙️ Optimize Inventory", type="primary", use_container_width=True)
            calculate_reorder_button = st.button("📊 Calculate Reorder Point", use_container_width=True)
        
        if optimize_button:
            with st.spinner("Optimizing inventory..."):
                query = f"Optimize inventory for {product_id} with service level {service_level}"
                try:
                    result = run_agent_async(inventory_agent, query)
                    
                    if hasattr(result, 'final_output'):
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write("### Optimization Results")
                        st.write(result.final_output)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if calculate_reorder_button:
            with st.spinner("Calculating reorder point..."):
                query = f"Calculate reorder point for {product_id}"
                try:
                    result = run_agent_async(inventory_agent, query)
                    
                    if hasattr(result, 'final_output'):
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write("### Reorder Point Analysis")
                        st.write(result.final_output)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Current Inventory Status
        st.divider()
        st.subheader("Current Inventory Status")
        
        product_inventory = inventory_df[inventory_df['product_id'] == product_id] if len(inventory_df) > 0 else pd.DataFrame()
        
        if len(product_inventory) > 0:
            inv = product_inventory.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Stock", int(inv['current_stock']))
            with col2:
                st.metric("Reorder Point", int(inv['reorder_point']))
            with col3:
                st.metric("Safety Stock", int(inv['safety_stock']))
            with col4:
                st.metric("Lead Time (days)", int(inv['lead_time_days']))
            
            # Visual comparison
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Current', 'Reorder Point', 'Safety Stock'],
                y=[inv['current_stock'], inv['reorder_point'], inv['safety_stock']],
                name='Stock Levels'
            ))
            fig.update_layout(
                title=f"Inventory Levels - {product_id}",
                yaxis_title="Quantity"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading inventory data: {e}")


def show_logistics_planning():
    """Show logistics planning interface."""
    st.markdown('<div class="sub-header">🚚 Logistics Planning</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        origin = st.selectbox(
            "Origin Country",
            ["China", "Vietnam", "India", "Mexico", "Taiwan", "South Korea", "Japan", "Germany"],
            key="logistics_origin_select"
        )
        destination = st.selectbox(
            "Destination Country",
            ["USA", "UK", "Germany", "France", "Japan", "South Korea", "China", "India"],
            key="logistics_destination_select"
        )
    
    with col2:
        product_category = st.text_input("Product Category", "Memory Chips")
        exclude_countries = st.multiselect(
            "Exclude Countries",
            ["China", "Russia", "North Korea"]
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        optimize_route_button = st.button("🗺️ Optimize Route", type="primary", use_container_width=True)
    
    with col2:
        compare_modes_button = st.button("✈️ Compare Transport Modes", use_container_width=True)
    
    if optimize_route_button:
        with st.spinner("Optimizing route..."):
            query = f"Optimize route from {origin} to {destination} for {product_category}"
            if exclude_countries:
                query += f" excluding {', '.join(exclude_countries)}"
            try:
                result = run_agent_async(logistics_agent, query)
                
                if hasattr(result, 'final_output'):
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write("### Route Optimization Results")
                    st.write(result.final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    if compare_modes_button:
        with st.spinner("Comparing transportation modes..."):
            query = f"Compare transportation modes from {origin} to {destination} for {product_category}"
            try:
                result = run_agent_async(logistics_agent, query)
                
                if hasattr(result, 'final_output'):
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write("### Transportation Mode Comparison")
                    st.write(result.final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")


def show_comprehensive_analysis():
    """Show comprehensive analysis interface."""
    st.markdown('<div class="sub-header">🔍 Comprehensive Supply Chain Analysis</div>', unsafe_allow_html=True)
    
    st.write("Perform a complete end-to-end analysis of your supply chain covering all aspects.")
    
    analysis_options = st.multiselect(
        "Select Analysis Components",
        ["Risk Assessment", "Demand Forecasting", "Supplier Evaluation", "Inventory Optimization", "Logistics Planning"],
        default=["Risk Assessment", "Demand Forecasting", "Supplier Evaluation", "Inventory Optimization"]
    )
    
    if st.button("🚀 Run Comprehensive Analysis", type="primary", use_container_width=True):
        with st.spinner("Running comprehensive analysis... This may take a few minutes..."):
            query = "Perform a comprehensive analysis of our supply chain: "
            if "Risk Assessment" in analysis_options:
                query += "assess all geopolitical risks, "
            if "Demand Forecasting" in analysis_options:
                query += "forecast demand for our top products, "
            if "Supplier Evaluation" in analysis_options:
                query += "evaluate all suppliers, "
            if "Inventory Optimization" in analysis_options:
                query += "optimize inventory across all products, "
            if "Logistics Planning" in analysis_options:
                query += "analyze logistics routes, "
            query += "and provide an executive summary with actionable recommendations."
            
            try:
                result = run_agent_async(orchestrator_agent, query)
                
                if hasattr(result, 'final_output'):
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.write("### Comprehensive Analysis Results")
                    st.write(result.final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")


def show_demo_scenarios():
    """Show demo scenarios interface."""
    st.markdown('<div class="sub-header">🎬 Demo Scenarios</div>', unsafe_allow_html=True)
    
    scenarios = list_scenarios()
    
    selected_scenario = st.selectbox(
        "Select Demo Scenario",
        scenarios,
        key="demo_scenario_select"
    )
    
    if selected_scenario:
        scenario = get_scenario(selected_scenario)
        st.write(f"**{scenario['name']}**")
        st.write(scenario['description'])
        st.write(f"**Expected Agents:** {', '.join(scenario['expected_agents'])}")
        
        st.divider()
        
        st.write("**Scenario Query:**")
        st.code(scenario['query'], language=None)
        
        if st.button("▶️ Run Scenario", type="primary", use_container_width=True):
            with st.spinner(f"Running scenario: {scenario['name']}..."):
                try:
                    result = run_agent_async(orchestrator_agent, scenario['query'])
                    
                    if hasattr(result, 'final_output'):
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.write("### Scenario Results")
                        st.write(result.final_output)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.write(result)
                except Exception as e:
                    st.error(f"Error: {e}")


if __name__ == "__main__":
    main()

