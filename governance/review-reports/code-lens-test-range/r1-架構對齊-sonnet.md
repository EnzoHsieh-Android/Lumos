severity: minor

## 問 1 分層與依賴方向
新測試與改動都留在 `scripts/test_lumos.py`,呼叫既有的 `_lens_smallest_commit`(`scripts/test_lumos.py:16806`)與 `_SrcOnly`(`scripts/test_lumos.py:129`),沒有跨層直呼。守衛測試放在輔助函式正上方、跟同族測試相鄰,可接受。筆記寫回走 Systems 節點的 PITFALL 行,與同檔既有格式相同。結構一致。

## 問 2 命名與錯誤處理
測試名 `t_lens_tests_avoid_branch_dependent_range` 符合 `t_*` 慣例。拿不到範圍時拋 `_SrcOnly`,與前例 `t_lens_timeout_keeps_warming_cache`(`scripts/test_lumos.py:16876`)相同。有兩處不一致。

## F1 守衛缺「現場成立」前置斷言
severity: minor
blocking: 否
引句:「        if '"dispatch-lens"' not in f or "Path(GRAPHCTL).resolve().parent.parent" not in f:」
前例習慣在斷言前先用 check 證明掃描現場成立,見 `scripts/test_lumos.py:16863`(`★前置★ 現場成立`)。本守衛直接判「bad 為空」。若兩個篩選字串日後改名,篩選結果會變成零支,守衛恆綠。專案自己的 `t_lens_recount_tests_guarded`(`scripts/test_lumos.py:44930`)也沒有前置,所以只列 minor。

## F2 範圍計算複製兩份,而前例是用本地 sha() 小函式
severity: minor
blocking: 否
引句:「    _base = _sp.run(["git", "-C", str(repo), "rev-parse", "--verify", _head + "~1^{commit}"],」
同樣六行在 `t_codex_s1_lens_arm_claim` 與 `t_codex_s1_r1_fixes` 各貼一份。前例用函式內的 `sha(ref)` 取 base(`scripts/test_lumos.py:16833`)。結構仍是同一個 helper,所以不算第二種做法。變數用底線前綴 `_head`、`_base`,前例用 `head`、`base`,是小差異。

## 問 3 第二種做法
沒有。範圍挑選沿用 `_lens_smallest_commit`。原始碼掃描用 `Path(__file__).read_text` 是同檔既有手法(`scripts/test_lumos.py:44938`、`scripts/test_lumos.py:51531`)。切函式的方式有差異:守衛用 `re.split(r"(?m)^(?=def )", src)`,鄰居 `t_lens_recount_tests_guarded` 用 `re.finditer(r"\ndef (t_\w+)\(\):\n(.*?)(?=\ndef |\nif __name__)", src, re.S)`。目的相同、寫法不同,同檔也沒有統一輔助函式可用,⚠ 判為不算第二種做法,屬於風格差異,不列為發現。

不對齊共 2 條,其中 major 0 條
