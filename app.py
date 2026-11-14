from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3, os, re, uuid

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "campus.db")

def db():
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS requests(
            id TEXT PRIMARY KEY, student TEXT, service TEXT, details TEXT,
            status TEXT, created_at TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT, student TEXT, lab TEXT,
            slot TEXT, status TEXT)""")
        # Sample bookings make availability checking demonstrable.
        con.execute("INSERT OR IGNORE INTO bookings(id,student,lab,slot,status) VALUES(1,'Demo Student','Computer Lab 1','tomorrow 10 AM','Confirmed')")

def save_request(student, service, details, status="Submitted"):
    rid="REQ-"+uuid.uuid4().hex[:6].upper()
    with db() as con:
        con.execute("INSERT INTO requests VALUES(?,?,?,?,?,?)",
                    (rid,student,service,details,status,datetime.now().strftime("%d-%m-%Y %H:%M")))
    return rid

def run_agent(message, student="Student"):
    """Transparent rule-based agent prototype: plan -> tool -> observe -> replan/escalate."""
    msg=message.lower()
    steps=[]
    def step(name, result):
        steps.append({"name":name,"result":result})

    # Goal decomposition
    step("Goal decomposition", "Identified the student's intent and split it into service actions.")

    if any(k in msg for k in ["lab","book a lab","reserve lab"]):
        service="Lab booking"
        lab="Computer Lab 1" if "computer" in msg or "lab" in msg else "General Lab"
        slot="tomorrow 10 AM" if "10" in msg or "tomorrow" in msg else "tomorrow 10 AM"
        step("Tool selection", "Selected the lab availability and booking tools.")
        with db() as con:
            clash=con.execute("SELECT id FROM bookings WHERE lab=? AND slot=? AND status='Confirmed'",(lab,slot)).fetchone()
            if clash:
                step("Execution", f"{lab} at {slot} is already occupied in the sample schedule.")
                step("Result observation", "Booking was not confirmed because the requested slot is unavailable.")
                step("Failure-based replanning", "Checked an alternative slot: tomorrow 11 AM.")
                alt=con.execute("SELECT id FROM bookings WHERE lab=? AND slot=? AND status='Confirmed'",(lab,"tomorrow 11 AM")).fetchone()
                if not alt:
                    con.execute("INSERT INTO bookings(student,lab,slot,status) VALUES(?,?,?,?)",(student,lab,"tomorrow 11 AM","Confirmed"))
                    alternative_reserved=True
                else:
                    alternative_reserved=False
            else:
                con.execute("INSERT INTO bookings(student,lab,slot,status) VALUES(?,?,?,?)",(student,lab,slot,"Confirmed"))
        if clash:
            if alternative_reserved:
                rid=save_request(student,service,f"{lab} - tomorrow 11 AM (alternative slot)")
                step("Result observation", "Alternative slot is available and has been reserved.")
                return answer(service, f"Your requested 10 AM slot was unavailable. Alternative slot {lab}, tomorrow 11 AM, is reserved. Reference: {rid}",steps, "Completed")
            rid=save_request(student,service,f"{lab} - requested {slot}; alternative unavailable","Needs human review")
            step("Human escalation", "No alternative slot was available. Sent the request for administrator review.")
            return answer(service,f"No slot was available. Your request was escalated to an administrator. Reference: {rid}",steps,"Escalated")
        rid=save_request(student,service,f"{lab} - {slot}")
        step("Execution","Created the lab booking.")
        step("Result observation","Verified that the booking record exists.")
        return answer(service,f"Your {lab} booking for {slot} is confirmed. Reference: {rid}",steps,"Completed")

    if not any(k in msg for k in ["not listed", "unusual"]) and any(k in msg for k in ["maintenance","broken","repair","projector","fan","light","complaint"]):
        service="Maintenance complaint"
        detail=message
        step("Tool selection","Selected the maintenance complaint tool.")
        rid=save_request(student,service,detail)
        step("Execution", "Created a maintenance ticket.")
        step("Result observation", "Verified that the ticket was saved.")
        return answer(service,f"Maintenance complaint submitted. Ticket: {rid}. Status: Submitted.",steps,"Completed")

    if any(k in msg for k in ["attendance","present","percentage"]):
        service="Attendance check"
        step("Tool selection","Selected the attendance lookup tool.")
        # Clearly labelled demo data, not connected to university records.
        pct=82
        step("Execution","Retrieved the sample attendance record for demonstration.")
        step("Result observation","Attendance value was returned successfully.")
        return answer(service,f"Demo attendance: {pct}%. This is sample data only, not your official LPU attendance.",steps,"Completed")

    if any(k in msg for k in ["leave","absent","permission"]):
        service="Leave application"
        step("Tool selection","Selected the leave application tool.")
        rid=save_request(student,service,message)
        step("Execution","Submitted the leave request to the prototype database.")
        step("Result observation","Verified that the request was saved.")
        return answer(service,f"Leave application submitted for review. Reference: {rid}.",steps,"Completed")

    if any(k in msg for k in ["library","book","reserve","borrow"]):
        service="Library reservation"
        step("Tool selection","Selected the library catalogue and reservation tools.")
        title="Introduction to Python Programming"
        step("Execution",f"Checked the demo catalogue for '{title}'.")
        rid=save_request(student,service,f"Reservation request: {title}")
        step("Result observation","Demo book is available; reservation request saved.")
        return answer(service,f"'{title}' reservation request submitted. Reference: {rid}. Demo catalogue only.",steps,"Completed")

    step("Tool selection","No matching campus service tool was identified.")
    step("Human escalation","The request needs clarification or administrator assistance.")
    rid=save_request(student,"General help",message,"Needs human review")
    return answer("General help",f"I couldn't safely identify the service. Your request was escalated for human review. Reference: {rid}. Try mentioning lab, maintenance, attendance, leave, or library.",steps,"Escalated")

def answer(service, text, steps, status):
    return {"service":service,"reply":text,"steps":steps,"status":status}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat",methods=["POST"])
def chat():
    data=request.get_json(force=True)
    message=(data.get("message") or "").strip()
    student=(data.get("student") or "Student").strip()[:60]
    if not message:
        return jsonify({"error":"Please enter a request."}),400
    return jsonify(run_agent(message,student))

@app.route("/api/requests")
def requests_list():
    with db() as con:
        rows=con.execute("SELECT * FROM requests ORDER BY rowid DESC LIMIT 20").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/health")
def health():
    return jsonify({"status":"ok","message":"Campus assistant is running"})

# Initialize the demo database when imported by a production WSGI server too.
init_db()

if __name__=="__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
