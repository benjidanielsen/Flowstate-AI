#!/usr/bin/env python3
"""
Test script to verify Unicode/emoji logging works correctly
Run this on Windows to verify the fix works
"""
import sys
import logging
import platform
from datetime import datetime

# Apply the UTF-8 fix (same as in our fixed files)
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("UnicodeTest")

def main():
    """Test emoji logging"""
    print("=" * 70)
    print(f"Testing Unicode/Emoji Logging on {platform.system()}")
    print("=" * 70)
    print()
    
    # Test all emojis that were failing in the error logs
    test_emojis = [
        ("✅", "Check mark - Dashboard initialized"),
        ("🔄", "Refresh - Monitoring loop started"),
        ("❌", "Cross mark - Error occurred"),
        ("🚀", "Rocket - Starting application"),
        ("🪟", "Window - Platform detection"),
        ("🐍", "Python - Python version"),
        ("📊", "Chart - Dashboard available"),
        ("🔌", "Plug - Client connected"),
        ("🔧", "Wrench - Logging initialized"),
        ("💓", "Heart - Heartbeat received"),
        ("⚡", "Lightning - High priority"),
        ("🎯", "Target - Mission objectives"),
        ("🧠", "Brain - AI intelligence"),
        ("🤖", "Robot - AI agent"),
    ]
    
    print("Testing emoji logging:")
    print("-" * 70)
    
    all_passed = True
    for emoji, description in test_emojis:
        try:
            logger.info(f"{emoji} {description}")
            print(f"  ✓ {emoji} - OK")
        except UnicodeEncodeError as e:
            print(f"  ✗ {emoji} - FAILED: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ✗ {emoji} - ERROR: {e}")
            all_passed = False
    
    print("-" * 70)
    print()
    
    if all_passed:
        print("✅ SUCCESS! All emoji characters logged correctly.")
        print()
        print("The Unicode encoding fix is working properly on your system.")
        return 0
    else:
        print("❌ FAILURE! Some emoji characters failed to log.")
        print()
        print("The Unicode encoding fix may not be working correctly.")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
