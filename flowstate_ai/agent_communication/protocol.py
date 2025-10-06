import enum
import json
from typing import Dict, Any, Optional

class MessageType(enum.Enum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    EVENT = "EVENT"
    ERROR = "ERROR"

class AgentMessage:
    def __init__(self, 
                 sender_id: str, 
                 receiver_id: str, 
                 msg_type: MessageType, 
                 content: Dict[str, Any], 
                 message_id: Optional[str] = None, 
                 in_response_to: Optional[str] = None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.msg_type = msg_type
        self.content = content
        self.message_id = message_id
        self.in_response_to = in_response_to

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "msg_type": self.msg_type.value,
            "content": self.content,
            "message_id": self.message_id,
            "in_response_to": self.in_response_to
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AgentMessage':
        msg_type = MessageType(data["msg_type"])
        return AgentMessage(
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            msg_type=msg_type,
            content=data["content"],
            message_id=data.get("message_id"),
            in_response_to=data.get("in_response_to")
        )

    @staticmethod
    def from_json(json_str: str) -> 'AgentMessage':
        data = json.loads(json_str)
        return AgentMessage.from_dict(data)

# Standardized message structure example:
# {
#   "sender_id": "agent_123",
#   "receiver_id": "agent_456",
#   "msg_type": "REQUEST",
#   "content": {"task": "fetch_data", "params": {"url": "http://example.com"}},
#   "message_id": "msg_001",
#   "in_response_to": null
# }

# Protocol utility functions

def create_request(sender_id: str, receiver_id: str, content: Dict[str, Any], message_id: str) -> AgentMessage:
    return AgentMessage(sender_id, receiver_id, MessageType.REQUEST, content, message_id)

def create_response(sender_id: str, receiver_id: str, content: Dict[str, Any], message_id: str, in_response_to: str) -> AgentMessage:
    return AgentMessage(sender_id, receiver_id, MessageType.RESPONSE, content, message_id, in_response_to)

def create_event(sender_id: str, receiver_id: str, content: Dict[str, Any], message_id: str) -> AgentMessage:
    return AgentMessage(sender_id, receiver_id, MessageType.EVENT, content, message_id)

def create_error(sender_id: str, receiver_id: str, content: Dict[str, Any], message_id: str, in_response_to: Optional[str] = None) -> AgentMessage:
    return AgentMessage(sender_id, receiver_id, MessageType.ERROR, content, message_id, in_response_to)
