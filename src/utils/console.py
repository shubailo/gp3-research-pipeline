"""Console and terminal encoding utilities."""
import sys
import io

def configure_utf8_console() -> None:
    """Ensure standard output and standard error use UTF-8 on Windows without crashing."""
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, io.UnsupportedOperation, ValueError, OSError):
            pass
