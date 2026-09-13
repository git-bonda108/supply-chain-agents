"""
Reinforcement Learning Model for Inventory Optimization
Uses Q-Learning to learn optimal inventory policies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import pickle
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class InventoryRLEnvironment:
    """RL Environment for inventory optimization."""
    
    def __init__(self, product_data: Dict):
        """
        Initialize RL environment.
        
        Args:
            product_data: Product information (demand, lead_time, costs, etc.)
        """
        self.product_data = product_data
        self.current_stock = product_data.get('current_stock', 1000)
        self.reorder_point = product_data.get('reorder_point', 300)
        self.lead_time = product_data.get('lead_time_days', 14)
        self.unit_cost = product_data.get('unit_cost', 50)
        self.holding_cost_rate = product_data.get('holding_cost_rate', 0.20)
        
        # State space: (stock_level, days_until_delivery, demand_forecast)
        self.state = (self.current_stock, 0, product_data.get('avg_demand', 100))
        
        # Action space: order quantities (discrete: 0, 100, 200, ..., 2000)
        self.action_space = list(range(0, 2001, 100))
        
        self.days_until_delivery = 0
        self.pending_order = 0
    
    def reset(self) -> Tuple:
        """Reset environment to initial state."""
        self.current_stock = self.product_data.get('current_stock', 1000)
        self.days_until_delivery = 0
        self.pending_order = 0
        self.state = (self.current_stock, 0, self.product_data.get('avg_demand', 100))
        return self.state
    
    def step(self, action: int, demand: float) -> Tuple[Tuple, float, bool, Dict]:
        """
        Execute one step in environment.
        
        Args:
            action: Order quantity
            demand: Actual demand for this period
        
        Returns:
            (next_state, reward, done, info)
        """
        # Update stock with demand
        self.current_stock = max(0, self.current_stock - demand)
        
        # Process pending orders
        if self.days_until_delivery > 0:
            self.days_until_delivery -= 1
            if self.days_until_delivery == 0:
                self.current_stock += self.pending_order
                self.pending_order = 0
        
        # Place new order if action > 0
        if action > 0:
            self.pending_order = action
            self.days_until_delivery = self.lead_time
        
        # Calculate reward
        reward = self._calculate_reward(demand)
        
        # Update state
        next_state = (
            self.current_stock,
            self.days_until_delivery,
            self.product_data.get('avg_demand', 100)
        )
        self.state = next_state
        
        # Check if done (simulation end)
        done = False
        
        info = {
            "stock": self.current_stock,
            "stockout": self.current_stock == 0,
            "pending_order": self.pending_order
        }
        
        return next_state, reward, done, info
    
    def _calculate_reward(self, demand: float) -> float:
        """
        Calculate reward based on inventory performance.
        
        Args:
            demand: Actual demand
        
        Returns:
            Reward value
        """
        # Base reward for having stock
        reward = 10.0 if self.current_stock > 0 else -50.0  # Stockout penalty
        
        # Holding cost penalty
        holding_cost = self.current_stock * self.unit_cost * self.holding_cost_rate / 365
        reward -= holding_cost * 0.1
        
        # Service level reward
        if self.current_stock >= demand:
            reward += 20.0  # Met demand
        else:
            reward -= 30.0  # Partial fulfillment
        
        # Reorder point adherence
        if self.current_stock <= self.reorder_point and self.pending_order == 0:
            reward -= 10.0  # Should have reordered
        
        return reward


class QLearningAgent:
    """Q-Learning agent for inventory optimization."""
    
    def __init__(
        self,
        state_size: int = 3,
        action_size: int = 21,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1
    ):
        """
        Initialize Q-Learning agent.
        
        Args:
            state_size: Size of state space
            action_size: Size of action space
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Exploration rate
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-table: state -> action -> Q-value
        # Using discretized states
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Track training history
        self.training_history = []
    
    def get_state_key(self, state: Tuple) -> str:
        """Convert state tuple to string key for Q-table."""
        # Discretize state
        stock, delivery, demand = state
        stock_bin = int(stock / 100) * 100  # Round to nearest 100
        delivery_bin = int(delivery / 7) * 7  # Round to nearest week
        demand_bin = int(demand / 10) * 10  # Round to nearest 10
        return f"{stock_bin}_{delivery_bin}_{demand_bin}"
    
    def choose_action(self, state: Tuple, action_space: List[int], training: bool = True) -> int:
        """
        Choose action using epsilon-greedy policy.
        
        Args:
            state: Current state
            action_space: Available actions
            training: Whether in training mode
        
        Returns:
            Selected action
        """
        state_key = self.get_state_key(state)
        
        if training and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(action_space)
        else:
            # Exploit: best known action
            q_values = [self.q_table[state_key][action] for action in action_space]
            best_action_idx = np.argmax(q_values)
            return action_space[best_action_idx]
    
    def update(self, state: Tuple, action: int, reward: float, next_state: Tuple, done: bool):
        """
        Update Q-table using Q-learning algorithm.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        # Next best Q-value
        next_max_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
        
        # Q-learning update
        if done:
            target_q = reward
        else:
            target_q = reward + self.discount_factor * next_max_q
        
        # Update Q-value
        self.q_table[state_key][action] = current_q + self.learning_rate * (target_q - current_q)
    
    def save(self, filepath: str):
        """Save Q-table to file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
        logger.info(f"Saved Q-table to {filepath}")
    
    def load(self, filepath: str):
        """Load Q-table from file."""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                q_dict = pickle.load(f)
                self.q_table = defaultdict(lambda: defaultdict(float), q_dict)
            logger.info(f"Loaded Q-table from {filepath}")
        else:
            logger.warning(f"Q-table file not found: {filepath}")


