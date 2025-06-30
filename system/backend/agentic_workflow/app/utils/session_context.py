from contextvars import ContextVar

session_state: ContextVar[str] = ContextVar("session_state", default="")
