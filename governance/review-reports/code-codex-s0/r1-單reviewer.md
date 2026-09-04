# Codex 完全支援 S0 安裝層 — 第三方 code review(單 reviewer,r1-snapshot.patch)

審查對象:`governance/review-reports/code-codex-s0/r1-snapshot.patch`(對應 commit `8bbe680`)。
方法:逐 hunk 讀完整份 diff;所有可疑處另外用 `git worktree add --detach <tmp> 8bbe680` 建立一份與快照位元組相同的乾淨副本,在裡面實際執行/mutation-test 驗證,不受審查期間主工作樹持續被別人修改(觀察到 `scripts/lumos`、`scripts/merge-claude-settings.py`、`scripts/test_lumos.py` 在審查途中被即時改動,疑似另一輪修補正在進行)影響。所有 repro 指令都針對隔離 HOME 的臨時目錄,未動到本機真實 `~/.claude`、`~/.codex`。

---

## Findings

### F1 — `lumos install` 在 `~/.codex` 是檔案(非目錄)且 `codex` 在 PATH 時,整支指令未接住例外、直接崩潰

severity: blocker
blocking: 是
file: `scripts/lumos:11181`(`_codex_present` 的 PATH 後備判斷未與後面的 mkdir 共用同一個目錄存在性前提)、`scripts/lumos:11186`(崩潰點 `chooks.mkdir(...)`)、`scripts/lumos:10247-10249`(`cmd_install` 呼叫處,無 try/except)
引句:「if harness == "codex" and not _codex_present():」

`_codex_present()` 的判斷是「`~/.codex` 目錄在,或 `codex` 執行檔在 PATH」二選一為真即視為「有 Codex」,但緊接著 `_sync_global_hooks` 就無條件對 `Path.home()/".codex"/"hooks"` 呼叫 `mkdir(parents=True, exist_ok=True)`,完全沒有檢查 `~/.codex` 是不是已經以「檔案」型態存在。用隔離 HOME + 一支假的 `codex` 執行檔(只需要在 PATH 上,不需真的裝 Codex)重現:

```
$ echo "not a directory" > $HOME/.codex
$ HOME=$HOME PATH=<有 codex 的路徑>:$PATH python3 scripts/lumos install --force
...
  ✓ 全域 Claude hooks/settings.json 已同步(含清撤除的舊註冊)
Traceback (most recent call last):
  ...
  File ".../scripts/lumos", line 11186, in _sync_global_hooks
    chooks.mkdir(parents=True, exist_ok=True)
NotADirectoryError: [Errno 20] Not a directory: '.../.codex/hooks'
$ echo $?
1
```

`lumos enforcement`(`codex_ok = (home / ".codex").is_dir()`)與 `_teardown_global_hooks`(`if harness == "codex" and not chome.is_dir(): return True`)這兩個姊妹路徑都有先判斷「是不是目錄」才敢動作,唯獨 `_sync_global_hooks`(`install` 唯一入口)因為 `_codex_present()` 多了 PATH 後備條件,繞過了同一道防線,導致 S0 這支 PR 的核心動作(`lumos install`)在這個邊界輸入下整支崩潰、噴出原始 traceback,而不是像本 PR 其他地方(codex-cli 版本偵測、enforcement 讀 hooks.json)一貫的「每層各自 try 包住,一層壞不拖垮整份」風格。

---

### F2 — `lumos install` 的回傳碼恆為 0,即使 Codex(或 Claude)hook 註冊已回報 `merge-failed`

severity: major
blocking: 是
file: `scripts/lumos:10247-10258`
引句:「for _h in ("claude", "codex"):            # r3:接上契約,別無條件印成功;三態各印各的(r2 邊界 N2)」

`cmd_install` 迴圈裡呼叫 `_sync_global_hooks(_src_repo, _h)` 並印出對應三態訊息,但回傳值完全沒被接住判斷,函式結尾固定 `return 0`(`scripts/lumos:10258` 附近,`print(f"  {bindir} 已在 PATH...")` 後面就是 `return 0`,中間沒有任何 rc 累積)。用隔離 HOME、`~/.codex/hooks.json` 內容為 `{"hooks": null}`(合法 JSON、非法 schema,見 F3)重現:

