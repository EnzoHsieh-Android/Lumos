severity: minor

## F1 同時掛 [test:] 與 [manual:] 的條款被列兩次
severity: minor
blocking: 否 — 只是提醒段(不計入問題數)的重複與計數膨脹,不影響擋放行
引句:「for no in _ns_tr_manual_clauses(rel, text):」
`_ns_test_ref_lines` 那支迴圈與新的 manual 迴圈互不排除:定義行有真 [test:] 名、也有非「已撤除」的 [manual:] 時兩邊都成立。
最小重現(已跑):計劃寫 `- [S1] 當 x 時應 y [test:test_alive] [manual:看畫面]` 下一層 `  - 裁定:撤除`,`_doctor_test_ref_lines(e, root)["prose"]` 回兩筆:「條款仍掛 [test:]…」與「條款仍掛 [manual:]…」,同一行,標題「N 條」也多算一條。clause_bindings 自己的規則是「同時有就以 [test:] 為準」,這裡沒跟。
file: `scripts/lumos:7229`(clause_bindings 的「靠人只在沒測試時成立」文件句)。修法:manual 迴圈跳過 `_ns_test_ref_lines` 已列的行號。
新測試沒有「同行兩者並存」案例,所以照綠(⑥只驗單列格式)。

## F2 [manual:x] 太短也會被列,與 clause_bindings 的 manual 判定不一致
severity: minor
blocking: 否 — 只多列候選,提醒性質
引句:「if any(v and not v.startswith("已撤除") for v in vals) and not _ns_tr_retired(slot_parse(raw)):」
clause_bindings 規定 manual 要 ≥ `_MANUAL_MIN_CHARS` 字且有實字才算「靠人」(否則是 untagged),新函式只判非空。已跑:`[manual:x]` + 下一層「裁定:撤除」會列出,而同一條在 spec-trace 是 untagged。註解宣稱「同一支 clause_bindings 取定義行」但 manual 值判定另寫一套。
另:`[status:superseded]` 只寫在反引號裡時,此處用已剝行內碼的 raw 做 slot_parse 所以不認(照列),而 [test:] 那支用未剝的行,兩邊對「已標作廢」可見性不同(已跑 status_in_code 照列);偏安全方向,不算 finding。

## 已讀無 finding
- 未閉合反引號、行內碼內的 `[manual:x]`:引句:「raw = _strip_inline_markup(lines[no - 1])[0] if 0 < no <= len(lines) else ""」,已跑 codespan/unclosed 皆不列,正確(寧可少認)。
- `[manual: 已撤除,…]`(冒號後空白)與空 `[manual:]`:MANUAL_REF_RE 的 `\s*` 加 strip,已跑皆不列;`[manual:已撤除]` 與別的 manual 並存則照列,合理。
- [manual:] 寫在條款下一層而非定義行:引句:「defined = sorted({r["line"] for r in clause_bindings(text, {}, None, lambda _p: set(), lambda _p: "") if r.get("defined")})」,只看定義行,已跑 manual_on_child 不列,符合設計。
- 非計劃類筆記與摘要裡的 [SN]:引句:「if _note_from_text(rel, text).fields.get("type") != "project" or "[S" not in text:」,非 project 直接回空;摘要區的 [SN] 不是 body 行,clause_bindings 照既有規則。
- clause_bindings 丟例外:引句:「except Exception:」→ 回空,fail-open;但靜默吞錯,與既有 _ns_test_ref_lines 同款,不另標。
- 大型計劃成本:入口篩選只對含 [test:] 或 [manual:] 的筆記放行,project 且有 "[S" 才多叫一次 clause_bindings(線性、純函式、傳空索引不建真索引),每篇至多約 2 到 3 次,全庫掃可接受;未做實測,不標。
- 入口篩選放寬:引句:「if not text or not (_NS_TR_HAS_REF_RE.search(text) or MANUAL_REF_RE.search(text)):」,只掛 [manual:] 的筆記現也進 _ns_test_ref_violations,但它只處理 [test:]/[test-gone:],無此類標記就沒產出,無新誤報。
- 資料狀態五問:空(無 [S]/無 manual)→回空;單筆→列一筆;多筆→各列;重複(同行 test+manual)→見 F1;壞資料(未閉合反引號、clause_bindings 例外)→不列不崩。
- 新測試是否改壞既有:引句:「def t_doctor_s20_prose_retire_manual():」是新增函式,未動既有案例,既有 t_doctor_s20_prose_retire_by_verdict_verb 不受影響;提示文字改動(增「,」)若有測試逐字比對修法字串才會受影響,本審未跑全套。

總結:邏輯大致正確,僅有同行並存重複列與短 manual 判準不一的小問題。
