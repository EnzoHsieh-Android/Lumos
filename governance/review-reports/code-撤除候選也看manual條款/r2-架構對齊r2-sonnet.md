severity: minor

## F1 計劃的 lands_in 只列「筆記內容閘」,說明卻寫進 lumos-cli-read
severity: minor
blocking: 否
引句:「lands_in:
  - Systems/筆記內容閘」
佐證:file: `docs/lumos-toolchain-knowledge/Projects/筆記測試綁定要存在_計劃.md:10`。這篇鄰居計劃的 lands_in 把 Systems/筆記內容閘、Systems/lumos-cli-read、Systems/bound-tests-gate 三篇都列了。
說明:專案規則要求計劃寫 lands_in(現況落在哪幾篇)。本案實際只改了 Systems/lumos-cli-read.md(同層 S20 的 WHY 都在那裡,位置對),Systems/筆記內容閘 沒動。所以 lands_in 列的那篇沒收到說明,收到說明的那篇沒列。欄位跟實際落點對不上,結構本身沒錯。

## 三問

**1. 分層與依賴方向:對齊。**
- 新函式 _ns_tr_manual_clauses 放在 _ns_tr_sub_says_retire 與 _doctor_test_ref_lines 之間,跟鄰居同一組 _ns_tr_* 輔助函式。
- 它只往下呼叫 _note_from_text、clause_bindings、slot_parse、_ns_tr_retired,只被 _doctor_test_ref_lines 呼叫。沒有跨層直呼。
- 引句:「rows = clause_bindings(text, {}, None, lambda _p: set(), lambda _p: "")」
- 對照:_ns_test_ref_lines 呼叫 clause_bindings 的參數一模一樣(都是空索引加純函式)。file: `scripts/lumos:31976` 起那段。
- 入口篩選只是在 _NS_TR_HAS_REF_RE 後面加 MANUAL_REF_RE,沒有另寫正則(file: `scripts/lumos:31906`、`scripts/lumos:5275`)。

**2. 命名與錯誤處理:對齊。**
- 命名沿用 _ns_tr_ 前綴與 cats["prose"] 輸出格式。
- 引句:「cats["prose"].append(_esc_clean(f"{rel}:{no}  條款仍掛 [manual:],下一層寫了撤除", _DOCTOR_LINE_MAX))」
- 錯誤處理是 try: … except Exception: return [],跟 _ns_test_ref_lines 的 except Exception: clause = set() 同一種寫法(file: `scripts/lumos:32010` 附近)。
- 輸出走 _esc_clean 與 _DOCTOR_LINE_MAX,跟旁邊 [test:] 那行一致。
- 摘要行檢查:新的 WHY 行有 [出處:] 和 [因:],修補後補上了「因」,通過。

**3. 第二種做法:沒有。**
- 修補前的版本是自己再解析一次:raw = _strip_inline_markup(lines[no - 1])[0] 加 MANUAL_REF_RE.finditer。這在 r1 是第二種做法,已被拿掉。
- 修補後改成直接取 clause_bindings 算好的 state。
- 引句:「if r.get("state") == "manual" and not all(v.startswith("已撤除") for v in r.get("manual") or [])」
- 這個「已撤除」開頭判法跟 _ns_tr_fix_retired 給的改寫建議 [manual:已撤除,見 …] 是同一種(file: `scripts/lumos:32026`)。
- ⚠ 同一篇筆記裡 clause_bindings 現在跑兩次,一次在 _ns_test_ref_lines、一次在 _ns_tr_manual_clauses。這只是重複呼叫既有函式,沒有新解析邏輯,不算第二種做法。

## 核對修補:口徑一致
- 修補後判「靠人驗」用的是 clause_bindings 的 state == "manual"。這個 state 由 manual = [… if len(x.strip()) >= _MANUAL_MIN_CHARS and re.search(r"[^\W_]", x)] 與 row["state"] = "manual" if manual else "untagged" 決定(file: `scripts/lumos:7210`、`scripts/lumos:7214`)。
- spec-trace 與 spec-gate 都用同一個 state(file: `scripts/lumos:7051`、`scripts/lumos:8012`)。所以「至少 4 字、含實字、同行有 [test:] 以 [test:] 為準」三件事,doctor 現在跟條款解析、spec-trace 一致。
- 測試也補了對應案例。
- 引句:「⑧同一行同時掛 [test:] 與 [manual:] → 只列一次(以 [test:] 為準)」
- 引句:「⑦[manual:] 太短(條款解析判成未標)」
- 殘留差異:入口篩選 MANUAL_REF_RE.search(text) 沒有長度限制,比 state 鬆。它只是預篩,真正判定仍交給 state,不影響結果。

不對齊共 1 條,其中 major 0 條
