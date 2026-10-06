severity: major

## 問 1 分層與依賴方向
差異把 c7 放進 drift 層(`scripts/lumos:34621` 一帶的 _drift_c6 / _drift_state_findings / _DRIFT_KINDS / _drift_fix_hint / doctor Z 段迴圈),這部分四處都照 c6 的先例,對齊。但提交前筆記形狀檢查那一層(`scripts/lumos:32358` cmd_note_shape 一帶)新增的 _ns_close_summary_hints 直接呼叫 drift 層內部:_drift_fm_end、_drift_pending_lines、_drift_pending_clauses、_DRIFT_SETTLED。我掃了 `scripts/lumos:30400-32520` 的 note-shape 區,既有程式沒有任何一處直呼 _drift_*,只在註解裡「照 _drift_xxx 的先例」(如 `scripts/lumos:31007`)。這是跨層直呼(⚠ 若編排者認為 _drift_* 本就是全檔共用工具則降 minor)。
引句:「    e = _drift_fm_end(lines)」

## 問 2 命名與錯誤處理
提醒字首「提醒:」、stderr、出錯只印一句且「不影響這道檢查的判定」,與 `scripts/lumos:32484` _note_shape_negation_emit、`scripts/lumos:31137` _ns_tag_hints_emit 一致。不一致處三點:
(a) 既有兩則提醒都記 note-shape/hinted 治理帳(`scripts/lumos:32499`、`scripts/lumos:31150`,且 ("note-shape","hinted") 在 `scripts/lumos:1323` 白名單),這則完全沒記,算不一致(minor):事後無法量這則提醒觸發了幾次、是否有效。
(b) 既有提醒把「蒐集」(_ns_*_collected)與「印出+記帳」(_*_emit)拆開,單一 try 只包印出;這則把查 git、算判定、印出全包進同一個 try/except Exception,出錯時可能已印了一半標題才報錯。
(c) 既有兩則提醒有 note_shape.* 設定開關(off/warn)與 doctor 一行說明;這則沒有關閉方式。
引句:「        print(f"提醒:結案時摘要的對照這次沒做成({e.__class__.__name__}),不影響這道檢查的判定", file=sys.stderr)」

## 問 3 第二種做法
(1) 讀上一版/暫存版:既有格子檢查用 `scripts/lumos:31484` _ns_base_summary_lines 走 _nodehome_cat_blobs(`scripts/lumos:29336`)批次讀、批次失敗回 None 讓呼叫端 fail-open;新碼對每篇各跑兩次 _lens_git show(`scripts/lumos:32396-32397`),N 篇 2N 個子程序,且以 `git diff --cached --diff-filter=M` 自己另列清單,另起一套讀版本的方式(major,第二種做法)。
(2) 摘要行切法:既有提交檢查用 _ns_summary_logical(`scripts/lumos:31338`,邏輯行,處理續行)比摘要;新碼用 _drift_pending_lines 的實體行並以 `osum == nsum` 整串相等判「沒動」,縮排或續行重排會被當成有改或沒改,與既有邏輯行口徑不同(minor,⚠ 交編排者看是否須統一)。
(3) 待定判定:沿用 _drift_pending_clauses(與 c6 同一套遮罩),未另起詞表,對齊。收尾值沿用 _DRIFT_SETTLED,對齊。
引句:「        old = _lens_git(root, "show", f"{base_where}:{path}", binary=True)」

## F1 note-shape 層直呼 drift 層內部函式
severity: major
blocking: 否
引句:「        nst, nsum = _ns_status_summary(new.stdout.decode("utf-8", "replace"))」

## F2 讀舊版/新版另起逐篇 git show,不走既有批次讀
severity: major
blocking: 是
引句:「        new = _lens_git(root, "show", f":{path}", binary=True)」

## F3 提醒沒記 note-shape/hinted 治理帳
severity: minor
blocking: 否
引句:「    ★只提醒,不改 rc、出錯只印一句★(結案通常只改狀態與正文,摘要是現況、最容易被忘)。只在提交前做(staged)。」

## F4 蒐集與印出沒拆開、無設定開關
severity: minor
blocking: 否
引句:「    except Exception as e:」

## F5 摘要比對用實體行相等,既有用邏輯行
severity: minor
blocking: 否
引句:「    return st, [ln for _no, ln, reg in _drift_pending_lines(text) if reg == "summary"]」

不對齊共 5 條,其中 major 2 條
