severity: major

# 架構對齊審查——clause_bindings(r1,sonnet)

被審:`governance/review-reports/code-clause-bindings/r1-snapshot.patch`(scripts/lumos + scripts/test_lumos.py + 圖譜/skill 文檔)。
只判「跟既有做法一不一致」,不找 bug、不評風格。

---

## 1. 分層與依賴方向

**判定:不對齊(1 條 major)。**

對齊的部分先講:`clause_bindings(text, split, default, methods_for, hay_for)` 是純函式,不做 I/O,參數形狀完全照抄 `_classify_one(x, split, default, methods_for, hay_for)` 與 `_platform_test_index` 回傳的 `(split, default, methods_for, hay_for)` 四件套——這是既有的「index 先建好、純函式再吃」分層,新函式照做:

> 引句:「def clause_bindings(text, split, default, methods_for, hay_for):」

`_clause_bindings_for(env, text, root=None)` 扮演的是 env→index 的轉接層,對應 `classify_invariants(env)` 用 `_repo_root_from_env(env)` + `_platform_test_index(repo_root)` 建 index 再逐條丟給純函式的既有分層——這一半對齊。

不對齊的地方在 repo 根的**取捨優先序**。這個 repo 對「顯式 root/repo 覆蓋 vs env 反推」的既有慣例,全部是「顯式的贏,env 反推只是預設值」,例如 `_loop_status_disposal` 呼叫端自己:

file: `scripts/lumos:6701-6703`——`_dsp_root = Path(repo).resolve() if repo else _vault_repo_root(env)`,註解明講「顯式 --repo 覆蓋(r3 s2 席:git-less 部署副本裡 .git 不在,向上找會落錯根——給使用者一條明路)」。同款寫法在 `scripts/lumos:559/600/6440/6716/6745/6801/6853/10361/13715` 等十餘處全部一致:`repo`/`root` 給了就贏,`_vault_repo_root(env)` 只在沒給時墊底。

新的 `_clause_bindings_for` 把這個優先序**倒過來**:

> 引句:「rr = _vault_repo_root(env) if env is not None else Path(root or ".")」

只要 `env` 不是 None,傳進來的 `root` 就整個被無視,一律重新用 `_vault_repo_root(env)` 反推。而 `_disposal_clause_step(rows, spec, root, env, ...)`(`scripts/lumos:13422`)呼叫它時是 `_clause_bindings_for(env, text, root=root)`——兩個參數同時給,`root` 是呼叫端(`_loop_status_disposal`)已經照上面「顯式覆蓋優先」規則算好的 repo 根(可能來自使用者的 `--repo`,正是為了 git-less 部署副本量身打的逃生口)。但因為 `env` 幾乎必存在(CLI 路徑一律傳真 `Env`),這個已經算好、可能是使用者顯式指定的 `root` 在條款綁定這一步會被靜默丟棄,改用重新反推的 `_vault_repo_root(env)`——在 git-less 部署副本這個既有註解明講的場景下,兩者可能不同,結果是條款綁定步驟悄悄用錯 repo 根建測試索引(索引建不起來或建到別的 repo),而 disposal 閘的其他四步(①-④)用的是使用者真正指定的那個根。同一次問閘、五個步驟看不同的「repo 根」是什麼,是這裡唯一具體的分層問題。

- severity: major
- blocking: 是

---

## 2. 命名與錯誤處理

**判定:不對齊(2 條 minor)。**

對齊的部分:`_clause_bindings_for` 的 `except (ValueError, OSError)`、`clause_bindings` 裡 `resolve_test_refs` 的 `except ValueError: row["state"] = "bad-name"`,都是窄捕捉、不吞 `Exception`,跟 `_classify_one` 的 `except ValueError: return "dangling"` 是同一套錯誤處理風格:

> 引句:「回 "fail" / "ok" / "skip",自己印一行 [disposal] 條款綁定。」

spec-trace 索引建不起來時印 `提醒:...` 到 stderr、不擋(rc 仍看 untagged),這跟既有 `bound-tests` 指令「range-unavailable」的「提醒:...這次沒跑合約測試」是同一種「失敗隔離、不跟真沒事混在一起」的講法,這一段對齊。