```
$ HOME=$HOME python3 scripts/lumos install --force; echo "rc=$?"
...
  ⚠ 全域 Codex hooks:檔已 copy 但 ~/.codex/hooks.json 損毀、註冊沒更新——修好 JSON 再跑 lumos install --force
rc=0
```

畫面上明明印了 `⚠`,但整個 `lumos install` 仍宣告成功(rc=0)。任何腳本化 onboarding(CI、`lumos install && lumos doctor`)只看退出碼就會誤判裝好了。這與 PR 自己在 enforcement 設計文件裡強調的「fail-open 本身要能被觀測」精神相牴觸——這裡不是 fail-open,是 fail-silent(訊息印在 stdout/stderr,但退出碼撒謊)。

---

### F3 — `merge-claude-settings.py` 對「合法 JSON、但 `hooks` 不是 dict」的 schema 直接崩潰,teardown 因此假裝成功並漏剪懸空註冊

severity: major
blocking: 是
file: `scripts/merge-claude-settings.py:161`(崩潰點)、`scripts/lumos:11239` 附近(`_teardown_global_hooks` 只驗 JSON 語法、不驗 schema)
引句:「for event, entries in list(settings.get("hooks", {}).items()):」

`main()` 只 catch `json.JSONDecodeError`(語法錯誤),對於「語法合法但 `"hooks"` 是 `null`(或 list)」這種 schema 錯誤完全沒有防護——`settings.get("hooks", {})` 在 key 存在但值是 `None` 時回傳 `None` 而不是預設值 `{}`,`.items()` 直接 `AttributeError`。兩個重現(都在對應 r1-snapshot 的乾淨 worktree 上跑):

1. 直接跑合併器:
```
$ echo '{"hooks": null}' > $HOME/.codex/hooks.json
$ HOME=$HOME python3 scripts/merge-claude-settings.py --target codex
Traceback (most recent call last):
  ...
  File ".../merge-claude-settings.py", line 161, in _prune_dangling
    for event, entries in list(settings.get("hooks", {}).items()):
AttributeError: 'NoneType' object has no attribute 'items'
$ echo $?
1
```
這與文件宣稱的「壞 JSON 回 1 且訊息講『設定檔壞、修好再跑』」(`實作紀錄`)不符——這裡回 1 沒錯,但訊息是原始 traceback,不是那句友善訊息。

2. 透過 `_teardown_global_hooks(repo, "codex")`(teardown 會走這條路):
```
>>> m._teardown_global_hooks(repo, "codex")
Traceback (most recent call last):
  ...
AttributeError: 'NoneType' object has no attribute 'items'
  ✓ 全域 Codex hook 清理:無我方殘留
teardown result: True
```
`_teardown_global_hooks` 自己那道「先 `json.loads` 驗證可解析」的閘只擋語法錯,擋不住這種 schema 錯;`subprocess.run([...,"--prune-only",...])` 沒接 returncode,子行程崩潰的 traceback 直接洩到 stderr,但呼叫端照樣印「✓ 全域 Codex hook 清理:無我方殘留」且回 `True`——`~/.codex/hooks.json` 裡真正懸空的我方註冊完全沒被剪掉,卻回報成功。這正好打在計劃文件自己列的合約候選「install/teardown 對稱:Codex 三處在 teardown 後必為空」上。

---

### F4 — 新測試 `t_codex_enforcement_rows` 裡有一段 `and False` 的永假子句,讓它聲稱驗證的不變量實際上沒被測到

severity: major
blocking: 否(測試品質問題,不影響production行為本身;但「宣稱驗證的東西沒被測到」本身是這次審查的指定鏡頭)
file: `scripts/test_lumos.py:25001`
引句:「not any(r["status"] == "registered-trust-unknown" and False for r in rows)」

