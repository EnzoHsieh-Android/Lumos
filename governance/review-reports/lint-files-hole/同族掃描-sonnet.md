severity: major

# 同族缺陷掃描(A/B/C/D 四類)

範圍:`scripts/lumos`(約 28,572 行)、`scripts/test_lumos.py`(約 42,348 行)。
今天已經修掉、不再重報的四個實例:`_ledger_fold` 只看三欄有沒有值(A)、`valid_under`/`revalidate_when`
判空兩套口徑(B)、`{LINT_FILES}` 佔位符五個呼叫端漏一個(C,`_pitfall_diff_collect` 那條)、
節點檔名撞上斷言子字串(D)。以下只列這四個之外、新找到的。

本次掃描由我(主導)+ 三個並行 fork 分工完成:A 類我自己全程手動核對,B/C/D 各由一個 fork 專責,
每一條發現我都用 `python3 SourceFileLoader` 動態載入 `scripts/lumos` 獨立重跑過一次,確認 fork
回報的重現步驟跟輸出屬實,不是照抄轉述。

---

## A. 靠「欄位剛好有沒有值」在過濾,而不是看種類/型別欄位

沒有找到新實例。

逐一核對過主程式裡目前全部的 jsonl 帳本折疊/分類邏輯(`.canary-log.jsonl`、`.governance-log.jsonl`、
`.escape-log.jsonl`、`.kill-log.jsonl`、`.signoff-log.jsonl`、`.ci-log.jsonl`、cascade 用的
每輪一份 jsonl),以及 frontmatter 的 `type`/`status` 判斷、`.lumos/lint.json`、
`.lumos/lint-waivers.json`、`.lumos/rules/index.json` 這些「誰都能寫」的 JSON 設定檔載入邏輯。
除了今天已修的 `_ledger_fold` 之外,其餘所有分類/折疊邏輯都是靠明確的 `kind`/`gate`/`event`/
`status` 欄位判斷是不是某一種紀錄,沒有再靠「幾個欄位剛好都有值」去猜種類的地方。

---

## B. 同一個語意判斷有兩套實作

### B-1:「有沒有藏在圍欄裡的假宣告」——`_intake_declared` 自己重寫一套剝圍欄邏輯,跟全檔唯一的 `_visible_lines` 不一樣

severity: minor

位置:`scripts/lumos:5373-5384`(`_intake_declared`)對照 `scripts/lumos:2841`(`_visible_lines`,
docstring 自陳是「這個弱點原本散在四處,現在統一」的唯一實作)

重現:實際動態載入跑過。

```
python3 -c "
import importlib.machinery, importlib.util, sys
loader = importlib.machinery.SourceFileLoader('m', 'scripts/lumos')
spec = importlib.util.spec_from_loader('m', loader)
mod = importlib.util.module_from_spec(spec); sys.argv=['lumos']; loader.exec_module(mod)
text = '\`\`\`\`\n\`\`\`\npreflight-4: ran\n\`\`\`\n\`\`\`\`\n'   # 4 個反引號包住一段示範,示範裡又有 3 個反引號
print('intake_declared:', mod._intake_declared(text))
hits=[ln for _no,ln in mod._visible_lines(text.splitlines(), keep_fenced=False) if ln.startswith('preflight-4:')]
print('visible_lines hits:', hits)
"
```

實際輸出:
```
intake_declared: True
visible_lines hits: []
```

白話:`_intake_declared` 是 intake 守衛用來判斷「這份前掃紀錄檔裡有沒有一行合法的
`preflight-4: ran` 宣告」的函式,docstring 自己講的規則是「先剝圍欄再掃,圍欄內的頂格示例
不算數,因為模板照抄貼上就等於偽造」。但它剝圍欄用的是自己寫的一行正則
`` ```.*?``` ``(非貪婪、不管反引號數量對不對稱),遇到「4 個反引號包住一段裡面又有 3 個反引號
的示範文字」這種巢狀情況,會剝錯配對,反而把應該被當成「圍欄內示範」而忽略的假宣告,誤判成
「圍欄外的真宣告」而判定 `True`(合法留痕)。全檔另外有一支 `_visible_lines`,docstring 明講
這個處理不對稱圍欄的坑「原本散在四處」而統一成一支唯一實作,`_intake_declared` 卻沒有用它,
自己另開一條路,對同一份輸入給出跟唯一實作不一樣的答案。目前判定 minor 是因為
`_intake_dir_status`(它唯一的呼叫端)的後果只是印一個 ⚠ 提示、明寫「不進合取、不改 rc」,
沒有接到任何真正會擋人的閘;但如果之後有人把它接進會擋的閘,這個洞會讓刻意用巢狀圍欄
包裝假宣告的人騙過守衛。

