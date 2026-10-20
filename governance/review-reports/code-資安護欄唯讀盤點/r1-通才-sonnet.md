severity: major

通才席的結論:這次改動沒有弄壞既有呼叫端,`_visible_lines` 的圍欄重構行為等價;但新測試漏掉三個守衛的驗證,拿掉實作測試照綠。

我跑了 `python3.14 scripts/test_lumos.py -k seclist`,203 全綠。另在 `/tmp/lumos-seat-work/code-資安護欄唯讀盤點/通才-sonnet/` 的複本上對實作做了 18 項拿掉實作的實驗,其中 14 項測試照綠,最有代表性的列在下面。

## findings

### 1. 列舉後開檔前把中間目錄換成捷徑,沒有任何測試守

severity: major
blocking: 是

- **位置**:`_secinv_open_rel` 逐層開目錄時帶的 `O_NOFOLLOW`。`_secinv_descend` 開子目錄那一處也是。S3 的置換測試只換「檔案」,沒換「中間目錄」。
- **問題**:計劃 S3 與讀取算法第 3 點要求「檔案或中間目錄符號連結」都拒讀、「不得讀取 repo 外哨兵」。測試的 `swapping` 只做 `swap.unlink()` 再 `os.symlink` 檔案。
- **具體例**:
  - 輸入:`Systems/Sub/N.md`。列舉後、讀 `Systems/A.md` 時,把 `Systems/Sub` 換成指向 repo 外 `outside/Sub` 的捷徑。
  - 預期:外部檔從沒被 open。
  - 實際:把 `_secinv_open_rel` 那行 `| os.O_NOFOLLOW` 拿掉,`test_lumos.py -k seclist` 仍是 203 passed, 0 failed。
- **重現**:用 `dswap.py`(同目錄)做。它在複本上,用跟 S3 一樣的 `os` 替身記錄 inode。原碼印 `sentinel inode opened: False`,拿掉 `O_NOFOLLOW` 的複本印 `sentinel inode opened: True`。
- **緩解與限制**:屬性比對(dev/ino/mtime)會讓外部內容不進解析、只回 `changed_during_read`,所以不外洩。但「零讀取」的條款被破、測試不報。
- **同族**:`_secinv_descend` 的 `O_NOFOLLOW`、`_secinv_lstat_rel` 也一樣沒人釘。拿掉 `_secinv_descend` 那個 `O_NOFOLLOW`,測試同樣照綠。

引句:「check("S3 開檔前置換:從沒開到外部哨兵", secret_ino not in opened_inodes and "SENTINEL-TWO" not in str(d2))」

### 2. 巢狀過深 JSON 的 `RecursionError` 處理沒有測試

severity: major
blocking: 是

- **位置**:`_secinv_parse_block` 的 `except RecursionError` 分支。
- **問題**:契約是「JSON stdout 始終僅一個可解析物件、壞輸入退出 2」。測試沒有任何深層巢狀輸入。
- **具體例**:
  - 輸入:`Systems/Deep.md` 內 `lumos-security-v1` 圍欄寫 200000 個 `[`(約 200KB,遠小於 2MiB 上限)。
  - 預期:`json_invalid` 加「巢狀太深」,退出 2。
  - 實際:原碼正確;把 `except RecursionError` 換成 `except ZeroDivisionError`,測試 203 全綠,但 CLI 直接丟 `RecursionError: Stack overflow ... while decoding a JSON array` 的 traceback,stdout 沒有 JSON。
- **同族**:`_secinv_enumerate` 的「目錄巢狀太深」分支也沒有測試。
- **違反的規則**:全域 CLAUDE.md〈修審查發現〉明列「巢狀深度」要先紅測試、要對大型與深層巢狀輸入跑一次檢查。

引句:「errors.append(_secinv_err("json_invalid", rel, line=line, detail="巢狀太深"))」

### 3. `unregistered_nodes` 與 inventory 驗證(`inventory_error`、覆蓋未知)完全沒有測試

