# server_capi_stub.py (eksempel)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.post("/hooks/dm")
def dm():
    payload = request.json
    # map → contact/deal/events, enforce consent
    return jsonify({"ok": True})

@app.post("/capi/lead")
def capi_lead():
    body = request.json  # ensure event_id + fbp/fbc + hash(email/phone)
    # send to Meta CAPI (requests.post(...))
    return jsonify({"ok": True})