這行斷言掛在 `check("codex-enf: summary 分母排除 registered-trust-unknown", ...)` 裡。拆開看:
- `r["status"] == "registered-trust-unknown" and False` 對任何 `r` 恆為 `False`(`X and False` 恆假),`any(...)` 恆 `False`,`not any(...)` 恆 `True`——這個子句對每一列輸入都給同一個答案,不具鑑別力。
- 同一個 `check` 裡的 `t == len(rows) - u` 也不具鑑別力:`t`、`u` 是 `enforcement_summary(rows)` 的回傳值,而 `enforcement_summary` 自己的實作就是 `total = len(rows) - unknown`——用被測函式自己的公式去驗證被測函式自己算出來的值,恆真,不管「該不該把 `registered-trust-unknown` 排除在分母外」這件事算對還算錯。

用 mutation test 實證(針對 8bbe680 的乾淨 worktree,改完再還原,沒留痕):把 `enforcement_summary` 裡 `unknown = sum(1 for r in rows if r["status"] in ("unknown", "registered-trust-unknown"))` 改回舊版 `unknown = sum(1 for r in rows if r["status"] == "unknown")`(也就是刻意打破「排除 registered-trust-unknown」這條 S0 新加的不變量),重跑 `python3 scripts/test_lumos.py -k t_codex_enforcement_rows`:

```
  ✓ codex-enf: summary 分母排除 registered-trust-unknown
  ...
10 passed, 0 failed
```

被刻意打破的不變量,測試照樣全綠。這條 check 名字承諾的東西,目前沒有任何測試真的守著。

---

### F5 — `_link_or_copy_shared` 用 `is_symlink()` 判斷「是不是我方連結」,在 Windows junction 上會誤判自己裝的東西是「別人的目錄」,冪等重跑會卡住

severity: minor(範圍聲明「不做 Windows 的 Codex 路徑、只保證不炸」,這裡不炸只是行為錯,故不升級為 major)
blocking: 否
file: `scripts/lumos:11081-11094`
引句:「if dst.is_dir() and not dst.is_symlink():」

`scripts/lumos` 裡 `_link_or_copy`(既有函式,W4 註解,雖然該段註解文字本身不在這份 diff 的 hunk 範圍內,但同一支檔案裡明文記載且此 diff 直接依賴這個事實)明確指出 Windows 的目錄 junction 不會被 `Path.is_symlink()` 認出。`_link_or_copy_shared` 用「`is_dir()` 為真且 `is_symlink()` 為假」當作「這是別人手動放的真目錄,不能動」的判準——但 lumos 自己在 Windows 上裝出來的 junction 剛好符合這個條件(`is_dir()` True、`is_symlink()` False),於是:第一次 `lumos install` 建好 junction 沒問題;第二次(或任何之後)重跑 `lumos install`,`_link_or_copy_shared` 會把自己裝的 junction 誤判成「已有不是 lumos 裝的同名目錄」,印警告、跳過重建,失去冪等/自癒能力(內容仍會透過 junction 直接反映來源變動,不算資料損毀,但「跳過+警告」這行為本身就是錯的,且訊息會誤導使用者以為自己動過手)。新測試 `t_codex_skills_shared_dir` 對此明確標註 `if sys.platform == "win32": ...; return`(跳過不驗),所以這個路徑沒有機械覆蓋。

---

### F6 — `merge-claude-settings.py --target` 沒有值域檢查,拼錯字會靜默退回改 Claude 的檔

