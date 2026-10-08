severity: minor

## Finding COR7-01
severity: minor
blocking: 否
引句:「規則跟 _atomic_write_bytes 與歷史檔追加一一對應:取代模式下,字元裝置直接寫、其他非目錄的東西」
file: `scripts/scenario_probe.py:47`
- 具體輸入:`--out /dev/klog`(`crw-------` root,非 root 執行),或在沒有控制終端的環境(setsid、cron)下用 `--out /dev/tty` 或 `--history /dev/tty`。
- 走到哪一段:`_output_target_problem` 在 `S_ISCHR` 時直接回 None,不查 `os.access`,也不試開。`_atomic_write_bytes` 實際會 `os.open(O_WRONLY|O_NONBLOCK|O_NOFOLLOW)`。歷史追加同樣是真開。
- 壞在哪:開跑前放行,整批模型跑完才寫入失敗。這正是「呼叫模型前就擋下」要避免的情況,也和 docstring 宣稱的「一一對應」不符。
- 重現(修後 67b1dea2):`_output_target_problem("/dev/klog")` 回 None,`_atomic_write_bytes(Path("/dev/klog"), b"")` 丟 `PermissionError [Errno 13]`。在 `start_new_session=True` 下,`/dev/tty` 的 preflight 取代與追加都回 None,實寫與追加開檔都丟 `OSError [Errno 6] Device not configured`。
- 歸因:有證據的原有漏查。修前 483df9fe 跑同一個腳本,兩個輸入的 preflight 與寫入結果完全相同。

## Finding COR7-02
severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/scenario_probe.py:82`
- 具體輸入:沒有控制終端的 session leader,執行 `--out /dev/ttysNNN`(`--history` 同理,見 `scripts/scenario_probe.py:1389`)。
- 走到哪一段:字元裝置分支開 tty 時沒帶 `O_NOCTTY`。`_confirm_tty` 與本次合併進來的 lumos 主程式都已為同一問題加了 `O_NOCTTY`,見 lumos-cli-lifecycle 筆記的 PITFALL。
- 壞在哪:開檔會把該 tty 取得成控制終端。
- 重現:`start_new_session=True` 的子程序先確認 `os.open("/dev/tty", O_RDWR|O_NOCTTY)` 失敗(ctty=False),開 pty slave 後同一檢查變 True(ctty=True)。我沒看到 SIGHUP,子程序 rc 0,所以只證明取得控制終端,沒證明被掛斷。
- 歸因:有證據的原有漏查。r5 的 `os.open(path, O_WRONLY|O_NOFOLLOW)` 同樣沒有 `O_NOCTTY`,r6 只是加了 `O_NONBLOCK`。

## Finding COR7-03
severity: minor
blocking: 否
引句:「標記字元 ⟦ 本身也照寫,原文因此一對一還原得回去,字面反斜線不必加倍」
file: `governance/eval/ablation_lumos_first.py:389`
- 具體輸入:meta 的 date 欄為 `"a\nb"`、`"a\u00a0b"`、`"a\u3000b"` 或 `"a b"`。
- 走到哪一段:`text()` 先把 `\r`、`\n` 換成空白,`visible()` 又把 Zs 類字元折成空白,所以這幾種輸入的報表標題行完全相同。
- 壞在哪:程式註解和 ablation-lumos-first 的 WHY 都寫「一對一」、「要能從報表一對一看出原值是哪個字元」,與行為不符。⟦ 本身確實可逆(`⟦U+001B⟧` 字面文字會變成 `⟦U+27E6⟧U+001B⟧`,和真 ESC 不同;代理對 `\ud800` 變成 `⟦U+D800⟧`)。不可逆的是換行與 Zs 空白。
- 重現(修後版 `render_md` 第一行):`nl==sp`、`nbsp==sp`、`ideo==sp` 全部為 True。
- 歸因:折成空白的行為是原有的,修前 483df9fe 輸出同樣相等。「一對一」這個宣稱是 3e149721 新寫進註解和筆記的。

## 固定席逐條判定
- **測試假綠形態(★INVARIANT★ 前置斷言)**:不影響。新測試都有「現場成立」斷言:硬連結 `nlink==2`、symlink 被換掉、tempfile 預設 0600。我另外拿 FIFO 在修前版實跑,3 秒內卡住,修後版換成普通檔,確認這個紅綠成立。
- **canary-audit、bound-tests-gate、design-loop、lumos-cli-read(★INVARIANT★)**:不影響。diff 沒有碰 canary、bound-tests、處置閘或 search 的程式。這些節點只因為牽連檔列表才出現。
- **lumos-cli-lifecycle(O_NOCTTY 的 INVARIANT 與 PITFALL)**:合併後 PITFALL 和「Claude 外掛」章節都在,`scripts/lumos` 沒變。COR7-02 是探針這條路徑沒有跟進 `O_NOCTTY`。
- **codex-harness**:合併段保留兩邊,詳見下一項。
- **be-api-compat**:`--out` 的 JSON 內容和 CLI 旗標沒變。行為差異有兩處:FIFO、socket、連結改成換成普通檔,以及 stdout 是管線時 `--out /dev/fd/1` 現在在 preflight 回 rc2(修前版放行並直寫)。這是 r6 的刻意改動,訊息是「`/dev/fd` 不可寫」,不是靜默失敗。報表標記格式從 `\xNN` 改成 `⟦U+XXXX⟧`,舊報表不受影響。
- **be-authz**:硬連結到自己 0666 檔時,新檔 0644,原名稱內容不變(實測 `b` 為 0o644、`a` 仍是 V,修前版 b 為 0o666)。別人擁有的檔改走 `_euid` 探針,測試覆蓋。程序 umask 不再被改動(呼叫後仍是 0o22)。

## 合併段(手解衝突)
- **四篇 Systems 筆記**:我用 PyYAML 逐篇解析開頭欄位,全部合法,沒有重複 key,`verified_by`、`related`、`about_code` 清單也沒有重複項。
  - `updated` 和 `self_audit` 與兩個父版本比對一致:codex-harness 取 10-08;pitfalls-code-loop 的 self_audit 取較新的 `gpt-5.6-sol/2026-10-03`;測試假綠形態取主線 10-07;lumos-cli-lifecycle 兩邊本來就相同。
  - 正文兩邊都在,沒有衝突標記,也沒有互相矛盾的段落。
  - 小瑕疵:`lumos-cli-lifecycle.md` 的 PITFALL 與 `## Claude 外掛` 標題之間沒有空行,codex-harness 的 `## 2026-10-05 背景啟動錯誤的派工提示` 前也沒有空行。Markdown 仍能正確渲染,我沒找到具體失敗場景,所以不立 finding。
