import os
import uuid
import re
from flask import Flask, render_template, request, jsonify, redirect, session
from dotenv import load_dotenv
from llm import ask_llm
from search import web_search
from plugins import generate_graph, dns_lookup, ip_lookup, port_scan
from face_auth import capture_face, recognize_face
import PyPDF2

load_dotenv()

app = Flask(__name__)
app.secret_key = "shadow_secret_key"

app.config['SESSION_PERMANENT'] = False

sessions = {}

# =========================
# Helpers
# =========================

def extract_text_from_file(file):

    filename = file.filename.lower()

    if filename.endswith(".txt"):
        return file.read().decode("utf-8")

    elif filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    return ""


def save_message(session_id, role, content):

    if session_id not in sessions:
        sessions[session_id] = {
            "title": "New Chat",
            "messages": []
        }

    sessions[session_id]["messages"].append({
        "role": role,
        "content": content
    })


def build_conversation(session_id):

    if session_id not in sessions:
        return ""

    conversation = ""

    for msg in sessions[session_id]["messages"]:

        role = msg["role"]
        content = msg["content"]

        conversation += f"{role.upper()}: {content}\n"

    conversation += "ASSISTANT:"
    return conversation


# =========================
# FACE LOGIN
# =========================

@app.route("/face_login", methods=["POST"])
def face_login():

    data = request.get_json()

    image = data.get("image")

    name = recognize_face(image)

    if name:
        session["logged_in"] = True
        return jsonify({"success": True, "name": name})

    return jsonify({"success": False})


# =========================
# PASSWORD LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "shadow123":

            session["logged_in"] = True
            return redirect("/")

        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


# =========================
# REGISTER FACE
# =========================

@app.route("/register_face", methods=["POST"])
def register_face():

    data = request.get_json()

    username = data.get("username")
    image = data.get("image")

    if not username or not image:
        return jsonify({"success": False})

    result = capture_face(username, image)

    return jsonify({"success": result})


# =========================
# HOME
# =========================

@app.route("/")
def home():

    if not session.get("logged_in"):
        return redirect("/login")

    return render_template("index.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


# =========================
# CREATE SESSION
# =========================

@app.route("/api/session", methods=["POST"])
def create_session():

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "title": request.json.get("title", "New Chat"),
        "messages": []
    }

    return jsonify({
        "session_id": session_id
    })


# =========================
# GET ALL SESSIONS
# =========================

@app.route("/api/sessions", methods=["GET"])
def get_sessions():

    data = []

    for sid, sess in sessions.items():

        data.append({
            "id": sid,
            "title": sess["title"]
        })

    return jsonify({"sessions": data})


# =========================
# GET SESSION MESSAGES
# =========================

@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):

    if session_id not in sessions:
        return jsonify({"messages": []})

    return jsonify({
        "messages": sessions[session_id]["messages"]
    })


# =========================
# DELETE SESSION
# =========================

@app.route("/api/session/<session_id>", methods=["DELETE"])
def delete_session(session_id):

    if session_id in sessions:
        del sessions[session_id]

    return jsonify({"success": True})


# =========================
# MAIN MESSAGE ROUTE
# =========================

@app.route("/api/message", methods=["POST"])
def handle_message():

    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    text = request.form.get("text", "").strip()
    session_id = request.form.get("session_id")
    mode = request.form.get("mode", "chat").strip()

    lower_text = text.lower()
    parts = text.split()

    print("Incoming text:", text)
    print("Lower text:", lower_text)

    if not session_id:

        session_id = str(uuid.uuid4())

        sessions[session_id] = {
            "title": text[:30] if text else "New Chat",
            "messages": []
        }

    file = request.files.get("file")
    document_text = ""

    if file:
        document_text = extract_text_from_file(file)

    if text:
        save_message(session_id, "user", text)

    if sessions[session_id]["title"] == "New Chat" and text:
        sessions[session_id]["title"] = text[:40]

    # =========================
    # SEARCH MODE
    # =========================

    if mode == "search":

        results = web_search(text)

        if not results:
            reply = "No search results found."

        else:

            reply = ""

            for r in results:
                reply += f"{r['title']}\n{r['body']}\n{r['link']}\n\n"

        save_message(session_id, "assistant", reply)

        return jsonify({
            "session_id": session_id,
            "assistant": reply
        })


    # =========================
    # GRAPH PLUGIN
    # =========================

    if "plot" in lower_text or "graph" in lower_text:

        numbers = list(map(int, re.findall(r"\d+", text)))

        if numbers:

            graph_type = "line"

            if "bar" in lower_text:
                graph_type = "bar"
            elif "pie" in lower_text:
                graph_type = "pie"
            elif "scatter" in lower_text:
                graph_type = "scatter"

            image_path = generate_graph(numbers, graph_type)

            reply = f"Graph generated:\n\n![Graph]({image_path})"

            save_message(session_id, "assistant", reply)

            return jsonify({
                "session_id": session_id,
                "assistant": reply
            })


    # =========================
    # DNS LOOKUP
    # =========================

    if lower_text.startswith("dns ") and len(parts) >= 2:

        domain = parts[1]

        reply = dns_lookup(domain)

        save_message(session_id, "assistant", reply)

        return jsonify({
            "session_id": session_id,
            "assistant": reply
        })


    # =========================
    # PORT SCAN
    # =========================

    if lower_text.startswith("scan") and len(parts) >= 2:

        host = parts[1]

        reply = port_scan(host)

        save_message(session_id, "assistant", reply)

        return jsonify({
            "session_id": session_id,
            "assistant": reply
        })


    # =========================
    # RESEARCH MODE
    # =========================

    if mode == "research":

        reply = ask_llm(text, mode="research")


    # =========================
    # DOCUMENT MODE
    # =========================

    elif document_text:

        prompt = f"""
Answer strictly from this document.
If answer not found say you don't know.

DOCUMENT:
{document_text[:8000]}

QUESTION:
{text}
"""

        reply = ask_llm(prompt, mode="chat")


    # =========================
    # NORMAL CHAT
    # =========================

    else:

        history = sessions[session_id]["messages"][-6:]

        conversation_text = ""

        for msg in history:

            if msg["role"] == "user":
                conversation_text += f"User: {msg['content']}\n"

            else:
                conversation_text += f"Assistant: {msg['content']}\n"

        conversation_text += "Assistant:"

        reply = ask_llm(conversation_text, mode="chat")

    save_message(session_id, "assistant", reply)

    return jsonify({
        "session_id": session_id,
        "assistant": reply
    })


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)