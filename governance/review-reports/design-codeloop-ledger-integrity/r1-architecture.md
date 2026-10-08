severity: major

凍結稿 SHA-256 已核對：`f66bd1107b9fa25523d4ee9517c9b038e9e9eb8260d22a88cedfd7f9f8cc2577`。本席唯讀審查，以下「現況」依程式路徑推演，未改檔執行交錯實驗。

## F1：沿用的過期鎖接手法無法保證單一持鎖者

severity: major  
blocking: 是  
引句:「沿用專案 `_excl_lock_try` 的獨佔鎖檔方法，以 `docs/.governance-log.jsonl.lock` 為同一鎖鍵」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`；`scripts/lumos:33854`

可重現輸入：先留一個超過 900 秒的鎖。A、B 都讀到它已過期；A 把舊鎖移走並建立自己的新鎖後，暫停 B 於 `os.rename` 前。B 接著會把 **A 的新鎖** 移走，再建立 B 的鎖。預期只有一人取得鎖；依現有 `_excl_lock_try`，兩人都可回 `True`，並同時寫治理帳。凍結稿把共用鎖作為 S2 的保證，但直接沿用此接手路徑無法達成。

## F2：新鎖檔會被 Git 視為未追蹤改動

severity: minor  
blocking: 否  
引句:「以 `docs/.governance-log.jsonl.lock` 為同一鎖鍵，等待上限 2 秒、鎖檔過期門檻 900 秒」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`；`.gitignore:14`；`scripts/lumos:21547`、`scripts/lumos:29982`

可重現輸入：寫者取得鎖後被強制終止，留下 `docs/.governance-log.jsonl.lock`；在 900 秒接手門檻前執行帶 lint 設定的 `pitfalls --diff HEAD~1..HEAD`。預期僅因程式改動計算新增 lint 命中；現有 `.gitignore` 不排除此鎖檔，`git status --porcelain` 因而非空，`_lint_aligned` 轉為未對齊，改成收取該次 lint 的全部命中。這會使與本次新增行無關的舊命中進入風險判定。

## 治理帳讀者

已讀無 finding；凍結稿要求共用完整 LF、嚴格 UTF-8、JSON 物件判準，未見架構上必須另建第二套解析法的缺口。

總結：2 條 finding，**blocking 1 條**。未修改任何檔案。