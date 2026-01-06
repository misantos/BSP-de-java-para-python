#!/usr/bin/env python3
"""
Test edge cases for BSP bug fixes.
Tests scenarios that previously caused crashes or infinite loops.
"""

import sys
from lot import Lot
from lot_stack import LotStack

def test_division_by_zero():
    """Test Bug #1: MAX_SPLIT == MIN_SPLIT (division by zero)."""
    print("=" * 60)
    print("TEST 1: Division by zero (MAX_SPLIT == MIN_SPLIT)")
    print("=" * 60)

    # Create simple square lot
    initial_lot = Lot(0, 0, 500, 0, 500, 500, 0, 500)

    # Edge case: MAX == MIN (would cause division by zero in old code)
    config = {
        'MIN_LOTS': 10,
        'SEED': 123,
        'MIN_SPLIT_X': 2,  # Same as MAX
        'MAX_SPLIT_X': 2,  # Same as MIN
        'MIN_SPLIT_Y': 2,
        'MAX_SPLIT_Y': 2,
        'MIN_HEIGHT_LOT': 50,
        'MIN_WIDTH_LOT': 50,
        'MAX_HEIGHT_LOT': 1000,
        'MAX_WIDTH_LOT': 1000
    }

    try:
        lot_stack = LotStack(initial_lot, config)
        final_lots = lot_stack.get_lots()
        print(f"✅ SUCCESS: Created {len(final_lots)} lots without crashing")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_zero_divisions():
    """Test Bug #1: MIN_SPLIT = 0 (no subdivisions)."""
    print("\n" + "=" * 60)
    print("TEST 2: Zero divisions (MIN_SPLIT = 0)")
    print("=" * 60)

    initial_lot = Lot(0, 0, 500, 0, 500, 500, 0, 500)

    # Edge case: MIN_SPLIT = 0 (would create no lots in old code)
    config = {
        'MIN_LOTS': 5,
        'SEED': 456,
        'MIN_SPLIT_X': 0,  # Zero!
        'MAX_SPLIT_X': 2,
        'MIN_SPLIT_Y': 0,
        'MAX_SPLIT_Y': 2,
        'MIN_HEIGHT_LOT': 50,
        'MIN_WIDTH_LOT': 50,
        'MAX_HEIGHT_LOT': 1000,
        'MAX_WIDTH_LOT': 1000
    }

    try:
        lot_stack = LotStack(initial_lot, config)
        final_lots = lot_stack.get_lots()
        print(f"✅ SUCCESS: Created {len(final_lots)} lots (graceful handling)")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_infinite_loop_prevention():
    """Test Bug #2: Infinite loop prevention with impossible constraints."""
    print("\n" + "=" * 60)
    print("TEST 3: Infinite loop prevention (impossible constraints)")
    print("=" * 60)

    # Small lot with high MIN_LOTS (impossible to achieve)
    initial_lot = Lot(0, 0, 200, 0, 200, 200, 0, 200)

    config = {
        'MIN_LOTS': 100,  # Impossible to reach!
        'SEED': 789,
        'MIN_SPLIT_X': 1,
        'MAX_SPLIT_X': 3,
        'MIN_SPLIT_Y': 1,
        'MAX_SPLIT_Y': 3,
        'MIN_HEIGHT_LOT': 50,  # Constraints prevent reaching 100 lots
        'MIN_WIDTH_LOT': 50,
        'MAX_HEIGHT_LOT': 1000,
        'MAX_WIDTH_LOT': 1000
    }

    try:
        lot_stack = LotStack(initial_lot, config)
        final_lots = lot_stack.get_lots()
        print(f"✅ SUCCESS: Stopped gracefully at {len(final_lots)} lots (stagnation detection)")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all edge case tests."""
    print("\n🧪 BSP Edge Case Test Suite")
    print("Testing bug fixes for infinite loops and division by zero\n")

    results = []

    # Run all tests
    results.append(("Division by zero", test_division_by_zero()))
    results.append(("Zero divisions", test_zero_divisions()))
    results.append(("Infinite loop prevention", test_infinite_loop_prevention()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Bug fixes working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
