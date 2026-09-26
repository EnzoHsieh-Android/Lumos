severity: minor

## F1 `--withdraw` 混用旗標的擋檢查,給空字串會被當成沒給、悄悄放行
severity: minor
blocking: no
引句:「擋下:--withdraw 只能跟 --reason、--withdrawn-by 一起給,不能混記帳參數、--repo、--list 或 --auto(以免你以為做了兩件事)」
file: `scripts/lumos:9594`(`if auto or list_mode or withdrawn or any(x not in (None, "") for x in others):`)、`scripts/lumos:9651`(`others=(loop_id, stage, severity, desc, defect_ref, rule, git_range, sha, missing_ref, repo)`)

判斷式 `x not in (None, "")` 把「沒給這個旗標」(None)跟「給了空字串」("")當同一件事,兩者都不會觸發混用擋檢。等於這道擋只防「給了非空值」,防不了「給了空字串」——而後者在 shell 腳本裡很常見(變數沒設到值就內插出空字串,例如 `--stage "$STAGE"` 而 `$STAGE` 剛好是空的)。實際擋不到的話,`--withdraw` 照樣成功,呼叫者不會被提醒「你多給的那個旗標被吃掉了」,牴觸這行擋檢自己寫的理由「以免你以為做了兩件事」。

重現(在 exp2-邊界/ 下用複製的 scripts/lumos 對著暫存 vault 跑,不動 repo):
```
python3 scripts/lumos --vault <vault> loop escape --withdraw ESC-A --reason "理由夠長了" --withdrawn-by t --stage ""
```
實跑結果:rc=0、印出「✓ 撤回 ESC-A:...」,撤回照樣成功,`--stage ""` 完全沒被擋下也沒有任何提示——跟同一段程式碼里 `--stage CI`(非空值)會被擋下(S19 既有測試,`r2-snapshot.patch` 第 469–476 行)行為不一致。`--sha ""`、`--repo ""`、`--git_range ""` 等其餘 `others` 欄位同款可繞過。

已看,無:
- `_plan_for_loop`(scripts/lumos:9463–9482)新加的路徑字元擋(`/`、`\`、`..`)在絕對路徑、反斜線、NFC 組合字、單一 `.`、超長字串、NUL 位元組、全形斜線「／」等輸入下都不會拋例外或越界(用 Python 3.14 的 `Path.is_file()` 直接餵 NUL 位元組也不崩潰);全形斜線雖然沒被明文擋,但 POSIX 上它本來就不是路徑分隔符,拼不出跳脫 `Projects/` 的路徑,不構成可利用的洞。
- `--withdraw` 空字串 token、純空白 token、控制字元(含 ESC `\x1b`)token:都落在「找不到這個 token」分支,訊息經 `_esc_clean` 清洗、不會把控制碼印到終端機,帳本不動。
- `--withdrawn-by ""`(空字串,非純空白)一樣被「撤回要明講是誰撤的」擋下,跟純空白同一條路徑。
- token 重複(同一個 token 出現在兩列逃逸)→ 擋下且印出正確次數,不管重複的兩列是不是一列逃逸配一列撤回紀錄。
- `_escape_evidence_keys`(scripts/lumos:9877)把 sha 與 defect_ref 各自前綴成 `sha:`/`defect_ref:` 再當歸因鍵,即使兩個欄位的值字串上撞在一起(例如 sha 的值恰好等於 `"defect_ref:x"`)也不會產生假的歸因不明,交叉命中(同 defect_ref、不同 sha)能正確判成歸因不明。
- `nodes` 不是清單(字串、缺欄位、空清單 `[]`、元素不是字串)都被 `isinstance(d.get("nodes"), list) and d["nodes"] and isinstance(d["nodes"][0], str)` 擋掉,不算放行;拿正式帳 `docs/.governance-log.jsonl`(85880 列)機械掃過,目前沒有一筆 `gate=design-loop` 且 `kind=converged` 的紀錄踩到這個邊界,新加的 `gate == "design-loop"` 篩選條件不會漏掉既有資料(`_loop_gov_mark` 不論 code/design 迴圈一律寫 `gate: "design-loop"`)。
- `env.notes` 對不到計劃(計劃檔 frontmatter 壞掉、缺結尾 `---`)與 `tags` 欄位給字串而非清單兩種情況,都機械跑過 `escape-stats --json`,結果落在「未分類」或正確解析出 `scope/`,沒有例外、沒有誤算。
- `--missing-defect-ref` 與 `--sha`/`--defect-ref` 同時給 → 擋;`--missing-defect-ref` 給空字串時走的是「理由不夠字數」那條擋(訊息跟完全沒給 `--missing-defect-ref` 時的「要附佐證」訊息不同),但兩條路徑最終都是 rc=2、帳不動,不構成邊界漏洞,只是訊息選擇不同。

共 1 條。
