Run Backend:
===========

```
cd server
pip install -r Requirements.txt
uvicorn Main:app --reload
```
Note: Main is the Python file (without .py)
<br>
And app is the FastAPI/Starlette application instance

Access WebSocket at: `ws://localhost:8000/ws/livefeed`

You can also run it as:

```
cd server
python Main.py
```

Run Frontend:
==============
```
cd dashboard
npm install
npm start
```

Open browser at: `http://localhost:3000`


Not Used
=========
Navigate to `http://127.0.0.1:8000/dashboard` in your browser to view the real-time dashboard.
