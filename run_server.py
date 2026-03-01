import sys
import os

# Set working directory to project root
os.chdir(r"C:\Users\User\Desktop\downloads-warden")
sys.path.insert(0, r"C:\Users\User\Desktop\downloads-warden")

from src.server import mcp
mcp.run()
