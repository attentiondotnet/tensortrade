"""
Simple TensorTrade Example - Component System Demo
This demonstrates the Component and TradingContext pattern.
"""

import sys
import os

# Add tensortrade to path  
sys.path.insert(0, os.path.dirname(__file__))

from tensortrade.core import Component, TradingContext


from tensortrade.core import Component, TradingContext


class SimpleStrategy(Component):
    """A simple trading strategy component"""
    
    registered_name = "strategy"
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        # Access config injected via TradingContext
        self.max_position = self.context.get('max_position', 100)
        self.risk_level = self.context.get('risk_level', 'medium')
    
    def describe(self):
        return (f"Strategy '{self.name}': "
                f"max_position={self.max_position}, "
                f"risk_level={self.risk_level}")


def demo_component_system():
    """Demonstrate the Component and TradingContext pattern"""
    print("=" * 70)
    print("TensorTrade - Component System Demo")
    print("=" * 70)
    
    print("\n1. Components outside TradingContext have no config:")
    print("-" * 70)
    try:
        # This will fail - Components must be created inside a TradingContext
        strategy = SimpleStrategy("TestStrategy")
        print(f"❌ This shouldn't work!")
    except AttributeError as e:
        print(f"✅ Expected error: {e}")
    
    print("\n2. Creating components within TradingContext:")
    print("-" * 70)
    
    # Config for our trading strategy
    config = {
        "strategy": {
            "max_position": 500,
            "risk_level": "high"
        },
        "shared": {
            "base_currency": "USD",
            "trading_pair": "BTC/USD"
        }
    }
    
    with TradingContext(config):
        # Now the component gets config auto-injected
        strategy1 = SimpleStrategy("Aggressive")
        print(f"✅ {strategy1.describe()}")
        
        # Access shared config
        print(f"   Shared config: {strategy1.context.get('base_currency')}")
        print(f"   Trading pair: {strategy1.context.get('trading_pair')}")
    
    print("\n3. Multiple components in same context:")
    print("-" * 70)
    
    config2 = {
        "strategy": {
            "max_position": 50,
            "risk_level": "low"
        }
    }
    
    with TradingContext(config2):
        conservative = SimpleStrategy("Conservative")
        print(f"✅ {conservative.describe()}")
    
    print("\n4. Running a real unit test from the test suite:")
    print("-" * 70)
    print("Running: pytest tests/tensortrade/unit/base/test_component.py ...")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", 
         "tests/tensortrade/unit/base/test_component.py",
         "-v", "--tb=line", "-q"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )
    
    # Show test output
    if result.returncode == 0:
        print("✅ All tests passed!")
        # Count passed tests
        passed = result.stdout.count("PASSED")
        print(f"   {passed} tests passed successfully")
    else:
        print("❌ Some tests failed")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    
    return True


if __name__ == "__main__":
    print("\n🚀 Welcome to TensorTrade!")
    print("A framework for building RL trading algorithms\n")
    
    try:
        demo_component_system()
        
        print("\n" + "=" * 70)
        print("✅ Demo completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("  • Check examples/ folder for Jupyter notebooks")
        print("  • Run: make test (to run full test suite)")
        print("  • Run: make run-notebook (to launch Jupyter)")
        print("  • Read docs: https://tensortrade.org")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
