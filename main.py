import streamlit.web.cli as stcli
import sys
import os
import socket
import subprocess
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def open_firewall_port(port=8501):
    """Automatically open firewall port (requires admin rights)"""
    try:
        cmd = f'netsh advfirewall firewall add rule name="Streamlit Port {port}" dir=in action=allow protocol=TCP localport={port}'
        subprocess.run(cmd, shell=True, capture_output=True)
        print(f"✅ Firewall rule added for port {port}")
    except:
        print("⚠️  Could not automatically configure firewall. Please run as administrator.")

def main():
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent
    
    os.chdir(app_dir)
    
    # Get local IP
    local_ip = get_local_ip()
    
    print("🌐 Logistics Cost Calculator - Network Sharing")
    print("=" * 55)
    print(f"📍 Your IP Address: {local_ip}")
    print(f"🔗 Local URL: http://localhost:8501")
    print(f"🔗 Network URL: http://{local_ip}:8501")
    print("=" * 55)
    
    # Try to open firewall port
    open_firewall_port()
    
    # Configure streamlit for network access
    sys.argv = [
        "streamlit",
        "run",
        str(app_dir / "Overview.py"),
        "--server.address=0.0.0.0",  # Bind to all interfaces
        "--server.port=8501",
        "--server.headless=true",
        "--browser.serverAddress=localhost",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false"
    ]
    
    stcli.main()

if __name__ == "__main__":
    main()