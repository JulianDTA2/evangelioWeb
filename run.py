# run.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import createApp

app = createApp()

if __name__ == '__main__':
    app.run(debug=True)