不對齊 #1——**`cmd_spec_trace` 的 docstring 沒跟著改**。函式簽出的 rc 語意已經從「舊制認領」改成「有沒有 untagged」,程式碼確實改了:

> 引句:「return 1 if untagged else 0」

但函式頭的說明字串沒有同步,現在讀起來還是舊制的字面意思:

> 引句:「rc:全認領=0;有未認領=1;計劃無 [SN] 標記=0(opt-in 未啟用)。唯讀。」

「全認領/有未認領」講的是舊制(Verification 回指認領),不是新裁決(條款行綁 `[test:]`/`[manual:]`)。這篇 patch 自己的決策記錄裡明寫「★裁決改綁定★」是這次改動的核心語意變更,函式的自我文件卻沒有跟著訂正,讀者只看 docstring 會判斷錯 rc 觸發條件。

- severity: minor
- blocking: 否

不對齊 #2——**同一種錯誤(`--spec` 讀不到)在同一個函式裡被兩種嚴重度處理**。`_loop_status_disposal` 既有的 G3 步驟遇到 `--spec` 檔案讀不到是當成用法錯誤,直接 `擋下` 並整個函式 `return 2`:

file: `scripts/lumos:13522`——`print(f"擋下:--spec 指的文件讀不到({e}),確認路徑對不對:\n    {spec}", file=sys.stderr)` 緊接 `return 2`。

新的第五步遇到完全同一類失敗(計劃檔讀不到),處理方式改成軟性的「這一項算 FAIL」,不中斷函式、只是併進 `fails` 清單,最終跟其他項一起決定 rc1:

file: `scripts/lumos:13440`——`print(f"[disposal] 條款綁定: ✗ — 計劃讀不成文字({e.__class__.__name__})")`,之後 `return "fail"`,由呼叫端 `fails.append("條款綁定")`(`scripts/lumos:13753`)。

同一個 `spec` 參數、同一種「檔案讀不到」失敗,在同一支函式裡一個是「參數錯誤,rc2 立刻結束」、一個是「處置未過,rc1 繼續跑完其他步驟」——語意不一致(雖然實務上 G3 通常會先攔到,這裡是描述兩套規則本身不一致,不是說一定會被同時觸發)。

- severity: minor
- blocking: 否

---

## 3. 第二種做法

**判定:不對齊(1 條 major、2 條 minor)。**

對齊的部分:`_disposal_clause_step` 抽成獨立函式、回字串狀態讓呼叫端決定要不要 `fails.append`,這個做法有既有先例——`_intake_dir_status(repo_root, loop_id)`(`scripts/lumos:4762`)一樣是回傳列舉字串(`"no-dir"`/`"missing"`/`"ok"`),讓 `_loop_status_disposal` 自己判斷要印什麼(`scripts/lumos:13743-13748`)。不是憑空發明的第三套抽函式方式。

不對齊 #1(major)——**`[manual:]` 對「同一個標記家族」的宣稱與實作不一致**。新常數的註解明講它跟既有的 `[test:]`/`[audit:]` 是同一家族:

> 引句:「跟 [test:]/[audit:] 同一個標記家族(條款綁測試算進度 S1)」

但這個 repo 對「合約軸標記家族」有清楚的既有慣例:同家族的標記共用一個聯集正則、被同一支函式一起剝除——`TEST_REF_RE`/`AUDIT_REF_RE` 都收進 `INV_TAG_RE`,`strip_test_refs`(`scripts/lumos:3376-3378`)靠 `INV_TAG_RE` 一次剝乾淨:

file: `scripts/lumos:3036`——`INV_TAG_RE = re.compile(r"\[(?:test|audit|kill|src|git):\s*[^\]]+\]")`(含 test/audit/kill/src/git 五種,唯獨沒有 manual)。

而真正「另立門戶、不算進合約軸」的標記,這個 repo 的既有慣例是給它一條清楚的分隔註解,例如可逆性軸:

file: `scripts/lumos:3381`——`# ── 可逆性軸(獨立於 ★INVARIANT★ 合約軸;走平行函式,不碰 extract_contracts/INV_TAG_RE)──`,底下才定義 `ROLLBACK_REF_RE`/`GUARD_REF_RE`(`scripts/lumos:3384-3385`);regen 軸(`SRC_REF_RE`/`GIT_REF_RE`,`scripts/lumos:3390-3391`)也是同款「先宣告獨立、再定義」。

