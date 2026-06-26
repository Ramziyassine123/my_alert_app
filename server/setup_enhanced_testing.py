# ServerSide/setup_enhanced_testing.py

import sys
import subprocess
import importlib.util
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        ('websocket-client', 'websocket'),
        ('requests', 'requests'),
        ('psutil', 'psutil'),  # Optional for system monitoring
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {package_name} is missing")

    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✓ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {package}")
                return False

    return True


def setup_file_structure():
    """Ensure required files are in place"""
    current_dir = Path(__file__).parent

    # Core required files (must exist)
    core_required_files = [
        'network_condition_simulator.py',
        'websocket_performance_test.py',
        'longpolling_performance_test.py',
        'firebase_performance_test.py',
        'unified_performance_runner.py',
        'enhanced_performance_report.py'
    ]

    # Optional files (nice to have but not critical)
    optional_files = [
        'alerts/performance_tests.py',
        'setup_enhanced_testing.py'
    ]

    missing_core_files = []
    missing_optional_files = []

    # Check core files
    for file_path in core_required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            missing_core_files.append(file_path)
            print(f"✗ {file_path} is missing")

    # Check optional files
    for file_path in optional_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists (optional)")
        else:
            missing_optional_files.append(file_path)
            print(f"⚠ {file_path} is missing (optional)")

    if missing_core_files:
        print(f"\nCRITICAL: Missing core files: {missing_core_files}")
        return False

    if missing_optional_files:
        print(f"\nINFO: Missing optional files: {missing_optional_files}")
        print("This is OK - the system will work without these files.")

    return True


def test_imports():
    """Test that all modules can be imported correctly"""
    test_modules = [
        'network_condition_simulator',
        'websocket_performance_test',
        'longpolling_performance_test',
        'firebase_performance_test',
        'enhanced_performance_report'
    ]

    import_errors = []

    for module_name in test_modules:
        try:
            importlib.import_module(module_name)
            print(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            import_errors.append((module_name, str(e)))
            print(f"✗ Failed to import {module_name}: {e}")

    if import_errors:
        print(f"\nImport errors found:")
        for module, error in import_errors:
            print(f"  {module}: {error}")
        return False

    return True


def create_sample_config():
    """Create a sample test configuration file"""
    config_content = """{
    "technologies": ["websocket", "longpolling", "firebase"],
    "duration": 30,
    "message_count": 50,
    "concurrent_clients": 25,
    "max_connections": 100,
    "token_count": 25,
    "test_description": "Enhanced performance test for research analysis",
    "network_profiles": ["perfect", "local_wifi", "good_mobile", "poor_mobile", "satellite"],
    "output_formats": ["html", "csv", "json"],
    "generate_reports": true,
    "save_raw_data": true
}"""

    config_file = Path(__file__).parent / 'test_config.json'

    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✓ Created sample configuration: {config_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration file: {e}")
        return False


def run_quick_test():
    """Run a quick test to verify everything works"""
    print("\nRunning quick verification test...")

    try:
        from network_condition_simulator import NetworkConditionSimulator, EnhancedPerformanceMetrics

        # Test network simulator
        simulator = NetworkConditionSimulator()
        print("✓ Network simulator initialized")

        # Test metrics collection
        metrics = EnhancedPerformanceMetrics('test')
        metrics.start_test('perfect')
        metrics.record_connection_time(50.0)
        metrics.record_message_latency(25.0)
        metrics.record_success()
        metrics.end_test()

        result = metrics.calculate_comprehensive_metrics()
        print(f"✓ Metrics collection works - Sample latency: {result['message_latency_ms']:.1f}ms")

        return True

    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        return False


def check_django_integration():
    """Check if this is a Django project and suggest integration"""
    current_dir = Path(__file__).parent

    # Check for Django files
    django_files = ['manage.py', 'settings.py']
    django_indicators = []

    for file_name in django_files:
        if (current_dir / file_name).exists():
            django_indicators.append(file_name)

    # Also check subdirectories for settings.py
    for subdir in current_dir.iterdir():
        if subdir.is_dir() and (subdir / 'settings.py').exists():
            django_indicators.append(f"{subdir.name}/settings.py")

    if django_indicators:
        print(f"\n📋 Django project detected (found: {', '.join(django_indicators)})")
        print("💡 Suggestions for Django integration:")
        print("   • Run tests with: python performance_tests.py")
        print("   • Start Django server: python manage.py runserver 8001")
        print("   • Consider creating Django management commands for easier integration")
        return True

    return False


def run_integration_test():
    """Test if the system can run a basic performance test"""
    print("\nRunning integration test...")

    try:
        # Import the main test runner
        from performance_tests import main

        print("✓ Main test runner can be imported")
        print("💡 To run full tests: python performance_tests.py")
        print("💡 To run individual tests:")
        print("   • python websocket_performance_test.py")
        print("   • python longpolling_performance_test.py")
        print("   • python firebase_performance_test.py")

        return True

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        print("💡 Try running: python performance_tests.py")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("ENHANCED PERFORMANCE TESTING SETUP")
    print("=" * 60)

    success = True

    print("\n1. Checking dependencies...")
    if not check_dependencies():
        success = False

    print("\n2. Checking file structure...")
    if not setup_file_structure():
        success = False

    print("\n3. Testing imports...")
    if not test_imports():
        success = False

    print("\n4. Creating sample configuration...")
    if not create_sample_config():
        success = False

    print("\n5. Running verification test...")
    if not run_quick_test():
        success = False

    print("\n6. Checking Django integration...")
    check_django_integration()

    print("\n7. Testing integration...")
    run_integration_test()

    print("\n" + "=" * 60)
    if success:
        print("✅ SETUP COMPLETED SUCCESSFULLY")
        print("\n🚀 You can now run enhanced performance tests:")
        print("   📊 Full test suite:     python performance_tests.py")
        print("   🕷️ WebSocket only:      python websocket_performance_test.py")
        print("   🔄 Long Polling only:   python longpolling_performance_test.py")
        print("   🔔 Firebase only:       python firebase_performance_test.py")
        print("   📈 Unified runner:      python unified_performance_runner.py")
        print("\n📋 Configuration:")
        print("   • Test config:          test_config.json")
        print("   • Reports will be generated automatically")
        print("\n🎯 Quick Start:")
        print("   1. Start Django server: python manage.py runserver 8001")
        print("   2. Run tests:           python performance_tests.py")
        print("   3. Check reports:       *.html and *.csv files")
    else:
        print("⚠️ SETUP COMPLETED WITH WARNINGS")
        print("\n🔧 The core system is functional, but consider:")
        print("   • Fixing any import errors above")
        print("   • Installing missing optional dependencies")
        print("\n✅ You can still run tests:")
        print("   python performance_tests.py")

    print("=" * 60)

    return success


if __name__ == "__main__":
    main()
