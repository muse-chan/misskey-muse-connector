#!/usr/bin/env python3
"""CLI helper for the custom Misskey Otnc Dev connector.

All endpoints are POST with a JSON body, per the Misskey API.
The access token is applied as an Authorization Bearer header through the
dynamic credential surrogate. The real credential never appears here.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_response_body

HOST = "misskey.otnc.dev"
BASE = f"https://{HOST}/api"
CREDENTIAL = "custom.misskey-otnc-dev"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(endpoint, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE}/{endpoint}",
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 MuseMisskeyConnector/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )
    add_surrogate_to_request(request, CREDENTIAL, allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=60) as response:
            raw = read_response_body(response)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"http_status": exc.code, "body": raw}, ensure_ascii=False))
        raise SystemExit(1)
    if not raw:
        print(json.dumps({"ok": True}))
        return
    print(json.dumps(json.loads(raw.decode("utf-8")), ensure_ascii=False, indent=2))


def upload_file(path, name=None):
    import mimetypes
    import os
    import uuid

    boundary = f"----muse{uuid.uuid4().hex}"
    filename = os.path.basename(path)
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(path, "rb") as fh:
        content = fh.read()
    parts = []
    if name:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{name}\r\n".encode("utf-8")
        )
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {mime}\r\n\r\n".encode("utf-8")
        + content + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    request = urllib.request.Request(
        f"{BASE}/drive/files/create",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 MuseMisskeyConnector/1.0",
            "Accept": "application/json",
        },
        method="POST",
    )
    add_surrogate_to_request(request, CREDENTIAL, allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=60) as response:
            raw = read_response_body(response)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"http_status": exc.code, "body": raw}, ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps(json.loads(raw.decode("utf-8")), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Misskey Otnc Dev connector helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="POST /api/i, the authenticated account")
    sub.add_parser("meta", help="POST /api/meta, instance metadata")

    p = sub.add_parser("local-timeline", help="POST /api/notes/local-timeline")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("home-timeline", help="POST /api/notes/timeline")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("global-timeline", help="POST /api/notes/global-timeline")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("hybrid-timeline", help="POST /api/notes/hybrid-timeline")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("notifications", help="POST /api/i/notifications")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("note", help="POST /api/notes/create")
    p.add_argument("--text", required=True)
    p.add_argument("--reply-id")
    p.add_argument("--renote-id")
    p.add_argument("--visibility", default="public",
                   choices=["public", "home", "followers", "specified"])

    p = sub.add_parser("react", help="POST /api/notes/reactions/create")
    p.add_argument("--note-id", required=True)
    p.add_argument("--reaction", required=True)

    p = sub.add_parser("follow", help="POST /api/following/create")
    p.add_argument("--user-id", required=True)

    p = sub.add_parser("show-user", help="POST /api/users/show")
    p.add_argument("--username", required=True)

    p = sub.add_parser("user-notes", help="POST /api/users/notes")
    p.add_argument("--user-id", required=True)
    p.add_argument("--limit", type=int, default=30)

    p = sub.add_parser("show-note", help="POST /api/notes/show")
    p.add_argument("--note-id", required=True)

    p = sub.add_parser("upload", help="POST /api/drive/files/create")
    p.add_argument("--file", required=True)
    p.add_argument("--name")

    p = sub.add_parser("update-profile", help="POST /api/i/update")
    p.add_argument("--name")
    p.add_argument("--description")
    p.add_argument("--avatar-id")
    p.add_argument("--banner-id")

    args = parser.parse_args()

    if args.command == "me":
        call("i", {})
    elif args.command == "meta":
        call("meta", {"detail": False})
    elif args.command == "local-timeline":
        call("notes/local-timeline", {"limit": args.limit})
    elif args.command == "home-timeline":
        call("notes/timeline", {"limit": args.limit})
    elif args.command == "global-timeline":
        call("notes/global-timeline", {"limit": args.limit})
    elif args.command == "hybrid-timeline":
        call("notes/hybrid-timeline", {"limit": args.limit})
    elif args.command == "notifications":
        call("i/notifications", {"limit": args.limit, "markAsRead": False})
    elif args.command == "note":
        payload = {"text": args.text, "visibility": args.visibility}
        if args.reply_id:
            payload["replyId"] = args.reply_id
        if args.renote_id:
            payload["renoteId"] = args.renote_id
        call("notes/create", payload)
    elif args.command == "react":
        call("notes/reactions/create", {"noteId": args.note_id, "reaction": args.reaction})
    elif args.command == "follow":
        call("following/create", {"userId": args.user_id})
    elif args.command == "show-user":
        call("users/show", {"username": args.username})
    elif args.command == "user-notes":
        call("users/notes", {"userId": args.user_id, "limit": args.limit})
    elif args.command == "show-note":
        call("notes/show", {"noteId": args.note_id})
    elif args.command == "upload":
        upload_file(args.file, args.name)
    elif args.command == "update-profile":
        payload = {}
        if args.name is not None:
            payload["name"] = args.name
        if args.description is not None:
            payload["description"] = args.description
        if args.avatar_id:
            payload["avatarId"] = args.avatar_id
        if args.banner_id:
            payload["bannerId"] = args.banner_id
        call("i/update", payload)


if __name__ == "__main__":
    main()