`MANUAL_REF_RE`(`scripts/lumos:4085`)兩邊都不是:它宣稱「同家族」卻沒被收進 `INV_TAG_RE`(意味著哪天真的有人在 ★INVARIANT★ KEY 行寫 `[manual:...]`,`strip_test_refs` 產出的「乾淨宣稱文字」會留下這段標記,污染 Check T/guard list 的顯示與比對),而它的定義位置也離 `TEST_REF_RE`/`AUDIT_REF_RE` 那一叢(`scripts/lumos:3027-3037`)很遠、挨著 `SPEC_CLAUSE_RE` 落在別的區塊(`scripts/lumos:4084-4089`),沒有比照獨立軸拿到一條「這是平行家族,不碰 XXX」的宣告註解。結果是第三種、含混的處理方式:文字上認親,結構上沒收編,物理位置上也沒有按「獨立軸」慣例標明。目前 `[manual:]` 只用在計劃 `[SN]` 條款行、還沒有人把它寫進 ★INVARIANT★ KEY 行,所以還沒有真的炸,但這正是「這算不算同家族兩種處理」這題要問的東西,而答案是:是。

- severity: major
- blocking: 是

不對齊 #2(minor)——**「不回溯」cutoff 常數的日期取捨跟既有同款常數矛盾**。這個 repo 已經有一個「生效日只給讀側判新舊帳」的既有常數與明確設計原則:

file: `scripts/lumos:4738-4741`——註解「設隔日不設當日:合入日(08-26)白天經舊碼寫入的帳列若被標『寫側 bug』是誤告——日粒度切不開同日先後,保守往後推一天」,常數本身 `_SEV_WRITESIDE_CUTOFF = "2026-08-27"`(合入隔日,不是合入當日)。

新常數選了合入「當日」而不是隔日:

> 引句:「處置閘的條款綁定步只看首筆帳在這天(含)之後的迴圈——不回溯舊迴圈(週跑回放會重跑閘,回溯=舊判定全翻)」

即 `_CLAUSE_GATE_SINCE = "2026-09-08"`(今天),而不是隔日 `"2026-09-09"`。它踩的正是 `_SEV_WRITESIDE_CUTOFF` 那條註解要迴避的同一種歧義:今天白天、部署前用舊碼寫的第一筆帳,日期字串一樣是 `"2026-09-08"`,`first_ts[:10] < _CLAUSE_GATE_SINCE` 判不出「部署前/部署後」,會被誤判成「已經在新制之內」而被擋。同一個 repo 對「怎麼設不回溯的 cutoff」已經有一次踩坑後定案的規則,這次沒有沿用,也沒有解釋為什麼這裡可以不用管同日歧義。

- severity: minor
- blocking: 否

不對齊 #3(minor)——**同一句提醒,在同一個功能裡用了兩種呈現方式**。「條款沒標」這件事需要跟使用者講「為什麼在意」+「怎麼補」,`_disposal_clause_step` 的 FAIL 分支把這兩件事拆成兩行印,第二行還用既有的縮排延續慣例(比照 `_loop_status_disposal` 別處「  多席審查…」那種縮排子行):

> 引句:「每條要嘛在那一行綁 [test:測試名],要嘛寫 [manual:一句怎麼驗];沒有測試可掛也得講清楚靠人怎麼驗」

`cmd_spec_trace` 對完全同一件事(有 untagged 條款)卻把「為什麼在意」跟「怎麼補」揉進同一句、同一行印出:

> 引句:「未標的條款沒人能機械判它做到沒——要嘛在那一行綁 [test:測試名],要嘛寫 [manual:一句怎麼驗];設計審處置閘會擋。」

同一個新功能、同一份 patch,對「條款沒標怎麼辦」這句提醒用了兩種排版邏輯(分兩行 vs 揉一行)。不是白話三段式本身被違反(兩處都有講到「為什麼」跟「怎麼做」),而是同一件事在同一份改動裡沒有統一寫法。

- severity: minor
- blocking: 否

---

## 小結

不對齊共 6 條,其中 major 2 條。
