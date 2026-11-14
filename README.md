# CampusFlow — Agentic AI Assistant for Multi-Step Campus Service Workflows

A student project prototype built with Python, Flask, HTML, CSS, JavaScript and SQLite.

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open Command Prompt in the `agentic_campus_assistant` folder.
4. Run:
   ```bash
   py -m venv venv
   venv\\Scripts\\activate
   pip install -r requirements.txt
   py app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

If `py` is unavailable, use `python` instead.

## Demo prompts
- `Book the computer lab tomorrow at 10 AM` — the seeded demo schedule makes 10 AM unavailable; the agent checks and reserves 11 AM if free.
- `The classroom projector is not working. Register a complaint.`
- `Check my attendance percentage` — returns clearly labelled sample attendance of 82%.
- `Submit a leave application for tomorrow`
- `Reserve Introduction to Python Programming from the library`

## What the prototype demonstrates
- Goal decomposition
- Tool selection
- Service execution
- Result observation
- Failure-based replanning (lab slot conflict)
- Human escalation (unrecognized request or no alternative slot)
- SQLite request log
- Rule-based baseline comparison (simple keyword routing versus multi-stage agent workflow)

## Important limitations
This is a simulated academic prototype. It is NOT connected to LPU systems, real attendance records, real room schedules, official leave approval, or the real library catalogue. Attendance and catalogue information are sample data. Do not enter sensitive personal information.

## Suggested team responsibilities
- Member 1: agent workflow, backend and testing
- Member 2: frontend, API integration and demo
- Member 3: documentation, PPT, test cases and screenshots

## Before submission
- Run every demo prompt.
- Take screenshots of the interface and agent trace.
- Include architecture and workflow diagrams in the report.
- Explain which parts are simulated and what would be needed for real deployment.
