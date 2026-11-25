"""Folder access for the Mac App Store build, which runs in Apple's App Sandbox.

A sandboxed app may only open folders the person picked in an Open dialog. To keep that access
after a restart, macOS hands out "security-scoped bookmarks", which we keep in settings.json.
Outside the sandbox (the free download, Windows, running from source) everything here is a no-op.
"""
import base64
import os
import pwd
import sys
from pathlib import Path

SANDBOXED = sys.platform == "darwin" and "APP_SANDBOX_CONTAINER_ID" in os.environ

# Inside the sandbox Path.home() is the app's container; dialogs should start in the real home.
REAL_HOME = Path(pwd.getpwuid(os.getuid()).pw_dir) if sys.platform != "win32" else Path.home()

_WITH_SECURITY_SCOPE_CREATE = 1 << 11   # NSURLBookmarkCreationWithSecurityScope
_WITH_SECURITY_SCOPE_RESOLVE = 1 << 10  # NSURLBookmarkResolutionWithSecurityScope
_open = {}                               # path -> NSURL we called startAccessing on


def can_read(path):
    """True if we may list this folder right now."""
    try:
        os.listdir(path)
        return True
    except OSError:
        return False


def remember(path, bookmarks):
    """Store a bookmark for a folder the person just picked. bookmarks: dict saved in settings."""
    if not SANDBOXED or not path:
        return
    from Foundation import NSURL
    url = NSURL.fileURLWithPath_(str(path))
    data, _err = url.bookmarkDataWithOptions_includingResourceValuesForKeys_relativeToURL_error_(
        _WITH_SECURITY_SCOPE_CREATE, None, None, None)
    if data is not None:
        bookmarks[str(path)] = base64.b64encode(bytes(data)).decode()


def restore(bookmarks):
    """Reopen every remembered folder. Drops bookmarks that no longer resolve; returns True if
    bookmarks changed (so the caller can save settings)."""
    if not SANDBOXED:
        return False
    from Foundation import NSURL, NSData
    changed = False
    for path, b64 in list(bookmarks.items()):
        if path in _open:
            continue
        raw = base64.b64decode(b64)
        url, stale, _err = NSURL.URLByResolvingBookmarkData_options_relativeToURL_bookmarkDataIsStale_error_(
            NSData.dataWithBytes_length_(raw, len(raw)), _WITH_SECURITY_SCOPE_RESOLVE, None, None, None)
        if url is None:
            # Cards are often just not plugged in; keep their bookmark for next time.
            if not path.startswith("/Volumes/"):
                del bookmarks[path]
                changed = True
            continue
        if url.startAccessingSecurityScopedResource():
            _open[path] = url
        if stale:
            remember(path, bookmarks)
            changed = True
    return changed


def covered(path):
    """True if path is inside a folder we hold access to (or we're not sandboxed)."""
    if not SANDBOXED:
        return True
    p = str(path)
    return any(p == root or p.startswith(root.rstrip("/") + "/") for root in _open) or can_read(p)


def reveal(path):
    """Show a file or folder in Finder (works inside the sandbox, unlike `open`)."""
    from AppKit import NSWorkspace
    from Foundation import NSURL
    NSWorkspace.sharedWorkspace().activateFileViewerSelectingURLs_([NSURL.fileURLWithPath_(str(path))])
