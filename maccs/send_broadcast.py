import sys
sys.path.append(".")
from maccs.maccs_client import MACCSClientV3

client = MACCSClientV3("manus_6", ".")
with open("maccs/broadcast_message.txt", "r") as f:
    message_text = f.read()
client.send_message("broadcast", "COORDINATION_INSTRUCTION", {"text": message_text})
client.close()

