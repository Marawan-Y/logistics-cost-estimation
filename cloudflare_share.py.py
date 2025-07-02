# working_share.py - Complete working solution
import subprocess
import sys
import os
import time
import socket
from pathlib import Path

def test_streamlit_import():
    """Test if streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        print("❌ Streamlit not installed!")
        print("Run: pip install streamlit")
        return False

def find_main_app():
    """Find the main app file"""
    possible_files = ['Overview.py', 'app.py', 'main.py', 'Home.py']
    for file in possible_files:
        if Path(file).exists():
            return file
    
    # Look for any .py file
    py_files = list(Path('.').glob('*.py'))
    if py_files:
        print(f"Found Python files: {[f.name for f in py_files]}")
        return py_files[0].name
    return None

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    print("🚀 STREAMLIT APP LAUNCHER")
    print("=" * 60)
    
    # Check streamlit installation
    if not test_streamlit_import():
        return
    
    # Find app file
    app_file = find_main_app()
    if not app_file:
        print("❌ No Python app file found!")
        print("Make sure you're in the right directory")
        return
    
    print(f"✅ Found app file: {app_file}")
    
    # Get IP
    ip = get_local_ip()
    port = 8080
    
    print(f"\n📍 Your IP: {ip}")
    print(f"🔌 Port: {port}")
    print(f"\n🌐 After app starts, access at:")
    print(f"   Local: http://localhost:{port}")
    print(f"   Network: http://{ip}:{port}")
    
    # Create batch file for easy sharing
    with open("RUN_APP.bat", "w") as f:
        f.write(f"@echo off\n")
        f.write(f"echo Starting Logistics Cost Calculator...\n")
        f.write(f"streamlit run {app_file} --server.port {port} --server.address 0.0.0.0\n")
        f.write(f"pause\n")
    
    print(f"\n📝 Created RUN_APP.bat for easy launching")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("1. Windows Firewall is blocking connections")
    print("2. You need admin rights to fix this")
    print("3. For now, use alternatives below")
    
    print("\n🔧 STARTING APP NOW...")
    print("-" * 60)
    
    # Start streamlit with direct command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        app_file,
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    try:
        # Run the command
        process = subprocess.Popen(cmd)
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if it's running
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = test_socket.connect_ex(('localhost', port))
        test_socket.close()
        
        if result == 0:
            print(f"\n✅ App is running at http://localhost:{port}")
            print("\n❌ BUT colleagues can't access due to firewall!")
            print("\n💡 SOLUTION: Use one of these methods:")
            print("\n1. SCREEN SHARING (Easiest):")
            print("   - Open Microsoft Teams")
            print("   - Start a meeting/call")
            print("   - Share your screen")
            print("   - Navigate the app while colleagues watch")
            
            print("\n2. EXPORT RESULTS:")
            print("   - Use the app yourself")
            print("   - Export results as Excel/PDF")
            print("   - Share files via Teams/Email")
            
            print("\n3. IT REQUEST:")
            print("   - Email IT: 'Need port 8080 opened for internal tool'")
            print("   - Business case: 'Saves X hours per week'")
            
            print("\n4. CLOUD DEPLOYMENT:")
            print("   - Deploy to Streamlit Cloud (free)")
            print("   - Visit: share.streamlit.io")
        else:
            print(f"\n❌ App failed to start on port {port}")
        
        # Keep running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping app...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Try running directly:")
        print(f"   streamlit run {app_file}")

if __name__ == "__main__":
    main()