---

## C. 同一個契約在多個呼叫端各實作一次,可能漏了某一個

### C-1:寫入 `~/.cache/lumos/` 底下任何東西前要先驗目錄可信——`_vault_write_lock` 沒做

severity: major

位置:`scripts/lumos:11116-11132`(`_vault_write_lock`,鎖檔放在
`~/.cache/lumos/vault-lock/<hash>.lock`)對照 `scripts/lumos:24282`(`_trusted_private_dir`,
docstring 自稱「單一來源」)及它另外三個有做的呼叫端:`scripts/lumos:23959`
(`_lens_cache_write`)、`scripts/lumos:24345`(`_lens_arm_dir_ok`)、`scripts/lumos:25338`/
`25359`(bound-filter 快取讀寫)

呼叫端清單(要不要在 `~/.cache/lumos/*` 底下寫東西之前先過 `_trusted_private_dir`):
- `_lens_cache_write`(dispatch-lens 快取寫入)—— 有做
- `_lens_arm_dir_ok`(armed 目錄檢查)—— 有做
- bound-filter 快取讀取(25338)—— 有做
- bound-filter 快取寫入(25359)—— 有做
- `_vault_write_lock`(筆記庫寫入鎖)—— **沒做**;docstring 裡寫著「照 dispatch-lens 快取的
  先例:不放共用暫存目錄——路徑可預測、會被別的使用者先佔」,講的正是 `_trusted_private_dir`
  要擋的那個威脅,但程式碼裡只做了 `lock.parent.mkdir(parents=True, exist_ok=True)`,從沒呼叫
  `_trusted_private_dir`;它底層共用的鎖原語 `_excl_lock_try` 也不驗這件事,是靠呼叫端各自
  擋一次,而這條呼叫端沒有擋

重現:實際跑過,把 `HOME` 指到假家目錄,把 `~/.cache/lumos` 建成指向攻擊者目錄的 symlink。

```
python3 - <<'EOF'
import os, sys, tempfile, importlib.machinery, importlib.util
from pathlib import Path
fake_home = Path(tempfile.mkdtemp(prefix="fakehome-"))
attacker_dir = Path(tempfile.mkdtemp(prefix="attacker-"))
os.environ["HOME"] = str(fake_home)
(fake_home / ".cache").mkdir()
os.symlink(str(attacker_dir), str(fake_home / ".cache" / "lumos"))
loader = importlib.machinery.SourceFileLoader("lumos_mod", "scripts/lumos")
spec = importlib.util.spec_from_loader("lumos_mod", loader)
mod = importlib.util.module_from_spec(spec); sys.argv=["lumos"]; loader.exec_module(mod)
vault = Path(tempfile.mkdtemp(prefix="vault-")) / "notes"; vault.mkdir()
with mod._vault_write_lock(vault):
    pass
for p in attacker_dir.rglob("*"):
    print(p, p.stat().st_size if p.is_file() else "(dir)")
print("_trusted_private_dir 判定:", mod._trusted_private_dir(
    fake_home/".cache"/"lumos"/"vault-lock", ".cache","lumos","vault-lock"))
EOF
```

實際輸出:
```
/tmp/attacker-xxx/vault-lock (dir)
/tmp/attacker-xxx/vault-lock/c73b776bc372b8d08847410b21123918.lock 15
_trusted_private_dir 判定: False
```

工具真的把鎖檔(內容是 PID + 時間戳)寫進了攻擊者控制的目錄,而 `_trusted_private_dir` 對這條
路徑的判定明明是「不可信」——只是 `_vault_write_lock` 從沒去問過它。

