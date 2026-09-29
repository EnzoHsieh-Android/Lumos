severity: major

# 第 3 輪 邊界席(sonnet)報告

實驗環境:`git clone --shared` 到臨時目錄,直譯器 /opt/homebrew/bin/python3(3.14),用 test_lumos.py 的 `_df_repo` / `_df_fix` 夾具真跑 `lumos drift fix --kind c4`,純函式部分直接載入 scripts/lumos 呼叫。

## F1 c4 的 --old 連冒號後的空白一起吃掉,換完變成 `valid_under:x`,標準 YAML 讀不了整段開頭欄位,工具照樣回 0
severity: major
blocking: 是
引句:「_DRIFT_VU_ITEM_RE = re.compile(r"^(\s*-\s+|valid_under:\s*)(.*)$")」
佐證行:file: `scripts/lumos:27971`(`_DRIFT_VU_ITEM_RE`)、`scripts/lumos:28000`(`_drift_valid_under_hits` 的 col 從冒號之後起算,冒號後的空白算可被 --old 涵蓋)
1. 輸入:驗證紀錄開頭欄位 `valid_under: a uncommitted`(單行值),執行 `lumos drift fix Verification/E 4 --kind c4 --old " a uncommitted" --new x`(--old 前面帶一個空白)。
2. 走到:`_drift_valid_under_hits` 從冒號後一格開始 find,空白也在比對範圍內,命中一次;`out[i]` 變成 `valid_under:x`;`_drift_c4_yaml_err(after)` 用 `valid_under:\s*` 比對(`\s*` 允許零個空白),item=`x` 過 `_yaml_plain_ok`,回 None。
3. 壞在哪:實測 rc=0、訊息「✓ drift fix c4 …換掉了還沒提交的說法」,檔案落成 `valid_under:x`(帶 3 個空白的 `--old "   a uncommitted"` 同樣落成 `valid_under:x`)。本工具自己的 TOP_KEY_RE(冒號後 `\s*`)照讀,所以「換完再用自己的讀法驗證」與 c4 已消失都通過;標準 YAML:`ruby -ryaml -e 'YAML.safe_load("type: verification\nvalid_under:x\n")'` 得 `ERR could not find expected ':' while scanning a simple key at line 2 column 1`,也就是 Obsidian 讀整段開頭欄位會壞。這正是 `_drift_c4_yaml_err` 這次改寫要擋的類別(本工具讀法比標準寬),只是漏了「冒號後必須至少一個空白」這條:`-` 項目那一支用 `\s+` 所以擋得住(實測 `  -x` 走到「跨行的值」錯誤),`valid_under:` 那一支用 `\s*` 擋不住。
4. 重現:上述夾具腳本,`_df_fix(v,"Verification/E","4","--kind","c4","--old"," a uncommitted","--new","x")` 回 0,`E.md` 內 `valid_under:x`;對照組 `--old "a uncommitted"` 得 `valid_under: x`。

## F2 行尾帶 YAML 註解的引號項目,一律擋下,錯誤訊息指向沒動過的引號
severity: minor
blocking: 否
引句:「return f"換完那一項的 {q} 沒有剛好頭尾包住整項(--old 或 --new 碰到了引號?)——給不含引號的片段"」
佐證行:file: `scripts/lumos:27991`(`_drift_c4_yaml_err` 引號分支,`item[-1] == q` 才算包住)
1. 輸入:`valid_under:\n  - "a uncommitted" # c`,`--old uncommitted --new b`(--old/--new 都沒碰引號)。
2. 走到:`item` = `"a uncommitted" # c`,`q='"'`、`item[-1]='c'` → `inner is None` → 回錯誤。
3. 實測 rc=2,訊息叫使用者檢查「--old 或 --new 碰到了引號」,但兩者都沒碰;標準 YAML 裡引號後接 ` #` 註解是合法的,這一項只能手改,訊息卻指錯方向。(同形狀:單引號項目內含 `''` 跳脫如 `'it''s uncommitted'` 也一律走這條,`q in inner`。)這是保守擋下、不是寫壞檔,所以只到 minor。

## F3 r2 只把 `drift fix` 的節點參數補成 `./` 開頭,同一份 `_drift_sh` 的另一個節點參數用途沒補
severity: minor
blocking: 否
引句:「print(f"      看:lumos context {_esc_clean(_drift_sh(p[:-3]), 300)}")」
佐證行:file: `scripts/lumos:26461`(`_drift_print_followups` 呼叫 `_drift_sh(p[:-3])`,沒帶 node=True);file: `scripts/lumos:27630`(只有 fix 的 base 帶 node=True)
1. 輸入:已收尾計劃連到的筆記,路徑以 `-` 開頭(例:`-dir/x.md`)。
2. 走到:`_drift_sh("-dir/x")` 因 `[\w./@%+=:,-]+` 全符合而原樣輸出,印出 `看:lumos context -dir/x`。
3. 壞在哪:實測 `lumos context -dir/x` 回「擋下:少了必須要給的 note」(被當成選項);r2 資安席報的正是這個形狀(`-` 開頭的節點被當選項、加引號沒用),這次只修了 fix 那一處。另一處同形狀:`probe` 的提示 `lumos drift ack ./-dir/x 3 --kind probe …` 用 node=True 印成 `./-dir/x`,但 `Env.find`(scripts/lumos:691)只認索引鍵或 stem——`./-dir/x` 不在索引鍵裡,退回用最後一段 `x` 當 stem 取第一個,同名 stem 有兩篇時會表態到別篇(`lumos context ./-dir/x` 實測「找不到」,也證明 `./` 寫法只有 `_drift_fix_target` 認)。觸發條件是路徑第一段以 `-` 開頭,罕見,故 minor。

