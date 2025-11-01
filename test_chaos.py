#!/usr/bin/env python3
"""
Chaos testing script to validate blue/green failover and error rate alerts
"""
import requests
import time
import subprocess
import sys

def run_command(cmd):
    """Execute shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_baseline():
    """Test baseline functionality"""
    print("🧪 Testing baseline functionality...")
    
    try:
        response = requests.get('http://localhost:8080/version', timeout=5)
        if response.status_code == 200:
            pool = response.headers.get('X-App-Pool', 'unknown')
            print(f"✅ Baseline test passed - Active pool: {pool}")
            return True
        else:
            print(f"❌ Baseline test failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Baseline test failed - Error: {e}")
        return False

def test_failover():
    """Test failover by stopping blue container"""
    print("\n🔄 Testing failover scenario...")
    
    # Stop blue container
    print("Stopping blue container...")
    success, stdout, stderr = run_command("docker compose stop app_blue")
    if not success:
        print(f"❌ Failed to stop blue container: {stderr}")
        return False
    
    time.sleep(2)  # Wait for failover
    
    # Test that green is now serving
    try:
        response = requests.get('http://localhost:8080/version', timeout=5)
        if response.status_code == 200:
            pool = response.headers.get('X-App-Pool', 'unknown')
            print(f"✅ Failover successful - Now serving from: {pool}")
            
            # Restart blue container
            print("Restarting blue container...")
            run_command("docker compose start app_blue")
            time.sleep(3)
            
            return True
        else:
            print(f"❌ Failover failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failover test failed - Error: {e}")
        # Ensure blue is restarted
        run_command("docker compose start app_blue")
        return False

def test_error_rate():
    """Test error rate alerts by stopping both containers briefly"""
    print("\n📈 Testing error rate alerts...")
    
    # Stop both containers to generate errors
    print("Stopping both containers to generate errors...")
    run_command("docker compose stop app_blue app_green")
    
    # Make requests that will fail
    error_count = 0
    for i in range(10):
        try:
            requests.get('http://localhost:8080/version', timeout=2)
        except:
            error_count += 1
        time.sleep(0.5)
    
    print(f"Generated {error_count} error requests")
    
    # Restart containers
    print("Restarting containers...")
    run_command("docker compose start app_blue app_green")
    time.sleep(5)
    
    # Verify recovery
    try:
        response = requests.get('http://localhost:8080/version', timeout=5)
        if response.status_code == 200:
            print("✅ Error rate test completed - Services recovered")
            return True
        else:
            print("❌ Services did not recover properly")
            return False
    except Exception as e:
        print(f"❌ Recovery failed: {e}")
        return False

def main():
    """Run all chaos tests"""
    print("🚀 Starting Blue/Green Chaos Testing")
    print("=" * 50)
    
    tests = [
        ("Baseline", test_baseline),
        ("Failover", test_failover),
        ("Error Rate", test_error_rate)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Check Slack for alerts.")
    else:
        print("\n⚠️  Some tests failed. Check logs and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()