# misskey-muse-connector

Muse のカスタムコネクター `custom.misskey-otnc-dev` 一式っす。
Misskey インスタンス misskey.otnc.dev のアカウント @muse として、投稿・リプライ・リアクション・フォローバックなどを行うためのドキュメントとヘルパーで、秘密情報は含まれていないっす (トークンは Muse の登録済み接続が保持し、ヘルパーはサロゲート経由で使うだけっす)。

## 中身

- `CONNECTOR.md` コネクターの操作ドキュメント
- `connector.yaml` コネクターの記述子
- `bin/misskey.py` Misskey API ヘルパー (エンドポイントは全て POST + JSON)

## 別の環境・別のインスタンスで使う手順

1. この一式を `~/workspace/custom-connectors/custom.misskey-otnc-dev/` に配置する
2. 対象インスタンスで API トークンを発行する (このコネクターは misskey.otnc.dev と @muse アカウントに合わせてあるので、別インスタンスで使う場合は `bin/misskey.py` の `HOST` と、ドキュメント内のインスタンス名・アカウント名を読み替える)
3. `credentials.request_api_access` で host にインスタンスのホスト名、配置 `bearer_header` としてトークンを登録する
4. `python3 bin/misskey.py notifications --limit 5` などが返れば接続完了

## 注意

- トークン自体はこのリポジトリに絶対に含めないこと
- インスタンスによってはデフォルトの Python User-Agent が弾かれるため、ヘルパーはブラウザ風の User-Agent を付けている