severity: minor
blocking: 否(內部呼叫點 `scripts/lumos` 一律傳字面 `"codex"` 或不傳,不會拼錯;只有人手動直接跑這支腳本才會踩到)
file: `scripts/merge-claude-settings.py:18-19`
引句:「TARGET = "codex" if "--target=codex" in sys.argv or ("--target" in sys.argv and」

這段判斷式是「等於 `--target=codex` 或 `--target codex`」才算 codex,其餘一律落回 `claude`——包含 `--target=coddex`(打錯字)、`--target`(漏帶值)這種情況。此腳本檔頭註解自己說「跟 scripts/install-hooks.sh 配合用」,是有公開介面預期的獨立腳本,值域檢查缺席意味著手動誤用時會在錯的檔(`~/.claude/settings.json`)上動手,而使用者以為自己在操作 Codex 那邊,不會有任何錯誤訊息提示。

---

### F7 — `hooks.json.bak`(及既有的 `settings.json.bak`)teardown/uninstall 都不清

severity: minor
blocking: 否(既有債務被沿用到 Codex 側,非本次新增的回歸;Claude 側同款問題本來就存在)
file: `scripts/merge-claude-settings.py:256`;`scripts/lumos` 全檔搜尋 `.bak` 找不到任何清理呼叫
引句:「backup = SETTINGS.with_suffix(".json.bak")」

合併器每次改動 `SETTINGS`(`~/.claude/settings.json` 或本次新增的 `~/.codex/hooks.json`)前都會備份成 `.json.bak`,但 `scripts/lumos` 整份檔案裡沒有任何地方會移除這個 `.bak`。這代表 review brief 點名的「teardown 對稱」在嚴格意義上本來就沒有做到 100%(裝過的機器跑完 teardown 之後,`~/.claude/settings.json.bak` 與新增的 `~/.codex/hooks.json.bak` 都會留下)。本次 diff 沒有讓它變得更糟(Claude 側原本就這樣),但也沒有藉著這次「補齊 Codex 對稱」的機會把它一起補上。

---

## 已驗證「沒問題」的邊界(供對照,不算 finding)

- `subprocess.run(["codex", "--version"])` 在 `codex` 不在 PATH 時丟 `FileNotFoundError`——已被 `enforcement_status` 裡外層的 `try/except Exception` 接住,不會讓整個 `lumos enforcement` 掛掉(F1 是另一個呼叫點 `_sync_global_hooks` 沒有等價保護,不要混淆)。
- `_link_or_copy_shared` 對「symlink 指向已刪除的目標」(dangling symlink)處理正確:`dst.is_symlink()` 對懸空連結仍為 True,會走到 `_link_or_copy` 裡的 `dst.unlink()` 分支正常重建,不會誤判成「別人的真目錄」。
- `_link_or_copy_shared` 對「dst 是空目錄」處理正確:`os.scandir` 判空之後會放行給 `_link_or_copy` 用 `os.rmdir` 清掉再建連結。
- POSIX(macOS/Linux)上 `_link_or_copy_shared` 的冪等性沒問題:真 symlink 會被 `is_symlink()` 正確辨識,F5 只在 Windows junction 上發生。
- AGENTS.md 的「空檔 / 只有標題 / 沒有任何標題」三種 `absent` 分支都不會崩潰,新測試 `t_codex_reinject_agents_targets` 對三種情境(有標題插入其後、無標題插檔首、再跑一次 unchanged)都有實際內容斷言(不是空殼測試),邏輯也與斷言吻合。
- BOM/CRLF 正規化是沿用既有 CLAUDE.md 的作法(讀入去 BOM、統一轉 LF,寫出強制 LF),不是這次新增的行為變化,對 AGENTS.md 一視同仁,沒有製造新的不一致。
- 五支現役 hook(`lumos-entry-hook.py` 等)全部不讀 `sys.argv`,`--harness codex` 尾碼確實如文件所述「無害」,`grep` 逐支核對過。

---

## 圖譜固定席逐條判定(LUMOS-IMPACT: Lumos/main..HEAD)

1. **Issues/hook卸載殘留註冊.md**[事故]——不影響。兩階段撤除(STUB 換殼、隔一版才真刪)的判斷邏輯(`_RETIRED_STUB_CLAUDE_HOOKS`/`_RETIRED_CLAUDE_HOOKS`)本身完全沒被改動,只是被同一支 `_sync_global_hooks`/`_teardown_global_hooks` 參數化套用到 `codex` harness,兩階段順序與判準都原樣保留。

2. **Issues/測試未隔離HOME刪掉真機Claude-hooks.md**[事故]——不影響。六支新 Codex 測試全部經由 `_codex_run` helper(subprocess + env 覆蓋 `HOME`/`USERPROFILE`)或既有 `_enforcement_fixture`(顯式傳入 `home` 參數,函式內部用該參數而非直接呼叫 `Path.home()`)取得隔離,沒有走會污染真機 `~/.claude`、`~/.codex` 的路徑;已用 `-k codex`(46 條)、`-k enforcement`(43 條)在乾淨 worktree 實跑,全綠,過程沒有動到本機真實家目錄。

3. **Systems/lumos-cli-lifecycle.md**★INVARIANT★(re-inject 只覆蓋 sentinel 之間 body、外部 byte-equal 保留)——不影響。`target=="CLAUDE.md"` 時三態分派(`absent`→接檔尾、`found`→splice-only)與改動前是同一段程式碼路徑,新增的 `target` 參數與 AGENTS 分支是額外的 `else`,不改變 CLAUDE.md 既有行為;`found` 分支的位移計算(`span.body_start`/`span.body_end`)沒有因為支援多目標而改變演算法本身。

4. **Systems/slim-install-安裝器.md**★INVARIANT★(7 條:CLAUDE.md 原地取代/檔首插入、冪等、FULL-BACKUP base64 位元組級還原、bin manifest、三層目標守衛、Windows 直譯器偵測、Windows shim 碰撞偵測)——不影響。全 diff 與現行 `scripts/lumos` 搜尋不到 `LUMOS-SLIM` 字樣,代表這批合約守的是另一套精簡版安裝機制(不在這份 diff 觸碰的程式路徑內);牽連檔清單把 `scripts/lumos` 列入,判斷只是粗粒度的檔案層級關聯,不是這幾條 INVARIANT 實際命中的程式碼行。

5. **Systems/slim-uninstall-一行卸載.md**★INVARIANT★(6 條:manifest 優先於 sha256 比對、四步驟互不阻擋、skill 目錄備份 `.bak.<timestamp>`、CLAUDE.md 位元組級還原、Windows shim 獨立判斷、manifest 自我清理)——不影響,理由同上(同一套 LUMOS-SLIM 機制,本 diff 未觸碰)。本次 `cmd_uninstall` 新增的 `~/.agents/skills` 清理走的是全新的 symlink/`.lumos-managed` 標記判斷,不是這批 INVARIANT 描述的 manifest/備份機制,兩者是平行、不重疊的清理邏輯。

6. **Systems/bound-tests-gate.md**★INVARIANT★——不影響。本節點守的是 code-loop 對固定席合約綁定測試的機械執行邏輯,本 diff 未修改該函式,只是新增了不相關的 Codex 安裝碼與測試(這些新測試本身會不會被 bound-tests-gate 正確認領/執行是另一個問題,但不影響 gate 本身的行為)。

7. **Systems/canary-audit.md**★INVARIANT★(2 條:record/second 落盤可讀回、second 純 telemetry 不影響 gate)——不影響。本 diff 未觸碰 canary 記錄或讀回邏輯。

8. **Systems/guard-kill.md**★INVARIANT★(2 條:rc 優先序、`--json` stdout 純淨)——不影響。本 diff 未觸碰 guard kill 相關程式碼。

9. 其餘「超出上限,只列名」節點(lumos-cli-read、slim-get-一行安裝、測試假綠形態、design-loop、lumos-deinit、pitfalls-code-loop、reversibility-governance-ledger、doctor-irreversible-hint、loop-convergence-recording、lumos-refcheck、check-t-sentinel、cochange-guard、check-r-guard、core-invariant-baseline、judge-severity-gate)——內容被截斷,只有節點名,沒有 KEY/INVARIANT 原文可供逐條比對,無法做出有把握的裁定。就 diff 實際改動範圍(skills 連結、hook 合併器、reinject、enforcement 新列)與這些節點名稱字面意思看不出直接程式碼交集,傾向判斷不影響,但信心低,僅供參考,不當作正式結論。其中 **lumos-deinit** 因為 `cmd_deinit` 確實呼叫了本次被泛化的 `_deinit_strip_claude`,已在上面 finding 與第 3 條裡實際驗證過對稱性與行為正確,若該節點藏有更細的合約條文,建議另外用 `lumos context lumos-deinit --brief` 查一次全文再覆核。

---

## 總結

max severity: **blocker**(F1)
blocking 條數:**3**(F1、F2、F3)
non-blocking 但值得修的:F4(測試永假子句)、F5(Windows junction 冪等)、F6(`--target` 值域)、F7(`.bak` 殘留)。

pitfalls manifest 0 條命中,以上全部由人工逐 hunk 讀取 + 對照 8bbe680 乾淨 worktree 實跑/mutation test 找出,非機械掃描產物。