## F4 佔位字擋下規則收窄後,`<小寫/小寫>` 這一支仍會擋掉真的理由
severity: minor
blocking: 否
引句:「_DRIFT_PLACEHOLDER_RE = re.compile(r"<(?:為什麼[^<>\n]{0,30}|sha|卷證|原片段|新片段|[a-z]+(?:/[a-z]+)+)>")」
佐證行:file: `scripts/lumos:27607`(`_drift_placeholder_err`,--reason 與 --new 都走;drift ack 的 reason 也走 `scripts/lumos:27473`)
1. 輸入:`--reason "改用 <src/lib> 的新寫法,見提交 abc123"` 或 `--new` 裡帶 `<a/b>`。
2. 走到:`[a-z]+(?:/[a-z]+)+` 命中 `<src/lib>`,實測 `_drift_placeholder_err("<a/b>")` 非 None,回「還留著提示的佔位字」。
3. 提示真正印過的 `/` 形式只有 c3 的狀態清單(`<abandoned/pass/stale/superseded>`),而 c3 的 `--status` 不走這個函式(只 --reason、--new 走),所以這一支在現行提示下沒有對應的來源,卻仍會誤擋含尖括號路徑的真理由。已確認不擋:`Map<K,V>`、`<br/>`、大寫 `<SHA>`、全形 `＜為什麼＞`;30 字界線(「為什麼」後 30 字擋、31 字放行)由設計選擇決定,提示自己的佔位字都遠短於 30 字。

## 已逐項確認沒問題的邊界(不當 finding)
- `_drift_c4_yaml_err`:空引號 `""`/`''` 經 `--new ""` 進不來(`--old、--new 不能是空字串`);單一引號字元 `"` → 擋;`~`、日期、數字、yes/no 幾種 --new 在純文字項目下:日期/數字/yes 被 `_yaml_plain_ok` 擋(實測 rc=2),`~` 只在中間(`a ~`)所以放行合理;`? ` 開頭、`- ` 開頭由 `_YAML_PLAIN_BAD_START` 與 `_drift_c4_text_err` 兩層擋;行內清單 `[..]` 明確擋下;tab 縮排的 valid_under 不被判成 c4 發現(前置就沒進來);5000 字的長值放行且不壞。
- `_DRIFT_BANNER_RE`:前面多個 `>`、全形括號、全形冒號、`# ` 前綴皆命中;只有「已結案」三字或「已結案。」不命中(會再補一條橫幅,與先前行為相同,非本輪引入)。
- `_drift_sh(node=True)`:`-`→`./-`、`--`→`./--`、`-x/y`→`./-x/y`、空字串→`''`、純空白→引號包住;`_drift_fix_target` 的 `./` 只剝一層(`.//x`、`././x` 回「找不到」,是使用者自己打的、訊息照常,不算問題)。
- `_phys_path` / `_nfc_child`:路徑段不存在、目錄不存在、空 rel 都回原路徑或 root、不拋例外;NFC/NFD 同名並存只可能在 Linux 上發生,本機 APFS 無法造出,沒有重現,不交。

## 圖譜鏡頭固定席逐條判定
- guard-kill(INVARIANT:guard kill rc 優先序、--json 純度):本次改的是 drift 系列函式與 NFC 找檔,沒動 guard kill 的 rc 判定與 JSON 輸出路徑,不影響。
- lumos-cli-read(search 預設排除 superseded、不排除 stale):本次沒動 search 的濾網,不影響。
- lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 之間):沒動 re-inject/CLAUDE.md 寫入,不影響。
- bound-tests-gate(code-loop check 逐支真跑合約綁的測試):沒動閘的算法;test_lumos.py 的新增測試不改被綁測試的方法名,不影響。
- 授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT、scripts/lumos 檔頭 SPDX+MIT):diff 沒碰檔頭與白名單,不影響。
- 測試假綠形態(還原翻紅釘需前置斷言證明現場成立):新增的 c4 相關測試若要守 F1 類問題,需要有 `valid_under:` 後零空白的輸入當前置;現行測試沒有,這是 F1 沒被抓到的原因(非合約被破壞)。
- design-loop / pitfalls-code-loop / 其餘只列名節點:本次改動不涉及處置閘與 pitfalls 分級,不影響。

最高等級:major