severity: major
blocking: 是

- **問題**:輸出契約明列 `unregistered_nodes`,計劃也明寫「核可依據失效時 coverage=unknown,多份則列錯誤」。整份測試 patch 沒有 `unregistered_nodes`、`inventory_error`、`flag/security-relevant` 的斷言。S5 只測「缺 inventory」與「合法 inventory」。
- **具體例 A**:
  - 把 `_secinv_build` 的 `unregistered_nodes` 篩選改成 `if False]`,測試 203 全綠。
  - 真實行為:帶 `tags:` 區塊清單 `- flag/security-relevant` 但沒登記的 `Systems/Flag.md`,原碼會列出,拿掉就整欄空。
- **具體例 B**:
  - 把 `_secinv_inventory` 的 `ip = _secinv_inventory_problems(env, cand)` 改成 `ip = []`,測試 203 全綠。
  - 效果:`decision_ref` 指向不存在決策的 inventory 會被當成有效,覆蓋狀態變 `known_inventory`。原碼對同一輸入報 `inventory_error` 並維持 `coverage.status=unknown`(我用 `p2/kg` 實跑確認)。
- **影響**:覆蓋缺口是這個指令的主要價值。偽造的 inventory 會讓缺口被算成已知,而且沒有測試擋。

引句:「check("S5 缺 inventory:coverage.status=unknown", cov1.get("status") == "unknown" and cov1.get("inventory") is None, str(cov1)[:400])」

### 4. 計劃「鍵的必填規則」多項沒有反例

severity: minor
blocking: 否

下列各改壞一處,測試都是 203 全綠:
- `_SECINV_ID_RE.fullmatch` 改成 `.match`:id 只收 ASCII 的規則沒有壞 id 反例。
- `schema_version: true` 被接受(拿掉 `type(sv) is not int`):沒有布林或浮點版本的反例。
- `unclassified` 與其他關注面並存的檢查整段拿掉。
- `_sc_retire` 整段拿掉:retired 專屬鍵與必填規則沒有反例。
- `replacement_id` 指自己或不存在的 ID 的檢查拿掉。
- `exception.expires_on` 的真日期檢查拿掉。
- 控制項 `assets`/`surfaces` 指到 inventory 沒有的 ID 的檢查拿掉。

這些沒寫進 S1–S13,所以我評 minor,但都是計劃條文。難到的只有 id 字元集:id 會被印進文字輸出,目前靠 `_secinv_show` 跳脫兜底。

引句:「if not (isinstance(cid, str) and _SECINV_ID_RE.fullmatch(cid)):」

### 5. S10 一條斷言的名稱與實際判準不符,讀取長度上限的剩餘額度部分沒被釘住

severity: minor
blocking: 否

- **問題**:斷言名稱說「不超過剩餘額度+1」,判準卻是 `max(reads) <= 2 * MiB + 1`,跟剩餘額度無關。
- **具體例**:
  - 此時剩餘額度是 0,`SlZ.md` 被 `st0.st_size > remaining` 在讀取前擋掉,根本沒走到 `os.read`。
  - 把 `want = min(_SECINV_FILE_MAX, remaining) + 1` 改成 `_SECINV_FILE_MAX + 1`,測試照綠。
- **影響**:檔案在 fstat 之後、讀取之前長大的情境沒人測,斷言名稱還會讓人以為有測。

引句:「check("S10 總量超限時讀取請求不超過剩餘額度+1", reads and max(reads) <= 2 * MiB + 1)」

### 6. `t_seclist_integration_gaps` 沒有真的涵蓋母計劃六項整合反例

severity: minor
blocking: 否

