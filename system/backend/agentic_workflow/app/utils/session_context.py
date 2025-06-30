from contextvars import ContextVar
from uuid import uuid4

session_state = ContextVar("session_state")