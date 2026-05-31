from flask import Blueprint, Response
from app import csrf
import queue, time
from app.routes.auth import login_required


stream_bp  = Blueprint("stream", __name__)
csrf.exempt(stream_bp)
log_queue  = queue.Queue()


def log_stream():
    """Generator that yields SSE log lines to the browser."""
    while True:
        try:
            msg = log_queue.get(timeout=30)
            yield f"data: {msg}\n\n"
        except queue.Empty:
            yield "data: ping\n\n"


@stream_bp.route("/logs")
@login_required
def logs():
    return Response(log_stream(), mimetype="text/event-stream")
