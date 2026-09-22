severity: clean

## 審查範圍與方法

只審第三輪的三處新東西(依派工單):① `PLANNED_TAIL_RE`(只剝行尾那一對標籤)② 三支正則搬到合約抽取區的位置移動 ③ 新增的防回歸測試與一處註解對齊。前兩輪已折的十條不重審。

全程在 `/tmp/lumos-r3-test-vault`(建立 Systems/Verification/Projects/MOC + `MOC/idx.md`)用真實 `python3 scripts/lumos --vault ...` 指令跑,沒有只靠讀碼推論。另外複製一份 `scripts/lumos` 到 `/tmp/mutation_dir/lumos`(未動 repo 本體)做翻紅驗證。

## 實際跑過的路徑(逐項記錄)

1. **合約文字結尾恰好是一對同形狀的 `[watch:…] [due:…]`**(派工單點名的最刁鑽邊界):
   `guard plan Systems/Pay "退費規則要標好 [watch:某節點] [due:2020-01-01]" --due 2099-12-31 ...`
   寫出的行是 `... [watch:某節點] [due:2020-01-01] [watch:Verification/2026-09-22_...] [due:2099-12-31]`。
   `guard settle` 正確只剝掉真正在行尾的那一對(node 建立時附加的),假標籤原封不動留在合約文字裡,轉正後變成
   `KEY:★INVARIANT★ 退費規則要標好 [watch:某節點] [due:2020-01-01] [test:t_dummy]`。
   同一情境也跑了 `guard abandon`(`邊界D合約結尾像標籤 [watch:假] [due:2020-01-01]`),墓碑正確立起、家節點的預告行整行拿掉,假標籤沒有殘留、也沒有誤刪到別的內容。

2. **兩個標籤順序顛倒**(手改成 `[due:...] [watch:...]`):`guard settle` 正確判定找不到對應行、擋下(`擋下:...裡找不到預告行...`),不會誤剝、不會誤判成別條、不留半套。這屬於威脅模型明講「不防繞過」的手改情境,行為是安全失敗,不是資料損毀。

3. **標籤之間有多餘空白**(手改成 `[watch:X]    [due:Y]`,四個空格):`\s*` 正確吸收,`guard settle` 正常轉正成功。

4. **行尾有全形空白 `　`**(手改在真正尾巴之後多加一個全形空白):Python `\s` 在預設(非 bytes)模式下涵蓋 `　`,加上 `PLANNED_RE.match(lines[i].strip())` 本身會先整行 `.strip()`,兩層都吃得掉,`guard settle` 正常轉正。

5. **標籤裡含 `]`**:追到源頭——`gref`(守衛節點檔名)是 `_guard_plan_slug` 產生,正則 `[^\w一-鿿-]+` 會把 `]` 換掉,不可能出現;`due` 在 `cmd_guard_plan` 裡先過 `datetime.date.fromisoformat` 檢查,非 `YYYY-MM-DD` 格式一律擋下(`擋下:最遲日期『…』不是 YYYY-MM-DD`),同樣不可能含 `]`。所以「真正被程式附加的那一對」不會出現 `]` 在值裡;只有手改才能造出這種輸入,而手改本來就在「不防繞過」範圍內,沒有另外去驗證這條(懸空推論的話沒有意義,已用 1–4 的真跑結果確認 regex 本身邊界正確)。

6. **只有一個標籤**:追過寫入路徑,`cmd_guard_plan` 永遠是「一次寫好 `[watch:...] [due:...]` 兩個」(`scripts/lumos:10667` `marker = f"  KEY:{PLANNED_MARK} {claim.strip()} [watch:{gref}] [due:{due.strip()}]"`),沒有任何程式路徑會只寫一個;只剩手改才會少一個,那種情況跟情境 2 一樣,`PLANNED_TAIL_RE` 不匹配 → 整段留在 `body` 裡 → 跟 `want` 對不上 → 安全擋下,不是靜默錯剝。

## 正則搬移(第 2 點)

`grep -n "^PLANNED_RE\|^WATCH_REF_RE\|^DUE_REF_RE\|^PLANNED_TAIL_RE"` 確認 `scripts/lumos` 裡各只有一份定義(3672–3679 行),原本 guard 指令區(約 10556 行)那份已經整個拿掉、換成一句指向新位置的註解,沒有殘留副本、沒有遮蔽。四支正則的所有使用點(`extract_planned`、`_guard_planned_line`、`cmd_context` 裡的 `DUE_REF_RE`/`WATCH_REF_RE`)全部在函式體內,執行時模組早已載入完畢,搬到檔案前面對執行順序沒有影響(Python 模組層級變數在函式呼叫當下就緒即可,不需要定義先於使用的原始碼順序)。

## 新增的防回歸測試(第 3 點)

`t_guard_claim_with_bracket_tags_still_settles` 用真跑驗證過兩次:
- 對現有(未動)`scripts/lumos` 跑:`python3 scripts/test_lumos.py -k t_guard_claim_with_bracket_tags_still_settles` → 4 條全綠。
- 對 `/tmp/mutation_dir/lumos`(把 `body = PLANNED_TAIL_RE.sub(...)` 改回舊做法 `DUE_REF_RE.sub("", WATCH_REF_RE.sub("", m.group(1)))`,即剝掉整行所有標籤)重跑同一支測試 → ②③兩條真的翻紅,錯誤訊息正是「找不到預告行」,證實測試確實釘住這次修的東西,不是空氣測試。

註解對齊(`scripts/lumos` 舊位置留的那句「這一組的正則不在這裡,在上面合約抽取那一區…正則離函式 6800 行」)跟實際行號差距(舊位置約 10531 行 vs 新位置 3672 行,差約 6859 行)吻合,沒有失真。

## 結論

三處新東西都实际跑過對應的邊界輸入,沒有找到程式邏輯錯誤、資料損毀或誤判。手改造成的「順序顛倒」「缺一個標籤」都是安全擋下(擋住 + 給出清楚理由),沒有靜默改錯行或吃掉別條合約。判 clean。
