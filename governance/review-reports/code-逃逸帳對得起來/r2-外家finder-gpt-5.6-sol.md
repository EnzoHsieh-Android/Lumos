severity: major

## F1 全體「站名不認得」統計漏掉三類逃逸
severity: major
blocking: yes
引句:「if kind == "plan":   # 落帳時已決定的種類為準,不因後來才有審查紀錄就事後改類(r1 外家兩席)」
file: `scripts/lumos:9918`
`plan`、`unreleased`、`unattributed` 在站名分類前就 `continue`，所以這些列即使使用未知站名，也不會增加 `totals["unknown_stage"]`。這違反設計第 73、81 行要求末尾列出全體未知站名；現有 S7 只覆蓋已放行的 design 列，沒有釘住其他桶。

實跑重現：以純記憶 fixture 餵入一列 `loop_kind=plan, stage=新站名` 後呼叫 `_escape_stats`，得到：

```text
{'no_evidence': 0, 'unattributed': 0, 'unknown_stage': 0,
 'unreleased': 0, 'plan': 1, 'withdrawn': 0}
```

預期 `plan == 1` 且 `unknown_stage == 1`。應先做 `_escape_stage_class` 與全體未知站名計數，再依 bucket 決定是否進率的分子。

## F2 撤回在符號連結守衛前先讀完整帳本
severity: major
blocking: yes
引句:「rows = _escape_raw_rows(env)」
file: `scripts/lumos:9604`
設計明寫撤回要先過符號連結檢查，但實作先以 `read_text()` 讀完整帳本，直到找到目標、確認未撤回後才在 `scripts/lumos:9622` 呼叫 `_escape_log_guard`。因此符號連結若指向超大檔、FIFO 或 `/dev/zero`，撤回可在守衛前卡死或耗盡記憶體；若目標不存在，守衛甚至永遠不會執行。

實跑過以 spy 取代讀取器與守衛的指令，結果為：

```text
rc=2 calls=['READ_LEDGER']
```

`SYMLINK_GUARD` 沒出現，證明不存在目標的正常錯誤路徑會先讀、且完全跳過守衛。會紅的整合測試應建立 `.escape-log.jsonl -> FIFO/大型檔`，斷言命令立即回 rc2 且讀取器未被呼叫。守衛應移到鎖內、任何 `_escape_raw_rows` 之前。

## F3 清單新增 token 時仍讓帳本時間戳直接控制終端
severity: major
blocking: yes
引句:「print(f"    {str(r.get('ts') or '?')[:10]} {_esc_clean(r.get('token', '?'), 20)} [{sev_disp}@{_esc_clean(r.get('stage', '?'), 30)}] {_esc_clean(r.get('desc', ''))}"」
file: `scripts/lumos:9724`
新增段落清洗了 token、stage、desc，卻讓 `ts` 原樣輸出；撤回時間在 `scripts/lumos:9729` 也相同。逃逸帳是 repo 內可投稿的 JSONL，惡意列可用 `\u001b[2J` 清屏或注入其他終端控制序列，偽造巡帳畫面，破壞這支指令宣稱的「一行一筆」載重合約。

實跑 `cmd_loop_escape(..., list_mode=True)`，餵入 `ts="\u001b[2JFORGED"`，捕獲輸出為：

```text
'...\n    \x1b[2JFORGED ESC-A [major@CI] d[沒標該抓的規則]\n'
```

控制碼確實穿透。應把逃逸列與撤回列的時間戳都交給 `_esc_clean`，並補 C0/C1、換行及 ANSI 的回歸案例。

相關測試入口 `-k escape`、`-k rule_gap`、`-k plan_for_loop` 均已實跑，但唯讀沙箱沒有任何可寫暫存目錄，三者都在 `_isolate_environment()` 前置階段以 `FileNotFoundError: No usable temporary directory` 終止，不能宣稱案例綠；上述三個重現則皆以不寫檔方式實際跑過。

已看,無: `loop_kind` 落帳優先、sha/defect_ref 分鍵歸因、重複 token 禁撤、`--repo` 與撤回互斥、`nodes` 型別及 gate 過濾、`--withdrawn` 單獨擋下、NFC 與路徑字元守衛，未再找到具體失敗場景。
