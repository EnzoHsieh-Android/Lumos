severity: minor

## F1 治理帳 nodes 欄若不是陣列而是字串,會把字串第一個字元誤當成迴圈編號算進放行分母
severity: minor
blocking: no
引句:「lid = nfc(str(d["nodes"][0]))」
file: `scripts/lumos:9871`(函式 `_escape_released_loops`,定義在 `scripts/lumos:9860`)

`_escape_released_loops` 判斷治理帳一筆 `kind=converged` 紀錄是否算放行時只檢查 `d.get("nodes")` 是否為真值,沒有檢查它是不是 `list`。如果 `nodes` 是非空字串(手改帳本、舊版工具寫壞、或別的程式共寫這支帳本時格式不對),`d["nodes"][0]` 會取到字串的第一個字元,再被當成迴圈編號放進「已放行」集合——不是拋例外或跳過,而是靜默算對一個完全不相干的迴圈。同檔其他讀帳函式(例如緊鄰的 `_review_loop_ids`、`_escape_review_rows_by_loop`)對可疑欄位都明確 `isinstance(..., str)` 檢查後才採信,這支漏了同款防呆,跟本檔一貫的「壞行不炸、但也不能誤讀」原則不一致。

雖然目前唯一的寫入端 `_loop_gov_mark`(scripts/lumos:8842 附近)固定寫 `"nodes": [loop_id]`,正常路徑不會踩到,但這正是「逃逸帳對得起來」這個案子要處理的那類問題——帳本是 append-only、跨版本共用的檔案,防呆要防的是「不是我這次寫的那種格式」,不是「我自己不會寫錯」。

重現(已實跑,rc=0 無任何錯誤或警告):
```
python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ba2fc358-b2c4-4fe8-b8cf-9883c1468562/scratchpad/escimpl/exp-邊界/repro.py
```
「實驗一」:審查帳只有迴圈 `a` 的審查紀錄;治理帳寫一筆 `{"kind":"converged","nodes":"abcxyz"}`(`nodes` 是字串不是陣列,且視覺上完全沒提到迴圈 `a`)。`loop escape-stats --json` 輸出 `"released": 1`,把迴圈 `a` 算成了放行——實際上這筆治理帳紀錄從沒指名任何叫 `a` 的迴圈。

## F2 --missing-defect-ref 跟 --sha/--defect-ref 同時給時,理由被靜默丟棄、不寫進帳也不提示
severity: minor
blocking: no
引句:「rec["defect_ref_missing"] = missing_ref.strip()」
file: `scripts/lumos:9786`

`--missing-defect-ref` 的說明是「手動記帳既沒有 --sha 也沒有 --defect-ref 時,講為什麼沒有」,程式碼也確實只在 `not rec.get("defect_ref") and not rec.get("sha")` 才把理由寫進 `defect_ref_missing`。但驗證關卡(`if not (sha or "").strip() and not (defect_ref or "").strip(): ...`)只在兩者都空時才會檢查 `--missing-defect-ref`;如果使用者同時給了 `--sha` 又給了 `--missing-defect-ref`(例如複製貼上舊指令、或誤以為兩個旗標可以並存留雙重紀錄),程式不會擋、也不會警告,理由字串直接消失,使用者拿不到任何回饋知道這段話沒被記下。

重現(已實跑,rc=0,寫入的列裡沒有 `defect_ref_missing` 欄):
```
python3 <上同 repro.py>  # 見「實驗三」
```
指令:`loop escape 甲 --stage CI --severity major --desc d --sha abc1234 --missing-defect-ref "口頭回報沒有留下任何提交紀錄"`
輸出:`✓ 逃逸入帳:…`(rc=0,無任何提示);落盤的列只有 `sha`,沒有 `defect_ref_missing` 欄,理由文字整個不見。

## F3 逃逸列 token 重複(資料損毀或雜湊碰撞)時,撤回其中一筆會連帶讓共用同一 token 的其他逃逸列(含更嚴重的)一起從清單標記與所有統計中消失
severity: minor
blocking: no
引句:「return {r.get("target") for r in rows if _escape_is_withdraw(r) and r.get("target")}」
file: `scripts/lumos:7586-7588`(`_escape_withdrawn_targets`);同款以 token 比對的地方還有 `scripts/lumos:9704`(`_list` 標記已撤回)與 `scripts/lumos:120-126` 附近的 `_escape_rows_for`(`d.get("token") not in gone`)

整套撤回機制(`_escape_withdraw`、`_escape_rows_for`、`--list` 的已撤回標記)全部用 `token` 字串比對來判斷「這一列是不是那個被撤回的目標」,沒有任何地方假設或檢查 token 唯一。`token` 是用 `secrets.token_hex(4)`(16^8≈42 億分之一,但輸出只 8 hex 字元=32 位元空間,實際碰撞機率遠高於這個估計——約 65536 分之一量級,而且此檔的落盤自驗 `_jsonl_append_verified` 已經在別處註明「撞鍵時讀回比對可能對到舊筆」是已知且接受的天花板)。一旦兩筆逃逸列意外共用同一個 token(手改帳本示範最直接,但也可能是撞鍵),撤回其中一筆會讓 `--list` 把兩筆都標成「已撤回」,`escape-stats`/問閘尾漏斗/治理帳統計/規則缺口統計也都會把兩筆都當成撤回、不算進任何分子——包含一筆從未被使用者指名要撤回、甚至等級更高的真實事故。

重現(已實跑,rc=0):
```
python3 <上同 repro.py>  # 見「實驗四」
```
設定兩筆逃逸列共用 `token: "ESC-DUPE"`:第一筆是「誤判(該撤)」,第二筆是「真事故(blocker@prod,不該撤)」。只下一次 `--withdraw ESC-DUPE`,`--list` 輸出裡兩筆都被標成 `★已撤回(重現後確認是第一筆的誤判…)★`——包括那筆本來不該被動到的 blocker 事故。

已看,無:S1–S21 對應的 21 條測試涵蓋的邊界(空帳/帳檔不存在/token 走 `_jsonl_append_verified` 正常路徑/非物件行/撤回紀錄本身不進統計/NFC-NFD 迴圈編號正規化/只有 spec-gate 留痕不算審查紀錄/symlink 帳檔擋下/`--withdraw` 與其他旗標混用擋下/放行數為 0 不算率/放行 <20 標樣本太少/standalone 佈局下 rule-gap 仍讀得到帳且排除撤回列)都各自實跑過對應測試,行為與計劃條款一致,沒發現偏離。治理帳 `nodes` 是空陣列時(`d.get("nodes")` 為假)會被安全跳過,不會像 F1 那樣誤讀,這一格沒有問題。`_escape_reason_ok` 對全形空白、純標點理由的邊界判斷(去空白後 <4 字、或沒有實字)跟既有 `[manual:]` 判法一致,用 4 字整數邊界、3 字 CJK 理由與 4 字英文理由分別試過都正確擋下/放行。NFC/NFD 計劃檔名撞名的情境在本機 macOS(APFS)檔案系統層級就會把兩種正規化形式視為同一份檔案,無法在此環境構造出「兩個檔案並存但內容不同」的真實碰撞來證明問題,沒有可實跑的失敗場景,不列進正式發現。
