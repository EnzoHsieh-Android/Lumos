severity: minor

我逐 hunk 走過掛鉤與 lumos 的改動,沒有找到會做出錯行為的輸入。能擋下的洞都有測試把關;剩下兩條只是措辭不一致。

**實跑與變異驗證**
- 在 `/Users/enzo/orca/workspaces/lumos-toolchain/push-subset` 跑 `-k prepush_feature_branch`,16 條全過。`t_pitfalls_pushed_mainline` 9 條、`t_pitfalls_suite_computed` 3 條也全過。
- 變異在複本裡做,原 repo 沒動。我拿掉降級條件裡的 `"pushed_mainline": *false`,`t_prepush_feature_branch_*` 6 支變紅(10 過 6 敗)。這是 [S1] [S2] [S3] [S6] [S7] [S8] 共同守的那道檢查。
- 拿掉 `"suite_computed": *true` 那一條,`t_prepush_feature_branch_failclosed` 紅。這是 [S2] 的「算不出範圍照全套」。
- 第三個變異(把「沒有 pushed_mainline」也當成可降級)因為我改壞了續行語法,連正常案例都紅,沒有判別力,不採信。

**[S1]–[S8] 與失敗往全套走**
- pitfalls 失敗、`pf_json` 空、舊版 lumos 沒欄位:降級要同時讀到 `pushed_mainline: false` 和 `suite_computed: true`,缺任何一個都留在 full。
- `_pitfalls_pushed_mainline` 拋例外時,pitfalls 在印 JSON 之前就掛掉,`pf_json` 變空,所以不會誤降。
- 多個 ref:`_SUITE_FULL` 是「任一為全套就全套」的 OR。混推 main 時整次判 full、不印降級那行,不會被最後一個 ref 蓋掉。
- 本機 sha 全 0 的刪除分支被 `continue` 跳過。標籤和空字串回 true,走全套。
- 新分支首推用 `_brange`,`git diff` 對空樹正常;`_diff_range_ends` 取終點是 sha,不會是 None。
- `"computed": True` 在 `_test_suite_for_range` 所有 return 點都有設,`.get("computed", True)` 預設值用不到。
- 舊掛鉤配新 lumos:舊掛鉤不帶旗標,`pushed_mainline` 不出現,全套。新掛鉤配舊 lumos:探測不到 `dest="pf_pushed_ref"` 字樣就不帶旗標,避免 argparse 拒絕。
- 直接 grep 比對 JSON:被審分支內容裡的字串在 JSON 裡會被跳脫成 `\"`,偽造不了 `"pushed_mainline": false`。

**finding 1**
severity: minor
blocking: 否
全套那兩句提示仍寫「嫌久可 --no-verify,CI 會兜底」
引句:「echo "推送前先跑全部測試(約 8 分鐘;嫌久可 --no-verify,CI 會兜底)…" >&2」
`scripts/hooks/pre-push:974`、`scripts/hooks/pre-push:976`
設計做法 3 和說明文字都寫要拿掉這句,實作只改了子集分支那句。推 main 判全套時會印出這句,等於勸人跳過掛鉤。推 main 確實有主線 CI,不會做出錯的操作,所以不到 major。

**finding 2**
severity: minor
blocking: 否
放行理由文字自相矛盾
引句:「函式本身分支數沒變(_pitfall_diff_mode 多一個 if,cmd_pitfalls 零)」
`.lumos/lint-waivers.json` 新增的兩條 C901 放行
理由一句話裡說「分支數沒變」,括號裡又說 `_pitfall_diff_mode` 多了一個 if。放行本身仍成立(既有複雜度告警本來就在),只是理由文字不精確。

**弱點(講不出具體改壞,不算 finding)**
- 「迴圈後只印一次」只用單一功能分支 ref 驗。要把訊息搬進迴圈,必須同時引用迴圈後才定義的 `_suite_mode`,在這份掛鉤裡很難成為一個合理的改壞。
- [S8] 測試註解說「高風險提醒照印」,但斷言只驗證純文件推送仍判 docs。這間接證明 `pf_json` 不是空的,但沒有直接驗證高風險提醒。

**圖譜固定席**
- 我沒逐篇讀那 8 篇固定席節點,這部分沒有逐篇判。
- 我只確認這份 diff 沒碰 `Systems/bound-tests-gate`、`Systems/pitfalls-code-loop` 的合約行。這兩篇只在摘要裡補了說明和 WHY 行。

**manifest**
manifest 只有 `test_lumos.py` 上既有的 ruff 項(E702、E741、B023 等),都落在這次沒動的舊行,判誤報。

**清理**
我自己的臨時目錄 `/tmp/lumos-seat-work/code-推送只跑受影響測試/正確性-sonnet` 和三份 `gctl-run-*` 現場都已用字面路徑刪掉。
