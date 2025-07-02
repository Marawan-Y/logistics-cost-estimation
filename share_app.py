# share_app.py - Quick network sharing script
import socket
import subprocess
import sys
import webbrowser
import time
import threading

def get_local_ip():
    """Get local IP address automatically"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return socket.gethostbyname(socket.gethostname())

def main():
    print("🌐 Logistics Cost Calculator - Network Sharing")
    print("=" * 55)
    
    # Get IP and port
    local_ip = get_local_ip()
    port = 8501
    
    print(f"📍 Your IP Address: {local_ip}")
    print(f"🔗 Share this URL with your colleagues:")
    print(f"   http://{local_ip}:{port}")
    print()
    print("💡 Instructions for colleagues:")
    print("   1. Make sure you're on the same network")
    print(f"   2. Open browser and go to: http://{local_ip}:{port}")
    print("   3. Bookmark the URL for future use")
    print()
    print("🚀 Starting application...")
    print("❌ Close this window to stop sharing")
    print("-" * 55)
    
    # Open browser for host after delay
    def open_browser():
        time.sleep(3)
        webbrowser.open(f"http://localhost:{port}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Streamlit with network access
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "Overview.py",
            "--server.address=0.0.0.0",
            f"--server.port={port}",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Sharing stopped")

if __name__ == "__main__":
    main()