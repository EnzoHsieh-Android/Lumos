severity: major

R2-BND-1 Windows junction 會讓 deinit 穿出專案刪除外部 bytecode；屬修補造成。  
severity: major  
blocking: 是  
引句:「if cache.parent.is_symlink() or cache.is_symlink() or not cache.is_dir():」  
file: `scripts/lumos:21968`  
file: `scripts/lumos:22629`  
最小重現（已跑）：建立 `scripts/__pycache__ → external`，以 repo 已記載的 Windows junction 語意模擬 `is_symlink()==False`，呼叫 `_deinit_remove_bytecode` 後，外部 `test_quality.cpython-314.pyc` 被刪除。既有程式已明載「Windows junction 不被 is_symlink() 認出」，而新測試只覆蓋 POSIX symlink。這違反只清專案內 owned bytecode、保留連結外側內容的卸載邊界。

R2-BND-2 eval 結果目錄會漏掉 PHP 等已支援語言的真程式；屬修補造成。  
severity: major  
blocking: 是  
引句:「if file_mode == "100755" or kind == "ext":」  
file: `scripts/lumos:44074`  
file: `scripts/lumos:28654`  
file: `scripts/test_quality_scan.py:22`  
最小重現（已跑）：`_impact_diff_seed_ok("governance/eval/results/fixture/Test.php", "100644", None)` 回傳 `False`，同位置的 `test.py` 回傳 `True`。本 patch 把 eval 結果納入附件分類後，沿用的 `_NODEHOME_CODE_EXTS` 沒有 `.php`；修補前該路徑會落到一般程式的 `True`。這會讓 PHP 真碼失去 impact 種子、家與合約鏡頭。

R2-BND-3 無總數欄位的壞 JUnit 可把 suite 級 `<failure>` 驗成 passed；屬既有角落，本輪 F1 修補未封。  
severity: major  
blocking: 是  
引句:「observed[field] = sum(any(xml_tag(c) == tag for c in case) for case in cases)」  
file: `scripts/test_quality.py:43`  
file: `scripts/test_quality.py:158`  
最小重現（已跑）：exit 0 的可信命令輸出 `<testsuite><testcase classname="T" name="x"/><failure type="AssertionError">boom</failure></testsuite>`，再以 `capture --junit-stdout --target T::x` 收證；CLI 回 rc0、`status: executed`，並把 `T::x` 記為 passed。新增檢查只在總數屬性存在時比對，而且既有額外檢查只拒絕 suite 級 `error`，沒有拒絕孤立 `failure`。

R2-BND-4 Semgrep finding 的 `check_id` 型別錯誤會逸出 traceback；屬既有角落，抽函式後原樣保留。  
severity: minor  
blocking: 否  
引句:「if item.get('check_id', '').split('.')[-1] != 'same-comparison' or item.get('path') != str(source):」  
file: `scripts/test_quality_semgrep.py:28`  
file: `scripts/test_quality_semgrep.py:85`  
實測假 Semgrep 回傳頂層合法 JSON、但 finding 為 `"check_id": null`；`lumos test-quality scan --json` 回 rc1 與 `AttributeError` traceback，而非 rc2 的結構化 `complete:false`。結果沒有假綠，但破壞壞輸入的穩定輸出契約。

其餘逐 hunk 核對：

- core／scan／semgrep 缺檔 preflight、舊 `lumos --help`、共用 parser/namespace：已讀，無 finding。
- suite/root 總數矛盾、POSIX 取消清理、輸出上限、一般 owned bytecode、POSIX user/symlink、`.py`／可執行／shebang／未知 eval 種子：原問題控制均通過；除上述邊界外無 finding。
- `scripts/test_test_quality_cli.py` 33/33、`scripts/test_test_quality_scan.py` 21/21、兩個 `test_lumos.py` 接線案例皆綠。
- 模型 worker 的實作不在兩份指定 patch；只讀到控制案例，未用它宣稱無回歸。

前八篇固定席合約：

- `vendored測試套件在消費端假紅`：無正式 invariant；來源專用測試仍由 `_need_src` 跳過，無 finding。
- `lumos-cli-lifecycle`：re-inject sentinel 外 byte-equal invariant 未受影響；精確 vendor 白名單已含三個 test-quality 模組。
- `lumos-deinit`：junction 外側保留邊界受 R2-BND-1 影響。
- `lumos-cli-read`：search 作廢節點 invariant 與兩條有效 RULE 均未受影響。
- `bound-tests-gate`：閘本身未改；R2-BND-2 會在上游漏掉 impact 種子，間接使固定席與綁定測試無法進閘。
- `guard-kill`：兩條 invariant 與兩條有效 RULE 未受影響。
- `授權與歸屬`：白名單未含授權檔；三個 sidecar 均有 SPDX，兩條 invariant 無 finding。
- `測試假綠形態`：原修補控制確實能抓原問題；其覆蓋未包含 junction、PHP extension 與孤立 JUnit failure，對應上述 findings。

超出上限僅列名：`pitfalls-code-loop`、`design-loop`、`reversibility-governance-ledger`、`loop-convergence-recording`、`doctor-irreversible-hint`、`lumos-refcheck`、`check-t-sentinel`、`check-r-guard`、`節點範圍與索引守衛`、`cochange-guard`、`canary-audit`、`slim-get-一行安裝`、`slim-install-安裝器`、`slim-uninstall-一行卸載`、`規格落成可驗收條件_計劃`、`雙向門放行_計劃`、`引用座標依實際換行_計劃`、`逃逸自動記_計劃`、`異常派工單回報輸入錯誤_計劃`、`judge-severity-gate`、`core-invariant-baseline`。

已完整讀 `r2-runtime.patch`、`r2-scanner.patch`、`r2-repair-binding.json`、`r1-fix.json`、`r1-intake.md`、指定四篇圖譜與固定席鏡頭；未讀其他 r2 席報告。AGENTS 指向的兩篇試行／生效文件不在凍結樹，狀態未驗，未據此宣稱無回歸。

總結：最嚴重 severity=major，blocking=3 條