class HumanFeedbackReward:
    """Convert human feedback to RL rewards."""
    
    def __init__(self):
        """Initialize feedback reward system."""
        self.feedback_history = []
    
    def calculate_reward(self, feedback_type: str, original_recommendation: Dict, human_action: Dict) -> float:
        """
        Calculate reward from human feedback.
        
        Args:
            feedback_type: Type of feedback (approve, reject, modify)
            original_recommendation: Original system recommendation
            human_action: Human's actual action
        
        Returns:
            Reward value
        """
        if feedback_type == "approve":
            # Positive reward for approval
            reward = 50.0
        elif feedback_type == "reject":
            # Negative reward for rejection
            reward = -30.0
        elif feedback_type == "modify":
            # Moderate reward, depends on modification
            modification_ratio = abs(human_action.get('quantity', 0) - original_recommendation.get('quantity', 0)) / max(original_recommendation.get('quantity', 1), 1)
            reward = 20.0 * (1 - modification_ratio)  # Less reward for larger modifications
        else:
            reward = 0.0
        
        self.feedback_history.append({
            "feedback_type": feedback_type,
            "reward": reward,
            "timestamp": pd.Timestamp.now()
        })
        
        return reward
    
    def get_feedback_stats(self) -> Dict:
        """Get statistics on human feedback."""
        if not self.feedback_history:
            return {"total": 0}
        
        df = pd.DataFrame(self.feedback_history)
        return {
            "total": len(df),
            "approve": len(df[df['feedback_type'] == 'approve']),
            "reject": len(df[df['feedback_type'] == 'reject']),
            "modify": len(df[df['feedback_type'] == 'modify']),
            "avg_reward": df['reward'].mean()
        }


def train_rl_model(
    product_data: Dict,
    episodes: int = 1000,
    human_feedback: Optional[List[Dict]] = None
) -> QLearningAgent:
    """
    Train RL model for inventory optimization.
    
    Args:
        product_data: Product information
        episodes: Number of training episodes
        human_feedback: Optional human feedback data
    
    Returns:
        Trained Q-learning agent
    """
    env = InventoryRLEnvironment(product_data)
    agent = QLearningAgent()
    feedback_system = HumanFeedbackReward()
    
    # Load existing model if available
    model_path = f"ml_models/rl_models/inventory_{product_data.get('product_id', 'default')}.pkl"
    if os.path.exists(model_path):
        agent.load(model_path)
    
    # Training loop
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        
        # Simulate 30 days
        for day in range(30):
            # Choose action
            action = agent.choose_action(state, env.action_space, training=True)
            
            # Simulate demand (use actual if available, else random)
            if 'demand_history' in product_data:
                demand = np.random.choice(product_data['demand_history'])
            else:
                demand = np.random.normal(product_data.get('avg_demand', 100), 20)
            
            # Step environment
            next_state, reward, done, info = env.step(action, demand)
            
            # Apply human feedback if available
            if human_feedback and len(human_feedback) > episode % len(human_feedback):
                feedback = human_feedback[episode % len(human_feedback)]
                feedback_reward = feedback_system.calculate_reward(
                    feedback['type'],
                    feedback.get('original', {}),
                    feedback.get('action', {})
                )
                reward += feedback_reward
            
            # Update agent
            agent.update(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        agent.training_history.append(total_reward)
        
        if (episode + 1) % 100 == 0:
            avg_reward = np.mean(agent.training_history[-100:])
            logger.info(f"Episode {episode + 1}, Average Reward: {avg_reward:.2f}")
    
    # Save trained model
    agent.save(model_path)
    
    return agent


def get_optimal_action(agent: QLearningAgent, state: Tuple, action_space: List[int]) -> int:
    """
    Get optimal action from trained agent.
    
    Args:
        agent: Trained Q-learning agent
        state: Current state
        action_space: Available actions
    
    Returns:
        Optimal action
    """
    return agent.choose_action(state, action_space, training=False)



