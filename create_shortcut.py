"""
Create desktop shortcut for Student Admissions Manager.
Run this once to install the shortcut.
"""

import os
import sys

def create_windows_shortcut():
    """Create Windows desktop shortcut."""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Student Admissions.lnk")
        target = os.path.join(os.path.dirname(__file__), "run_as_admin.py")
        wDir = os.path.dirname(__file__)
        icon = os.path.join(wDir, "icon.ico") if os.path.exists(os.path.join(wDir, "icon.ico")) else sys.executable
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.Description = "Student Admissions Manager"
        shortcut.save()
        
        print(f"✓ Shortcut created on desktop: {path}")
        return True
        
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32", "winshell"])
        print("Packages installed. Please run this script again.")
        return False
    except Exception as e:
        print(f"Error creating Windows shortcut: {e}")
        return False

def create_linux_shortcut():
    """Create Linux desktop shortcut."""
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            desktop = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
        
        shortcut_path = os.path.join(desktop, "student-admissions.desktop")
        app_dir = os.path.dirname(__file__)
        
        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Student Admissions Manager
Comment=Manage student admissions
Exec={sys.executable} "{os.path.join(app_dir, 'main.py')}"
Path={app_dir}
Terminal=false
Categories=Education;Office;
"""
        
        with open(shortcut_path, 'w') as f:
            f.write(content)
        
        os.chmod(shortcut_path, 0o755)
        
        print(f"✓ Shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Error creating Linux shortcut: {e}")
        return False

def create_mac_shortcut():
    """Create macOS shortcut."""
    try:
        app_dir = os.path.dirname(__file__)
        script_path = os.path.join(os.path.expanduser("~"), "Desktop", "Student Admissions.command")
        
        content = f"""#!/bin/bash
cd "{app_dir}"
{sys.executable} main.py
"""
        
        with open(script_path, 'w') as f:
            f.write(content)
        
        os.chmod(script_path, 0o755)
        
        print(f"✓ Shortcut created: {script_path}")
        return True
        
    except Exception as e:
        print(f"Error creating Mac shortcut: {e}")
        return False

def main():
    print("=" * 60)
    print("Student Admissions Manager - Shortcut Installer")
    print("=" * 60)
    print()
    
    if sys.platform == 'win32':
        print("Creating Windows desktop shortcut...")
        success = create_windows_shortcut()
    elif sys.platform == 'darwin':
        print("Creating macOS shortcut...")
        success = create_mac_shortcut()
    else:
        print("Creating Linux shortcut...")
        success = create_linux_shortcut()
    
    if success:
        print()
        print("✓ Installation complete!")
        print("  You can now launch the application from your desktop.")
    else:
        print()
        print("✗ Installation failed.")
        print("  You can still run the application using: python main.py")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
