severity: minor

**鎖檢查**:`/Users/enzo/.cache/lumos/dispatch-lens/9e991183c77bdb65383a6b176dedf5ffd281ce17b48fcfee796feaf8f010fece.json.warming` 不存在(ls 與 cat 都回 No such file),所以沒有鎖要處理,也沒刪任何東西。

**做法**:我在臨時目錄開了修前、修後、模擬生效日三個 worktree,審完已刪。跑了下面幾項。
- 修後版的 `-k finding_seat`:54 案例全過。
- 修後版的 `-k loop_next`:148 案例全過。
- 對修後版的 `_seat_noise_name`,把真帳 `docs/.canary-log.jsonl` 裡全部 795 個 auditor 寫法跑一遍,另加多組手造名字,和修前正則逐個比對。
- 把 `_FINDING_SEAT_SINCE` 暫改成 2020 年、環境變數維持測試預設的 9999,跑 `-k canary`:505 案例全過。

## 固定席判定

固定席筆記清單我是從 `lumos impact --diff e3b2c50..af2fb6f` 取得的。整組分三類判。

- **`Systems/loop-convergence-recording.md`(守衛面)**:不影響原有守衛。
  - 新增的 `--loop` 必帶、`finding-seat-badts` 事件、純日期覆寫、推遲提醒,都只收緊或補充 `--finding-seat` 自己的路徑。
  - 沒帶 `--finding-seat` 的載體(含沒帶 `--loop` 的)仍可記,守衛條件沒被改寬。
- **`Systems/canary-audit.md` 與 `Systems/reversibility-governance-ledger.md`**:不影響。
  - 擋下時不寫帳這點沒變。
  - 治理帳事件仍走 `_gate_event_or_warn(hard=True)`,只是多了一層空白清洗。
- **`Systems/design-loop.md` 與 `Projects/記帳與迴圈工具小修_計劃.md`**:不影響。
  - `_loop_next_hints` 對設計審(`kind == "design"`)不印新提示,設計審提示行為與修前相同。
  - `loop next` 的 `hints` 輸出路徑沒動。
- **其餘 INVARIANT 與守衛面固定席**(bound-tests-gate、guard-kill、lumos-cli-*、測試假綠形態、slim-*、cochange 等):不影響。這次差異沒改它們管的檔案行為,只有 `scripts/test_lumos.py` 的一個測試輔助函式與一條環境預設值被動到。

## 發現

severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Projects/記帳與迴圈工具小修_計劃.md:189`(S27)對照 `scripts/lumos:24909` 的 `_loop_next_hints`
失敗場景:S27 寫「high 代碼審 plant-canary 印兩條提醒」,修後實際印三條,新增的「載體最後記」提示排在最前面。程式現在 `hints` 回 3 條,測試用「任一條含」比對所以照過,書面條款字面卻對不上。
歸因:有證據的修復回歸。「每個分級都提醒」是這次修補才加的(整合 4)。修前 `_loop_next_hints` 對代碼審只有 high 才有提示。
引句:「載體最後記:--finding-seat 的席名要是這一輪已經入帳那一席的 --auditor,其他席先記、載體最後記;席名不帶輪次(寫 正確性-sonnet)」
查證:`grep -n "兩條提醒" docs/lumos-toolchain-knowledge/Projects/記帳與迴圈工具小修_計劃.md`,修前修後都在;修前版 `hints` 對 high 是 2 條,修後是 3 條。

severity: minor
blocking: 否
file: `scripts/lumos:19564` 的 `_FINDING_SEAT_SINCE`,對照 `skills/lumos-code-loop/reference.md`、`skills/lumos-project-notes/commands/06-代碼審與推送.md` 與計劃〈回退〉
失敗場景:「目前 2026-11-22」這個日期現在手抄在三份文件(reference、06 速查、計劃〈回退〉)加程式常數共四處。回退改成 `9999-12-31` 時漏改任一份,文件就會叫人照做而被擋。計劃〈回退〉有寫要跟著改,但沒有機械守衛。
歸因:有證據的修復回歸,新抄的字面是這次修補加的。修前 reference 與 06 速查只寫「2026-11-22 起」,沒寫「目前」二字。
引句:「手冊與命令速查寫的「目前 2026-11-22」跟著改」
查證:`grep -n "2026-11-22" skills/lumos-code-loop/reference.md skills/lumos-project-notes/commands/06-代碼審與推送.md`。

severity: minor
blocking: 否
file: `scripts/lumos:18073`(`_seat_noise_name`)
失敗場景:輸入是中文角色加無連字號的模型編號,例如 `外家codex-5-mini` 與 `外家codex-6-mini`。第一個「後面接英文字母的連字號」落在後面,角色被切成 `外家codex-5`,結尾的 5 被當輪次記號去掉,兩者都變成 `外家codex--mini` 併成一列,而且名字有雙連字號。docstring 宣稱「模型名裡的數字不動」,這個形狀沒做到。修前正則同樣把它們併成 `外家codex--mini`,所以不是回歸。真帳 795 個 auditor 沒有這個形狀,`外家-gemini-2-flash`、`外家codex-gpt-5.6-terra` 都正確。
歸因:有證據的原有漏查。修前修後輸出一樣,我用兩版函式跑同一組名字得到相同的 `外家codex--mini`。
引句:「_SEAT_SPLIT_RE = re.compile(r"^(.*?)-(?=[A-Za-z])(.*)$")」
查證:把兩版的 `_seat_noise_name` 與修前正則各餵 `外家codex-5-mini`、`正確性-2-sonnet`,結果都是帶雙連字號的字串,修前修後相同。

## 修補效果與相鄰路徑核對

**repair(修補是否有效)**
- G1:`外家-gemini-2-flash` 與 `外家-gemini-3-flash` 分開;`外家codex-gpt-5.6-terra` 原樣保留;`外家finder2-codex` 併成 `外家finder-codex`。
- G2:同一迴圈首筆在生效前、第二筆在生效後,不帶 `--finding-seat` 仍 rc0。
- G3:不帶 `--loop`、帶 `--finding-seat` 擋下,測試覆蓋。
- G4:純日期覆寫生效。覆寫把常數要填的推遲時,stderr 有提醒,測試覆蓋。
- G5:badts 事件與脫困訊息由測試覆蓋。
- G6:standard 代碼審的 `hints` 帶「載體最後記」與 `--finding-seat`。
- G7:`_fs_blocked_n` 只讀 `docs/.governance-log.jsonl`。
- 以上由 `-k finding_seat`(54 案例)與 `-k loop_next`(148 案例)全過支撐,G1 另用真帳 795 個 auditor 實跑對照。

**preserve(相鄰路徑是否還成立)**
- `架構對齊r2-sonnet`、`架構對齊-r2-sonnet`、`架構對齊2-sonnet` 仍併成 `架構對齊-sonnet`。
- 不帶 `--finding-seat`、不帶 `--loop` 的載體仍可記帳。
- 設計審不印新提示。
- 帶時區的覆寫值仍照舊生效。

**新增補充案例**
- 時間炸彈:把常數退到 2020 年、環境變數維持測試預設的 9999,讓 2026-11-22 後的「推遲提醒」每筆載體都會印出來。跑 `-k canary` 505 案例全過,沒有測試因多出的 stderr 而紅,修補沒留下 11-22 之後才發作的紅燈。

## 三問

1. **原問題的修復效果有何行為證據?** 有。
   - 席名切分用真帳全部 795 個 auditor 與手造反例,修前正則與修後函式逐個對照,gemini 版本、gpt-5.6、finder2 都按預期。
   - 必填與擋下路徑由 `t_canary_record_finding_seat`(54 案例中的一支)覆蓋。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 是。
   - 設計審豁免、沒帶旗標的載體、結局帳(`outcome` 非 None 不走這道)、舊迴圈首筆在生效前,都沒壞。
   - 修補沒拿掉守衛。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 提示條數:修前 high 2 條、修後 3 條。
   - 生效日手抄字面:修前不寫「目前」,修後寫了。
   - `外家codex-5-mini`:修前修後都是 `外家codex--mini`。
   - 這三條都沒有會做出錯行為的證據,所以都標 minor。

最嚴重等級 minor