逐項對照母計劃〈證據交接與首案整合驗收〉:
- **① 決策作廢**:有涵蓋「作廢」與「不存在」。母計劃的「缺少權限答案」這個待決狀態在盤點 schema 裡沒有對應。
- **② 重抄 oracle**:`I-ORACLE` 就是預設的 `_sl_ctrl("I-ORACLE")`,跟 S4 的 `P-1` 完全相同。它沒有建模「oracle 重抄」,只是在重驗 pass 映射 declared_only。
- **③ 缺身分被拒**:等同 S4 的 `PE-1`(pending 映射 incomplete)。母計劃要求的「A 合法操作成功」成對對照沒有。
- **④ 編譯錯/零案例**:等同 S4 的 `AB-1`。
- **⑤ 舊環境**:等同 S4 的 `ST-1`。
- **⑥ 清單完整但有未驗與過期例外**:fixture 的 `S-refund` 沒有任何控制項映射,不是「清單完整」。測試也沒斷言 `coverage`。退出碼 2 來自 ① 的引用錯誤,看不出 ⑥ 單獨的退出碼。
- 最後一條 `doc.get("security_verdict") == "not_assessed"` 是程式寫死的常數,抓不到任何錯。

結論:②③④⑤ 是 S4 的改名重測,新增覆蓋只有 ① 與 ⑥ 的一半。這不是壞測試,但它宣稱涵蓋六項,實際沒有。

引句:「check("整合② 重抄 oracle 的 pass 證據仍只 declared_only", _sl_rec(doc, "I-ORACLE").get("evidence_check") == "declared_only")」

## 被刪掉的行為:`_visible_lines` 重構

我把基準 `ec4c6307:scripts/lumos` 的舊 `_visible_lines` 取出,跟新版做差分模糊測試。範圍是 20 萬個隨機行序列,詞庫包含三反引號、波浪號、四反引號、縮排 3 與 4 格、tab、帶語言標記、結尾帶空白。`keep_fenced` 兩種都測,結果 0 筆不同。保護邏輯完整搬進 `_fence_regions`,S12 的手算期望也跟舊行為一致。

## 固定席節點逐條答覆

- **lumos-cli-read 的 ★INVARIANT★**(search 預設排除 superseded、不排除 stale):不影響。`security list` 自己列舉全部 Markdown(包含作廢筆記)、自己開檔,沒碰 search 的濾網;`_visible_lines` 的輸出經差分驗證不變。
- **design-loop 的 ★INVARIANT★**(處置閘第五步):不影響。這份 diff 不碰 `lumos loop`、處置閘或 `.patch` 判定。
- **lumos-cli-lifecycle 的 ★INVARIANT★**(re-inject 只覆蓋 sentinel 之間):不影響。`security` 子命令在 `main` 的 vault 選擇前就返回,沒有任何寫入(我實跑確認 vault 與 parent 都沒新檔)。
- **測試假綠形態的 ★INVARIANT★**(還原翻紅釘要有前置斷言):新測試大多有前置斷言,例如 S9、S10 的大小、S11 的 `fired`。但本報告第 1、2、3 條就是「拿掉實作仍綠」的缺口。
- **guard-kill 的 ★INVARIANT★**:不影響。
- **loop-convergence-recording、pitfalls-code-loop、reversibility-governance-ledger 的 ★RISK★**:只有 `scripts/lumos` 牽連。`_regular_own_fd` 新增的是可選參數 `dir_fd=None`,不給時仍是 `os.open(str(path), flags, mode)`,既有呼叫端行為不變。
- **其他只列名的節點**:沒有找到 diff 在行為層碰到它們的證據。

## 善後

我跑 `-k seclist` 的拿掉實作實驗時,紅的場次留下 4 份 `gctl-run-*` 現場。確認沒有程序開著後,已用字面絕對路徑刪除。`/private/tmp/lumos-seat-work/code-資安護欄唯讀盤點/通才-sonnet/` 還在(`m/`、`p1/`、`p2/`、`dswap-*`、`old_lumos.py`、`mut.py`、`dswap.py`、`fuzz.py`),請編排者收貨後刪。

最嚴重 severity: major,blocking 共 3 條
