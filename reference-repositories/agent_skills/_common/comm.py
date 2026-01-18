from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time, uuid

@dataclass
class AgentMessage:
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requires_response: bool = False
    priority: int = 0

class AgentCommunication:
    def __init__(self):
        self.inbox: Dict[str, List[AgentMessage]] = {}
        self.outbox: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []
    def send(self, msg: AgentMessage):
        # Allow dict or AgentMessage
        if isinstance(msg, dict):
            receiver = msg.get('to') or msg.get('receiver')
            am = AgentMessage(sender=msg.get('from','unknown'), receiver=receiver, message_type=msg.get('message_type','request'), content=msg.get('task') if 'task' in msg else msg.get('content', {}))
            msg = am
        self.inbox.setdefault(msg.receiver, []).append(msg)
        self.outbox.append(msg)
        self.message_history.append(msg)
    def receive(self, agent_id: str):
        msgs = self.inbox.get(agent_id, [])
        self.inbox[agent_id] = []
        return msgs
    def broadcast(self, sender: str, message_type: str, content: Dict[str, Any], receivers: List[str]):
        for r in receivers:
            self.send(AgentMessage(sender=sender, receiver=r, message_type=message_type, content=content))