白話:這把鎖存在的唯一理由,是防止兩個 `lumos` 行程同時改同一本筆記庫時「後寫蓋掉先寫」
(`_vault_write_lock` 自己的 docstring 就是這樣寫的)。如果同一台機器上有別人、或用任何方式
能提前把 `~/.cache/lumos` 佔成一個他控制的目錄(`_trusted_private_dir` 自己的 REVISIT 註記就
點名「共用機器、容器掛載」是要重估的情境),他就能看到、刪掉、或偽造這把鎖檔,鎖形同虛設,
兩個 `lumos` 行程可能同時「讀—改—寫」同一本筆記庫、蓋掉彼此的修改——正是這道鎖原本要擋的
資料損壞。單機單使用者日常用法不受影響,但這是鎖機制在它自己承認要涵蓋的威脅模型下實際失效。

### C-2:`{LINT_FILES}` 佔位符替換宣稱「唯一實作」,但還有兩個呼叫端各自手寫一份

severity: major

位置:`scripts/lumos:17265-17282`(`_lintcheck_smoke_cmd`,`lint-check --smoke` 冒煙路徑)、
`scripts/lumos:17494-17502`(`cmd_rule_check`,`rule-check` 規則索引核對)對照
`scripts/lumos:17784-17800`(`_lint_cmd_with_files`,docstring 自稱「★唯一實作★……抽成一支
就不會再漏第四個地方」)

呼叫端清單:
- `_pitfall_diff_collect`(算改動風險分級,`scripts/lumos:20917`)—— 有做(呼叫
  `_lint_cmd_with_files`;今天才修好的那一條)
- `_lint_new_verdict`(新增告警閘真跑,`scripts/lumos:18388`)—— 有做
- `_lint_run_and_parse`(執行入口,`scripts/lumos:17649`)—— fail-closed 安全網
  (`if _LINT_NEW_FILES_TOKEN in cmd: return [], False`),不是正面實作但擋得住漏做的後果
- `_lintcheck_smoke_cmd`(冒煙,`scripts/lumos:17282`)—— **沒做**,自己寫
  `cmd.replace(_LINT_NEW_FILES_TOKEN, " ".join(shlex.quote(f) for f in files))`
- `cmd_rule_check`(規則索引核對,`scripts/lumos:17502`)—— **沒做**,自己寫
  `cmd.replace(_LINT_NEW_FILES_TOKEN, _shlex.quote(str(sp)))`

重現:實際載入模組驗證原始碼裡有沒有出現共用函式名,並比對三份實作對同一輸入的輸出。

```
python3 -c "
import importlib.machinery, importlib.util, sys, inspect
loader = importlib.machinery.SourceFileLoader('m', 'scripts/lumos')
spec = importlib.util.spec_from_loader('m', loader)
mod = importlib.util.module_from_spec(spec); sys.argv=['lumos']; loader.exec_module(mod)
print('smoke 用共用函式?', '_lint_cmd_with_files' in inspect.getsource(mod._lintcheck_smoke_cmd))
print('rule-check 用共用函式?', '_lint_cmd_with_files' in inspect.getsource(mod.cmd_rule_check))
print(mod._lint_cmd_with_files('cmd {LINT_FILES} out', ['a b.kt','c.kt']))
"
```

實際輸出:
```
smoke 用共用函式? False
rule-check 用共用函式? False
cmd 'a b.kt' c.kt out
```

白話:今天為了修「算風險分級那條漏了換佔位符」的洞,把換佔位符的邏輯抽成
`_lint_cmd_with_files` 一支函式,理由寫得很白:「抽成一支就不會再漏第四個地方」。但實際上
冒煙(`lint-check --smoke`)跟規則索引核對(`rule-check`)這兩個呼叫端沒有被改成呼叫它,還是
各自保留原本的手寫版本。現在三份實作對同樣輸入算出來的結果剛好一樣,所以*現在*不會出錯;
但這正是今天整批缺陷共同的病灶——「同一件事好幾個地方各寫一次」。只要以後有人改
`_lint_cmd_with_files` 的跳脫規則(例如加一層路徑存在性檢查、或改成去重),冒煙跟規則索引這
兩處不會跟著變,會悄悄變回三套不同答案,而且現有測試(`t_pitfalls_lint_gets_the_changed_files`)
只餵了算風險分級那一條路徑,冒煙跟規則索引路徑沒有測試網接住這種分裂。換句話說,「不會再漏
第四個地方」這句話目前只對新加的那個呼叫端成立,對兩個既有呼叫端不成立——這道防線名不副實。

