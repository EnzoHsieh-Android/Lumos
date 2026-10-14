severity: clean

我已逐 hunk 讀完測試文件組,從攻擊者角度看,沒有發現能被利用的洞。以下是各類的結論,最後三問附在後面。這次只讀了 patch 和 repo 在 9b8ce146 的相關行,沒有另外跑重現,所以結論是讀碼判斷。

## 逐類檢視

1. **執行邊界:已看,無。**
   - `scripts/test_lumos.py` 新增的測試,暫存目錄都用 `mkdtemp`,前綴是 `gctl-bypass-*` 或 `gctl-hookevent-trim-`。清理只對自己建的目錄做 `rmtree(..., ignore_errors=True)`,沒有萬用字元,也沒有寫到暫存目錄外。
   - 假 git 放在獨立的 `gctl-bypass-fakegit-*` 目錄,內容是 `sleep 30`,`chmod 0o755`。PATH 只加在傳給子程序的 `env` 裡,不污染測試行程。
   - 子程序都是固定的 `[sys.executable, 腳本路徑]`,沒有 `shell=True`,也沒有拼接指令字串。
   - `t_bypass_ask_registered` 把 `HOME`、`USERPROFILE`、`CODEX_HOME` 指向假 home 再跑 `merge-claude-settings.py`,不會碰真的 `~/.claude`。
   - `t_hook_event_trim_tmp_unique` 的 `chmod 0o644` 只對自己建的檔做。它對 `.trim` 殘檔的 `utime` 和 `unlink` 也都在自己的暫存目錄內。
   - `scripts/merge-claude-settings.py` 新增 `matcher: "Bash"` 的註冊,指令走既有的 `_hook_cmd`,逾時 5 秒。`_codex_entries` 對 Bash 這條用 `continue` 跳過,所以 Codex 不會收到看不懂的 `ask`。
   - `scripts/lumos` 把 `bypass-ask-hook.py` 加進 `_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES` 和 `enforcement_status`。
   - 反安裝名單(第 25408 行)用 `_GLOBAL_HOOKS + _RETIRED_*`,所以新檔會跟著清。
   - 安裝名單只增不減,沒有新增可任意指定路徑的入口。
2. **文件裡給人照抄的回退步驟:已看,無。**
   - 計劃〈回退〉的步驟只動 repo 內的註冊、名單和測試。
   - 它明講「只拿掉 matcher 不夠,已寫進 settings 的條目不會被剪」,要走空殼期再真刪。
   - 我驗證了 `_RETIRED_STUB_CLAUDE_HOOKS` 和 `_RETIRED_CLAUDE_HOOKS` 都存在於 `scripts/lumos`,步驟可照做。
   - 空殼是直接放行,不是靜默擋住,照做不會讓使用者被卡死或誤放。
   - 〈回退〉也沒有 `rm -rf`、`--force` 或繞閘的指令。
3. **授權範圍有沒有被放寬:已看,無。**
   - 掛鉤只回 `ask`,不回 `allow`。
   - 錯誤、逾時和壞輸入一律放行,這是計劃明寫的設計決定,不是新洞。
   - 掛鉤檔進了錨點名單(`anchor`),被改動會被擋推送,所以對它的防護是增加。
   - 複製到 `~/.codex/hooks` 但不註冊,是死檔,不會被執行。

## 固定席節點判讀

- **lumos-cli-read、lumos-cli-lifecycle、design-loop、測試假綠形態:不影響。**
  - 這次沒有動 `search` 排除邏輯、re-inject 的 sentinel 行為、處置閘判定,也沒有動還原翻紅釘的前置斷言。
  - 新測試都只做正向斷言,而且都是對真實呼叫做斷言,不是重寫實作。
- **guard-kill、pitfalls-code-loop、reversibility-governance-ledger:不影響。**
  - 沒有碰 guard kill 的 rc 優先序或 JSON 輸出。
  - `scripts/lumos` 的改動只是名單增列,沒有新增不可逆操作。
- **code-loop守衛main-direct盲區 Issue:不影響。**
  - 新掛鉤只問人,沒有處理 code-loop 守衛的 main 直推路徑。

## 修補鏡頭三問(測試文件組範圍)

1. **原問題的修復效果:**
   - 我只驗證了測試是否會抓到問題,沒有跑修前與修後的重現。
   - 讀碼可見 `t_hook_event_trim_tmp_unique` 的前置條件(把固定名 `.tmp` 佔成資料夾)會讓舊的固定暫存檔寫法失敗,所以能抓到回歸。
   - 但這是讀碼判斷,不是同一案例修前修後的實跑結果。
2. **修補處的正常、錯誤與相鄰路徑:**
   - 修剪的正常路徑、`os.replace` 失敗的清理分支、長行、權限保留、舊殘檔的清掃,測試都有覆蓋。
   - 我沒有發現相鄰路徑被破壞。
3. **新發現:無。** 修前與修後比對因此不適用。

未驗範圍:程式組(`bypass-ask-hook.py`、`_hookevent.py` 的實際分類邏輯)由另一席資安看,我沒有重現。

最嚴重等級:clean,blocking 共 0 條。
