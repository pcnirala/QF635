Needs:
fastapi
uvicorn

run backend:
===============
cd backend
uvicorn main:app --reload

Access WebSocket at: ws://localhost:8000/ws/ticks

Run Frontend:
==============
cd dashboard
npm install
npm start

Open browser at: http://localhost:3000




Not used
++++++++++++++
Navigate to http://127.0.0.1:8000/dashboard in your browser to view the real-time dashboard.

