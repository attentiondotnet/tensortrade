"""
Simple TensorTrade Example - Buy and Hold Strategy
This demonstrates the basic framework components and structure.
"""

import sys
import os

# Add tensortrade to path
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd

from tensortrade.core import TradingContext
from tensortrade.env.default.actions import BSH
from tensortrade.env.default.rewards import PBR
from tensortrade.env.generic import TradingEnv, create
from tensortrade.feed import Stream, DataFeed, NameSpace
from tensortrade.oms.exchanges import Exchange
from tensortrade.oms.services.execution.simulated import execute_order
from tensortrade.oms.instruments import USD, BTC
from tensortrade.oms.wallets import Wallet, Portfolio


def generate_sample_data(n_steps=200):
    """Generate sample price data"""
    dates = pd.date_range(start='2023-01-01', periods=n_steps, freq='H')
    # Generate somewhat realistic price movements
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, n_steps)
    price = 20000 * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'date': dates,
        'open': price + np.random.normal(0, 50, n_steps),
        'high': price + np.abs(np.random.normal(50, 50, n_steps)),
        'low': price - np.abs(np.random.normal(50, 50, n_steps)),
        'close': price,
        'volume': np.random.randint(100, 1000, n_steps)
    })
    
    return df


def create_trading_environment():
    """Create a simple trading environment"""
    print("Creating TensorTrade environment...")
    
    # Generate sample market data
    df = generate_sample_data(200)
    print(f"Generated {len(df)} price observations")
    print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # Create price streams
    price_stream = Stream.source(list(df['close']), dtype="float").rename("USD-BTC")
    
    # Setup exchange
    coinbase = Exchange("coinbase", service=execute_order)(
        price_stream
    )
    
    # Setup wallets and portfolio
    cash = Wallet(coinbase, 10000 * USD)
    asset = Wallet(coinbase, 0 * BTC)
    
    portfolio = Portfolio(USD, [
        cash,
        asset
    ])
    
    # Create data feed
    feed = DataFeed([
        price_stream,
    ])
    
    # Create environment with context
    config = {
        "actions": "bsh",  # Buy-Sell-Hold action scheme
        "rewards": "pbr",  # Position-based returns reward scheme
        "shared": {
            "base_instrument": USD,
            "base_precision": 2,
            "instrument_precision": 8
        }
    }
    
    with TradingContext(config):
        env = create(
            portfolio=portfolio,
            action_scheme=BSH(),
            reward_scheme=PBR(),
            feed=feed,
        )
    
    return env


def run_simple_episode():
    """Run a simple trading episode"""
    print("=" * 60)
    print("TensorTrade - Simple Trading Example")
    print("=" * 60)
    
    env = create_trading_environment()
    
    print("\nStarting trading episode...")
    print(f"Action space: {env.action_space}")
    print(f"Observation space shape: {env.observation_space.shape}")
    
    # Reset environment
    observation, info = env.reset()
    print(f"\nInitial observation shape: {observation.shape}")
    
    # Run simple episode with random actions
    done = False
    step_count = 0
    total_reward = 0
    
    print("\nRunning episode with random actions...")
    
    while not done:
        # Take random action
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        
        total_reward += reward
        step_count += 1
        
        # Print every 50 steps
        if step_count % 50 == 0:
            print(f"Step {step_count}: reward={reward:.4f}, total_reward={total_reward:.4f}")
    
    print(f"\nEpisode finished!")
    print(f"Total steps: {step_count}")
    print(f"Total reward: {total_reward:.4f}")
    print(f"Average reward: {total_reward/step_count:.4f}")
    
    # Get final portfolio value
    net_worth = env.action_scheme.portfolio.net_worth
    print(f"Final portfolio value: ${net_worth:.2f}")
    
    return env


if __name__ == "__main__":
    try:
        env = run_simple_episode()
        print("\n✅ Example completed successfully!")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
