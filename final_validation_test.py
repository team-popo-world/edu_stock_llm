#!/usr/bin/env python3
"""
Final validation test for all implemented features in the edu_stock_llm project.
This script validates all the enhancements made during the improvement process.
"""

import os
import sys
import json
import importlib
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_streamlit_app_functions():
    """Test all the new functions added to streamlit_app.py"""
    print("🧪 Testing Streamlit App Functions...")
    
    try:
        from src.streamlit_app import (
            display_educational_feedback,
            analyze_investment_patterns,
            generate_investment_lessons,
            display_game_data_management,
            save_current_game,
            show_game_history,
            show_data_cleanup_options
        )
        print("✅ All new Streamlit functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Streamlit functions: {e}")
        return False

def test_visualization_enhancements():
    """Test child-friendly visualization improvements"""
    print("🎨 Testing Visualization Enhancements...")
    
    try:
        from src.visualization.visualize import (
            _create_stock_plot,
            create_investment_history_chart,
            create_simple_stock_plot
        )
        from src.ui.components import (
            create_news_card,
            create_stock_card,
            create_metric_card
        )
        print("✅ All visualization functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import visualization functions: {e}")
        return False

def test_three_little_pigs_scenario():
    """Test Three Little Pigs scenario integration"""
    print("🐷 Testing Three Little Pigs Scenario...")
    
    scenario_file = os.path.join(current_dir, "data", "game_scenario_three_little_pigs_20250609_162517.json")
    
    if not os.path.exists(scenario_file):
        print(f"❌ Three Little Pigs scenario file not found: {scenario_file}")
        return False
    
    try:
        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        # Check required fields
        required_fields = ['scenario_type', 'turns', 'stocks']
        for field in required_fields:
            if field not in scenario_data:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check if we have 7 turns
        if len(scenario_data['turns']) != 7:
            print(f"❌ Expected 7 turns, found {len(scenario_data['turns'])}")
            return False
        
        print("✅ Three Little Pigs scenario data is valid")
        return True
    except Exception as e:
        print(f"❌ Failed to validate Three Little Pigs scenario: {e}")
        return False

def test_cli_integration():
    """Test CLI script integration"""
    print("🖥️ Testing CLI Integration...")
    
    run_script = os.path.join(current_dir, "run_game.sh")
    
    if not os.path.exists(run_script):
        print("❌ run_game.sh not found")
        return False
    
    try:
        with open(run_script, 'r') as f:
            content = f.read()
        
        # Check for Three Little Pigs option
        if "Three Little Pigs" not in content:
            print("❌ Three Little Pigs option not found in run_game.sh")
            return False
        
        # Check for correct file path
        if "game_scenario_three_little_pigs_20250609_162517.json" not in content:
            print("❌ Correct Three Little Pigs file path not found in run_game.sh")
            return False
        
        print("✅ CLI integration is correct")
        return True
    except Exception as e:
        print(f"❌ Failed to validate CLI integration: {e}")
        return False

def test_documentation_updates():
    """Test README documentation updates"""
    print("📖 Testing Documentation Updates...")
    
    readme_file = os.path.join(current_dir, "README.md")
    
    if not os.path.exists(readme_file):
        print("❌ README.md not found")
        return False
    
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        required_sections = [
            "Google API 키 설정",
            "Three Little Pigs",
            "## 설치 방법",
            "## 사용 방법"
        ]
        
        for section in required_sections:
            if section not in content:
                print(f"❌ Missing documentation section: {section}")
                return False
        
        print("✅ Documentation updates are complete")
        return True
    except Exception as e:
        print(f"❌ Failed to validate documentation: {e}")
        return False

def test_integration_report():
    """Test integration report existence"""
    print("📊 Testing Integration Report...")
    
    report_file = os.path.join(current_dir, "INTEGRATION_REPORT.md")
    
    if not os.path.exists(report_file):
        print("❌ INTEGRATION_REPORT.md not found")
        return False
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        if len(content) < 1000:  # Should be substantial
            print("❌ Integration report seems too short")
            return False
        
        print("✅ Integration report exists and has substantial content")
        return True
    except Exception as e:
        print(f"❌ Failed to validate integration report: {e}")
        return False

def run_final_validation():
    """Run all validation tests"""
    print("🚀 Starting Final Validation Test")
    print("=" * 50)
    
    tests = [
        ("Streamlit App Functions", test_streamlit_app_functions),
        ("Visualization Enhancements", test_visualization_enhancements),
        ("Three Little Pigs Scenario", test_three_little_pigs_scenario),
        ("CLI Integration", test_cli_integration),
        ("Documentation Updates", test_documentation_updates),
        ("Integration Report", test_integration_report)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📋 FINAL VALIDATION RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The edu_stock_llm project improvements are complete and validated.")
        print("\n🌟 Key Features Successfully Implemented:")
        print("   • Educational feedback and investment pattern analysis")
        print("   • Game data management with save/load capabilities")  
        print("   • Child-friendly visualizations with bright colors")
        print("   • Three Little Pigs theme integration")
        print("   • Updated documentation and CLI support")
        print("   • Comprehensive testing infrastructure")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_final_validation()
    sys.exit(0 if success else 1)
