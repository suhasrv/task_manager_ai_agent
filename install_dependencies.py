#!/usr/bin/env python3
"""Install all required dependencies"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=" * 60)
    print("Installing Required Dependencies")
    print("=" * 60)
    
    # Core dependencies first
    core_packages = [
        "fastapi==0.115.0",
        "uvicorn[standard]==0.30.0",
        "streamlit==1.51.0",
        "python-dotenv==1.0.0",
        "httpx==0.28.0",
        "requests==2.32.3",
        "pydantic==2.11.7",
        "pydantic-settings==2.3.0",
    ]
    
    print("\n1. Installing Core Dependencies...")
    for package in core_packages:
        print(f"   Installing {package}...")
        if install_package(package):
            print(f"   ✅ {package.split('==')[0]}")
        else:
            print(f"   ❌ Failed: {package.split('==')[0]}")
    
    # Database dependencies
    db_packages = [
        "supabase==2.24.0",
        "chromadb==1.3.5",
        "asyncpg==0.30.0",
    ]
    
    print("\n2. Installing Database Dependencies...")
    for package in db_packages:
        print(f"   Installing {package}...")
        if install_package(package):
            print(f"   ✅ {package.split('==')[0]}")
        else:
            print(f"   ❌ Failed: {package.split('==')[0]}")
    
    # AI/LLM dependencies
    ai_packages = [
        "langchain",
        "langchain-openai",
        "langchain-anthropic",
        "openai==1.51.1",
        "anthropic==0.31.0",
    ]
    
    print("\n3. Installing AI/LLM Dependencies...")
    for package in ai_packages:
        print(f"   Installing {package}...")
        if install_package(package):
            print(f"   ✅ {package.split('==')[0]}")
        else:
            print(f"   ❌ Failed: {package.split('==')[0]}")
    
    # Utilities
    util_packages = [
        "loguru==0.7.2",
        "APScheduler==3.11.1",
        "python-dateutil==2.8.2",
        "pytz==2024.1",
    ]
    
    print("\n4. Installing Utility Dependencies...")
    for package in util_packages:
        print(f"   Installing {package}...")
        if install_package(package):
            print(f"   ✅ {package.split('==')[0]}")
        else:
            print(f"   ❌ Failed: {package.split('==')[0]}")
    
    print("\n" + "=" * 60)
    print("✅ Installation Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify installation: python -c 'import uvicorn, streamlit; print(\"OK\")'")
    print("2. Start backend: python -m uvicorn backend.main:app --reload")
    print("3. Start frontend: streamlit run frontend/app.py")

if __name__ == "__main__":
    main()


