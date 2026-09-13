"""
New Streamlit Sections: Data Upload, RL Training, Human-in-the-Loop
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from tools.data_uploader import DataUploader
from ml_models.rl_inventory_optimizer import train_rl_model, get_optimal_action, QLearningAgent, HumanFeedbackReward
from tools.data_loader import get_data_loader
import os
import json


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
            ["suppliers", "inventory", "demand"]
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
                        
                        # Reload data
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
            
            analysis_type = st.selectbox("Select Data Type", ["suppliers", "inventory", "demand"])
            
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
            
            quality_type = st.selectbox("Select Dataset", ["suppliers", "inventory", "demand"])
            
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


def show_inventory_optimization_rl():
    """Show RL-based inventory optimization."""
    st.markdown('<div class="sub-header">🤖 Inventory Optimization with Reinforcement Learning</div>', unsafe_allow_html=True)
    
    st.write("""
    **Reinforcement Learning Model** learns optimal inventory policies through:
    - **Q-Learning**: Learns action-value function
    - **Human Feedback**: Incorporates domain expertise
    - **Continuous Improvement**: Gets better over time
    """)
    
    try:
        loader = get_data_loader()
        inventory_df = loader.load_inventory_data()
        demand_df = loader.load_demand_history(days_back=90)
        
        if len(inventory_df) == 0:
            st.warning("No inventory data available. Please upload data first.")
            return
        
        product_id = st.selectbox("Select Product", inventory_df['product_id'].tolist())
        
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
                        from ml_models.rl_inventory_optimizer import InventoryRLEnvironment, QLearningAgent
                        
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
            
            if st.button("🎓 Train RL Model", type="secondary"):
                episodes = st.slider("Training Episodes", 100, 5000, 1000)
                
                if st.button("▶️ Start Training", type="primary"):
                    with st.spinner(f"Training RL model for {episodes} episodes..."):
                        try:
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
            loader = get_data_loader()
            inventory_df = loader.load_inventory_data()
            
            if len(inventory_df) == 0:
                st.warning("No inventory data available.")
                return
            
            product_id = st.selectbox("Select Product", inventory_df['product_id'].tolist())
            
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
                        agent = train_rl_model(product_data, episodes=100, human_feedback=[feedback_data])
                        st.info("🔄 Model updated with your feedback!")
                    
                    except Exception as e:
                        st.warning(f"Could not update model: {e}")
    
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



