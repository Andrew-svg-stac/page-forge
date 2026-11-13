"""Runtime notification helper copied into generated skills."""
from pathlib import Path
import sys

# Import shared notify module from skill-forge installation.
forge_notify = Path.home() / ".claude" / "skills" / "skill-forge" / "lib" / "notify.py"
if str(forge_notify.parent) not in sys.path:
    sys.path.insert(0, str(forge_notify.parent))

from notify import push, require_human  # type: ignore
