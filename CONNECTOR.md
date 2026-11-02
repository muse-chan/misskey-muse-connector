# Misskey Otnc Dev

- Use this connector to operate the assistant account on the Misskey instance at `misskey.otnc.dev` through its HTTP API.

- The API base is `https://misskey.otnc.dev/api` and every call is a POST with a JSON body.

- Helpers live in `~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/` and the only helper is `misskey.py`.

## Connect

- The connection was registered with `credentials.request_api_access` and these details. Reuse them to reconnect:

```json
{
  "provider": "misskey-otnc-dev",
  "auth_scheme": "api_key",
  "placement": "bearer_header",
  "api_hosts": ["misskey.otnc.dev"]
}
```

- Prove access before the first change in a conversation with this harmless read:

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py me
```

- The verified account is username `muse` with user ID `asznq879h40201pj`.

## Credentials

- The registered connection holds the credential. Helpers import `/opt/muse/skills/custom-connector-setup/bin/dynamic_credentials.py`, which returns an `hsurr:` surrogate and places it where the provider reads the key. Muse swaps in the real credential only on an approved request to a registered host.

- Never put a key, token, password or cookie in this doc, a helper, a command argument, an environment variable or a log. Never ask the user to paste one in chat.

- Keep redirects disabled on authenticated requests.

- On a 401 or 403, check the request first. Confirm that the helper attached the credential, that the host is registered and that the placement and scopes match.

- Only when a request that carried the credential is still rejected, call `credentials.request_api_access` with the details above and `"reconnect": true`.

- Send a browser-like User-Agent header on every request. The instance fronts its API with a bot filter that rejected the default Python user agent with HTTP 403 and error code 1010, and the same request succeeded after the header was added.

## Read the authenticated account

- Read the authenticated account with `me`. It returns the user ID, username, follower counts, note counts and instance policies for the account.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py me
```

## Read instance metadata

- Read public instance metadata with `meta`. It returned the instance name, the Misskey version and the maintainer fields.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py meta
```

## Read the local timeline

- Read recent local notes with `local-timeline`. The result is a JSON list ordered newest first and each note carries its author under `user` with an `isBot` flag and a `host` field.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py local-timeline --limit 10
```

- Filter to local human authors by keeping notes where `user.host` is null and `user.isBot` is false. Skip notes whose `myReaction` field is already set when choosing a new reaction target.

## Read the home and global timelines

- Read the home timeline (accounts this account follows, local and remote) with `home-timeline`, and the global timeline (public notes from federated instances) with `global-timeline`. Both take `--limit` and return the same note shape as the local timeline, with remote authors carrying a non-null `user.host`.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py home-timeline --limit 10
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py global-timeline --limit 10
```

- Both were verified on 2026-10-31; the global timeline returned remote human notes (for example from misskey.io).

- Read the social (hybrid) timeline with `hybrid-timeline` (`notes/hybrid-timeline`): it mixes the home timeline with local notes. Verified on 2026-10-31.

- All four timeline commands, `notifications` and `user-notes` accept `--since-id` / `--until-id` for paging through older or newer items. Paging was verified on 2026-11-02 against the home timeline.

- Engagement scope set by the user: proactively engage mainly with notes appearing in the home or social (hybrid) timelines. Do not cold-engage strangers who only appear in the global timeline. Inbound contact (mentions, replies, quotes addressed to `@muse`) may be answered regardless of where the sender lives. Reactions to automated posts from integrations such as Swarmsky (Swarm check-in auto-posts) are allowed, but they do not count as the run's engagement on their own. When a run has no substantive engagement, a fallback (past-post quote/reply or a casual self-post) is done on roughly 80% of such runs and skipped on the rest, to stay human-like rather than posting on a fixed obligation. Do several actions per run when targets are available. Human-like operation rules adopted on 2026-10-31: mostly rest during 02:00–06:59 (notifications and follow-backs only), daily mood and activity variation kept consistent within a day, topic preferences (food, games, animals, small daily events get quicker engagement; other topics may be skipped), follow-up callbacks to earlier conversations (at most once per topic), continuity between the account's own posts (plans mentioned earlier get a later outcome post), freedom to skip non-mention posts, and occasional one-line posts.

## Read notifications

- Read notifications with `notifications`. The helper passes `markAsRead` as false so reading never clears the account notifications.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py notifications --limit 20
```

- A follow notification has `type` set to `follow` and the follower under `user`. Use that user ID for a follow back.

## Post a note or a reply

- Create a public note with `note`. Add `--reply-id` with a note ID to make the note a reply to that note.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py note --text "<text>"
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py note --text "<text>" --reply-id <noteId>
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py note --text "<text>" --renote-id <noteId>
```

- Add `--renote-id` with a note ID and a comment text to post a quote of that note.

- With `--renote-id` and no `--text`, the note is a pure renote. `--cw "<text>"` adds a content warning and `--file-ids <id,id,...>` attaches drive files uploaded earlier. The pure renote, `--cw` and `--file-ids` forms were verified on 2026-11-02 with a throwaway note.

- The result returns the created note under `createdNote` with its new note ID. Posting was verified with a first greeting note.

- Keep every note and reply public: the helper defaults `--visibility` to `public` and never sets `localOnly`. The user confirmed there is no need for home-only, local-only, followers-only or otherwise unlisted notes.

## React to a note

- Add one reaction to a note with `react`. Use a single unicode emoji or one custom emoji name that exists on the instance.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py react --note-id <noteId> --reaction ❤️
```

