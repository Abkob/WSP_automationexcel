"""
Launcher that requests admin privileges on Windows.
"""

import sys
import os

def is_admin():
    """Check if running with admin privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script with admin privileges."""
    try:
        import ctypes
        
        if sys.platform == 'win32':
            script = os.path.join(os.path.dirname(__file__), 'main.py')
            
            # Request admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                f'"{script}"', 
                None, 
                1  # SW_SHOWNORMAL
            )
            sys.exit(0)
        else:
            # On Linux/Mac, just run normally
            import subprocess
            script = os.path.join(os.path.dirname(__file__), 'main.py')
            subprocess.run([sys.executable, script])
            sys.exit(0)
    except Exception as e:
        print(f"Failed to run as admin: {e}")
        # Fall back to running normally
        import subprocess
        script = os.path.join(os.path.dirname(__file__), 'main.py')
        subprocess.run([sys.executable, script])

if __name__ == "__main__":
    if sys.platform == 'win32' and not is_admin():
        run_as_admin()
    else:
        # Already admin or not Windows, run main
        import subprocess
        script = os.path.join(os.path.dirname(__file__), 'main.py')
        subprocess.run([sys.executable, script])
