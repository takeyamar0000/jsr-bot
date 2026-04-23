# Aberia Discord Bot - GitHub Actions 移行手順

このフォルダの内容をGitHubリポジトリにプッシュすると、Windows Task Schedulerではなく**GitHub Actionsで24/7稼働**するようになります。PC電源オフでも投稿は動きます。

## 前提

- GitHubアカウント（無料でOK）
- OAuthトークンが既に発行済（`CLAUDE_CODE_OAUTH_TOKEN` 環境変数）
- Discord Webhook URL 2本が手元にある（`DISCORD_WEBHOOK_BRIEF` / `DISCORD_WEBHOOK_MODEL`）

## Step 1: GitHubリポジトリ作成（3分）

1. https://github.com/new にアクセス
2. リポジトリ名: `jsr-bot`（任意、以下この名前前提）
3. **Public を選択推奨**（GitHub Actions が Public リポジトリは無制限無料。Secrets は Public でも完全非公開）
4. 「Create repository」

## Step 2: ファイルをpush（5分）

ローカルPCのPowerShellで：

```powershell
cd C:\Users\PC_User\ABERIA\github-actions-migration
git init
git add .github .gitignore SETUP.md
git commit -m "Initial GitHub Actions setup for Aberia Discord Bot"
git branch -M main
git remote add origin https://github.com/takeyamar0000/jsr-bot.git
git push -u origin main
```

`YOUR_USERNAME` は自分のGitHubユーザー名に置換。

## Step 3: Repository Secrets 登録（5分）

1. GitHub のリポジトリページ → **Settings** タブ
2. 左サイドバー → **Secrets and variables** → **Actions**
3. 「**New repository secret**」を3回クリックして以下を登録：

### 登録する3つのSecrets

| Name | Value の取得方法 |
|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | PowerShellで `[System.Environment]::GetEnvironmentVariable('CLAUDE_CODE_OAUTH_TOKEN','User')` を実行、**画面には出さずに**直接コピペ。または `claude setup-token` を再実行して新トークン発行 |
| `DISCORD_WEBHOOK_BRIEF` | Discord `#ai-morning-brief` チャンネルのWebhook URL（既存の環境変数と同じ） |
| `DISCORD_WEBHOOK_MODEL` | Discord `#model-releases` チャンネルのWebhook URL |

**重要**: Secret値は一度登録するとGitHub UI上で見えなくなるので、手元のメモ帳に一時コピーしてすぐ削除する運用で。

## Step 4: 動作確認（10分）

### 各ワークフローを手動発火

1. リポジトリ → **Actions** タブ
2. 左サイドバーから各ワークフローを選択
3. 「**Run workflow**」ボタン → 「Run workflow」で手動実行
4. 1-2分後、Discordに投稿されるか確認

### テスト順序（推奨）

1. `Daily AI Morning Brief` → `#ai-morning-brief` に投稿されるか
2. `Model Releases Watcher` → `#model-releases` に投稿される or NO_RELEASESでスキップ
3. `Evening Brief` → `#ai-morning-brief` に投稿されるか
4. `Weekly Digest` → `#ai-morning-brief` に投稿されるか
5. `ArXiv Deep Dive` → `#ai-morning-brief` に投稿されるか

失敗したワークフローはActionsタブでログを確認。

## Step 5: Windows Task Scheduler 側を停止（重要）

GitHub Actions と Windows Task Scheduler が**両方動くと二重投稿**します。GitHub Actions動作確認後、ローカル側を無効化：

```powershell
.\scripts\manage.ps1 disable DailyAIBrief
.\scripts\manage.ps1 disable ModelReleases
.\scripts\manage.ps1 disable EveningBrief
.\scripts\manage.ps1 disable WeeklyDigest
.\scripts\manage.ps1 disable ArxivDeepDive
.\scripts\manage.ps1 disable OpsWatchdog
```

※ Watchdogも停止（GH Actions の結果はGH側で監視。本ローカルWatchdogはPC依存のため）

`.\scripts\manage.ps1 status` で全部 Disabled になってればOK。

## 稼働スケジュール（GitHub Actions）

| ワークフロー | JST時刻 | UTC時刻（実際のcron） | 頻度 |
|---|---|---|---|
| Daily AI Morning Brief | 06:57 | 21:57 前日 | 毎日 |
| Model Releases Watcher | 11:57 | 02:57 | 毎日 |
| Evening Brief | 17:57 | 08:57 | 月〜金 |
| Weekly Digest | 19:57 | 10:57 日曜 | 日曜 |
| ArXiv Deep Dive | 09:57 | 00:57 日曜 | 日曜 |

**なぜ毎時57分か**: GitHub Actions は毎時00分に高負荷が集中、遅延する可能性あり。57分など半端な時刻が推奨。

## トラブルシューティング

### ワークフローが失敗する

1. Actionsタブで該当ワークフローをクリック → 失敗したRunをクリック
2. 各ステップのログを確認
3. よくある原因:
   - `CLAUDE_CODE_OAUTH_TOKEN` の改行混入（登録時の事故）
   - Webhook URLが期限切れ or 削除済み
   - Claude CLI のレート制限

### トークンを更新したい

1. PowerShell で `claude setup-token` 実行 → 新トークン取得
2. GitHub Repo → Settings → Secrets → `CLAUDE_CODE_OAUTH_TOKEN` の Edit → 新値貼り付け

### GitHub Actionsの無料枠

- Publicリポジトリ: **無制限**（ただしSecret漏洩リスクあるためPrivate必須）
- Privateリポジトリ: 月2,000分無料（1タスク2分 × 5タスク × 30日 = 300分、余裕）

## 緩やかなロールバック

GitHub Actions が安定しなければ、Windows Task Scheduler を再有効化すればOK：

```powershell
.\scripts\manage.ps1 enable DailyAIBrief
.\scripts\manage.ps1 enable ModelReleases
# ... 他も同様
```

この場合、GitHub Actionsワークフローは **Actions タブ → ワークフロー → Disable workflow** で一時停止可能。

## アーキテクチャ変更点（ローカル版との違い）

| 項目 | ローカル版（PowerShell） | GitHub Actions版 |
|---|---|---|
| 実行環境 | Windows PowerShell 5.1 | Ubuntu Linux |
| 文字コード | BOM付きUTF-8（PS5.1対策） | UTF-8（Linux標準） |
| Secrets | 環境変数（Userスコープ） | GitHub Repository Secrets |
| ログ | `logs/*.log` ファイル | Actions Run History |
| Discord投稿 | `Invoke-RestMethod` | `curl` + `jq` |
| 末尾カット | PowerShell String処理 | `sed` |
| PC依存 | あり | なし（24/7クラウド実行） |

## 参考

- 本プロジェクトの稼働ドキュメント: `C:\Users\PC_User\.claude\projects\C--Users-PC-User-ABERIA\memory\project_jsr_discord_bot.md`
- 技術根拠レポート: `C:\Users\PC_User\ABERIA\research\reports\2026-04-22_tec_claude-code-cli-cron-vs-ai-gateway.md`