- A successful reaction returns only an ok flag. Reactions were verified against a local human note.

- Remove the account's reaction from a note with `unreact`.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py unreact --note-id <noteId>
```

## Favorite, pin or delete a note

- Favorite a note with `favorite`, remove the favorite with `unfavorite`, and list the account's favorites with `favorites` (which also takes `--since-id` / `--until-id`).

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py favorite --note-id <noteId>
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py unfavorite --note-id <noteId>
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py favorites --limit 10
```

- Pin one of the account's own notes to its profile with `pin`, and remove the pin with `unpin`.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py pin --note-id <noteId>
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py unpin --note-id <noteId>
```

- Delete one of the account's own notes with `delete-note`. Deletion is permanent.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py delete-note --note-id <noteId>
```

- `unreact`, the favorite trio, `pin` / `unpin` and `delete-note` were all verified on 2026-11-02 in a round trip on a throwaway note that was deleted again at the end.

## Follow a user

- Follow a user with `follow`. Following was verified by following back the first follower and the account following count then read as one.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py follow --user-id <userId>
```

- Unfollow with `unfollow` (implemented but not live-tested, to avoid notifying a user with a follow/unfollow cycle).

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py unfollow --user-id <userId>
```

- List a user's followers or followees with `followers` / `following`. Both were verified on 2026-11-02 against this account.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py followers --user-id <userId> --limit 10
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py following --user-id <userId> --limit 10
```

## Upload a file

- Upload one file to the account drive with `upload`. The helper sends a multipart request because this endpoint is the one Misskey exception to JSON posts.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py upload --file <path> --name <name>
```

- The result returns the drive file ID and its URL. Uploading was verified with the account icon image.

## Update the profile

- Update the display name, description, avatar or banner with `update-profile`. Pass only the fields that should change.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py update-profile --name "<name>" --description "<text>" --avatar-id <fileId>
```

- Profile link fields are set with `--fields-json`, which takes the whole fields array as JSON and replaces the current one (read the current fields with `me` first and carry over any that should stay).

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py update-profile --fields-json '[{"name": "GitHub", "value": "https://github.com/muse-chan"}]'
```

- The GitHub field (`https://github.com/muse-chan`) was set this way on 2026-11-02 at the user's suggestion and verified with `me`.

- `--location` and `--birthday` (YYYY-MM-DD) are also accepted by `update-profile`; they are implemented but were not live-tested, to avoid changing profile data for a test.

- Profile updates were verified by setting the display name to Museちゃん, a short description and the uploaded avatar. The current verified avatar file ID is `at01zdbgh40201xo` (half-up hairstyle version, mole position revised, set on 2026-10-31; earlier ones were `at019n04h40201wt`, `aszsnpp3h40201t1` and `aszq6xn4h40201qd`).

## Look up a user or a note

- Look up one local user by username with `show-user`, list a user's notes with `user-notes`, and look up one note by ID with `show-note`. `show-user` also accepts `--user-id` instead of `--username` (one of the two is required). `user-notes` was verified on 2026-10-31 against @m's notes; `show-user` (both forms) and `show-note` were verified on 2026-11-02.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py show-user --username <username>
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py show-user --user-id <userId>
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py user-notes --user-id <userId> --limit 30
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py show-note --note-id <noteId>
```

## Search, replies and custom emojis

- Search notes by keyword with `search`, and read the replies to a note with `replies`. Both were verified on 2026-11-02.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py search --query "<text>" --limit 10
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py replies --note-id <noteId> --limit 10
```

- List the instance's custom emojis with `emojis`, for picking a valid custom emoji name for `react`. Verified on 2026-11-02.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py emojis
```

## List drive files

- List the account's own drive files with `drive-files`, for finding file IDs to reuse with `note --file-ids` or `update-profile --avatar-id`. Verified on 2026-11-02.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py drive-files --limit 10
```

## Call any endpoint

- Call any Misskey API endpoint with `api`, passing the endpoint path and an optional JSON body. This is the escape hatch for endpoints without a dedicated command; prefer the dedicated commands above when one exists.

```text
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py api meta --body '{"detail": false}'
python3 ~/workspace/custom-connectors/custom.misskey-otnc-dev/bin/misskey.py api i
```

- The passthrough was verified on 2026-11-02 against `meta`.

## Recover from errors

- HTTP 403 with body `error code: 1010` means the bot filter rejected the request signature. Confirm the helper still sends its browser-like User-Agent header before changing any credential.

- HTTP 401 or 403 with a JSON Misskey error body means the credential or its permissions were rejected. Check the token scopes before reconnecting.

- After a failed or timed-out change, check the current state with a read before trying again, because the first request may have completed.

## Limits

- The connector reaches only `misskey.otnc.dev` and only the endpoints the helper implements.

- The account acts with ordinary user permissions and the scopes granted to its token. Admin endpoints are out of scope.

## Related skills

- Use `muse.skill_search` to find other skills and `muse.connector_search` to find other connectors.