---

## D. 測試斷言在驗別的東西

沒有找到新實例。

用腳本抓全檔 `scripts/test_lumos.py` 裡每個 `write(v, "路徑", ...)` 造的節點/檔名,跟同一測試函式
內 50 行窗口內每個 `check(...)` 子字串斷言做交集,篩出 107 筆候選,逐一讀碼核對;另外額外手動核對
了全部 69 處 `run(v, "lint", ...)` 呼叫(`lint` 指令固定印節點路徑,是最容易踩到這個坑的高風險區)。
107 筆候選裡沒有一筆是真正「驗到不相干的東西」——多數是「斷言在確認某節點的名字/路徑真的出現在
過濾後的結果段落裡」,這是正確的身分核對,不是誤驗;有幾筆是啟發式腳本抓到的假陽性(子字串剛好
重疊但語意無關);還有一處(`t_doctor_about_code_not_linked`,約 `scripts/test_lumos.py:36994`)
是作者已經主動防過同一類坑的正確寫法(先把 stdout 切到只剩相關段落再驗,不會被別段的列舉打臉)。
唯一符合這個形狀的實例就是今天已經修掉、不用再報的那一個。

沒掃到的部分:非 `check(...)` 形式的直接 `assert`(若存在,沒有特別搜);以及子字串比對邏輯
藏在測試檔案裡的共用 helper 函式內、而非直接寫在測試函式本體裡的情況(啟發式腳本只看
write/check 出現在同一函式字面範圍內的重疊,抓不到透過 helper 間接比對的案例)。

---

## 掃描範圍總結

- **A 類**:全檔掃過。逐一核對了主程式裡目前全部約 50+ 處 `json.loads(line)` 逐行解析 jsonl
  帳本的分類/折疊邏輯(六本治理帳 + cascade jsonl),以及 frontmatter `type`/`status` 判斷、
  三個 JSON 設定檔(`lint.json`/`lint-waivers.json`/`rules/index.json`)的載入邏輯。沒有窮舉
  frontmatter 裡每一個欄位對(理論上組合很多),但覆蓋了所有「讀取端拿多個欄位當分類依據」的
  主要路徑。
- **B 類**:不是全檔語意關鍵詞窮舉,是先抓「空/一致/合法/完成/新/正規化」這些語意動詞出現超過
  一次的函式當候選,逐一核對判法是否一致,判法不同的才動態驗證。抓到一條真的(`_intake_declared`
  vs `_visible_lines`)。沒有系統性核對過所有「路徑相不相同」「時間戳誰比較新」這類判斷的每一個
  出現點,只挑了看起來像重複邏輯的候選。
- **C 類**:先抓程式裡帶「唯一實作/單一實作/呼叫端負責/不要在別處」這類警語的函式(約 50 處
  候選),逐一核對宣告的函式有沒有被所有相關呼叫端呼叫,抓到兩條真的(`_trusted_private_dir`
  的 vault-lock 缺口、`_lint_cmd_with_files` 的冒煙/規則索引缺口)。另外約 40 個「唯一實作」
  宣告(例如 `_visible_lines`/`_strip_inline_markup`、`_report_severities`、
  `atomic_write_verify`、`_impact_repo_files` 等)只看了函式定義沒有逐一列呼叫端核對;也沒有
  系統性窮舉「沒有警語但看起來像重複組字串」的模式,只挑了跟已知契約警語相關的候選。
- **D 類**:不可能對四萬兩千行逐條核對。用「測試自建的檔名/節點名 vs 斷言子字串重疊」的啟發式
  篩出 107 筆候選 + 額外手動核對全部 69 處 lint 指令測試,逐一讀碼判斷,沒有對每一條候選做
  實際的「拆掉驗證」翻紅實驗(讀碼已經足以判斷語意是「身分核對」而非「診斷關鍵字核對」)。沒
  掃到:非 `check(...)` 的直接 `assert`,以及子字串比對邏輯藏在共用 helper 裡而非測試函式字面
  範圍內的情況。
