import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    try:
        # Change to the scripts directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(script_dir, "gemini_multimodal_app.py")
        
        print("🚀 Starting Streamlit application...")
        print("📱 The app will open in your default web browser")
        print("🛑 Press Ctrl+C to stop the application")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    print("🤖 Gemini Multimodal Content Generator Setup")
    print("=" * 50)
    
    # Install requirements
    print("📦 Installing requirements...")
    if not install_requirements():
        print("❌ Failed to install requirements. Please install manually:")
        print("pip install streamlit google-generativeai gtts")
        return
    
    print("\n" + "=" * 50)
    print("🎯 Setup Instructions:")
    print("1. Get your Google Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. The application will start in your web browser")
    print("3. Enter your API key in the sidebar")
    print("4. Start generating content!")
    print("=" * 50)
    
    input("\n⏳ Press Enter to start the application...")
    
    # Run the Streamlit app
    run_streamlit_app()

if __name__ == "__main__":
    main()