- **MOC/index**:兩行都在,`Systems/ablation-lumos-first` 與 `Systems/review-convergence-eval` 兩個節點檔都存在。
- **SKILL.md**:第 5、6 步取主線版,另保留「試行工作另依 reference.md」一行。
  - `reference.md` 的〈修復穩定性試行〉和兩篇計劃筆記都存在。
  - frontmatter 的 description 用引號包起來,合法。主線版的 description 含 `tier: high`,PyYAML 解析會報 `mapping values are not allowed here`,所以合併結果比主線更合法。

## 修補三問
1. **原問題的修復效果**:有行為證據。
   - G-FIFO:沒人讀的 FIFO,修前 3 秒卡住,修後換成普通檔;socket 也換成普通檔。
   - G-PRE:歷史檔是 FIFO 時,修前 preflight 回 None,修後回「不是一般檔案」。
   - G-UMASK/OWNER:程序 umask 不再被碰,硬連結不沿用 0666。
   - G-HISTSWAP:跑的期間被換成連結時追加報錯、受害檔不變(`t_probe_boundary_fifth_round_output_edges` 在修後版 25 passed、0 failed)。
   - G-MD:`C:\dir` 渲染成 `C\:\\dir`,修前版是 `C\:\\\\dir`。
2. **相鄰路徑是否仍成立**:成立。
   - `/dev/null` 取代與追加都照常。
   - 符號連結指向目錄時,連結本身被換成普通檔。
   - `os.replace` 失敗、`fsync` 時 KeyboardInterrupt 都不留暫存檔(實測目錄裡只剩 `sock`)。
   - 既有 0600 檔的權限保留。
   - 檔名 255 bytes 邊界由原測試覆蓋,我沒另外重跑。
3. **新發現在修前、修後的結果**:三條都是修前修後行為相同(COR7-01 與 COR7-02 的輸出完全一致,COR7-03 的折空白相等也一致),都不是修補回歸。G-MERGE 的「主線兩支派工鏡頭測試不再逾時」我沒驗。

## 未驗範圍
- 沒跑全套,也沒跑 `t_codex_s1_lens_arm_claim` 和 `t_codex_s1_r1_fixes`。
- 沒有驗證的假設:
  - sticky 目錄(如 `/tmp`)裡別人擁有、且我 `os.access` 可寫的檔。preflight 會放行,但 `os.replace` 理論上會被 sticky 位擋成 EPERM。我找不到可用的他人擁有的可寫檔來重現,所以不立 finding。
  - `os.O_NONBLOCK` 在歷史追加路徑沒用 `getattr` 保護(`O_NOFOLLOW` 有)。這只影響沒有 `O_NONBLOCK` 的平台(Windows),而探針依賴 rsync,我判定不是支援平台。
  - `--out /dev/fd/1` 且 stdout 是 tty 時,`set_blocking(True)` 會清掉共用檔案描述上呼叫端原本設的非阻塞旗標(實測 `nonblock-after=False`)。我沒找到會造成實際損害的場景,所以只記在這裡。
- 沒看 r1 到 r6 的卷證,也沒審主線 344 個提交本身。

總結:最高嚴重度 minor
