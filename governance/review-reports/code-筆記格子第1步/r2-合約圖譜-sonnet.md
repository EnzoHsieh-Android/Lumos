severity: major

範圍:`c5fc9870..440af7a4`(只動 `scripts/lumos`、`scripts/test_lumos.py` 和計劃一句天花板)。我把 `-k slots`(99 條)、`-k note_shape`(178 條)、`-k negation`(77 條)全跑過,都綠。寫「翻紅驗過」的修法我各拿掉一次實跑,結果見下。

## 固定席摘要(判「不影響」)

- **筆記內容審共用抽取**:不影響。`pre2` 只在傳了 `mark2` 時才另收一份,回傳還是三元組。筆記內容審沒傳 `mark2`,走原本的 `(dest,)`。
- **既有形狀規則、否定現況句、前綴提醒**:不影響。`vaults` 這個變數在 `cmd_note_shape` 裡已沒人用,抽成 `_ns_vault_rel` 後也沒有未定義名稱。相關子集全綠。
- **`_ns_slots_doctor_lines` 與 doctor 各段**:格子這一段有改動。完整 doctor 仍唸「沒帶 --slots」,`--ci` 不再唸,這個差異見 R2G2。
- **`--slots` 參數定義**:仍然保留。
- **r1 處置**:`r1-intake.md` 列的 25 條折入項,我逐條對過 diff,修法都在。這批裡沒有發現「fix 自己引入的」功能性新洞。下面是計劃跟實作對不上的地方,加上幾道沒被測試咬住的修法。

## 逐條 finding

**R2G1** 計劃〈擋〉寫「只放連結的舊行改了連結也算舊行」,實作改成「舊連結必須全在新行裡」才算舊行,兩邊矛盾
- `docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:114` 寫:「只放連結的舊 DEP/FLOW 行改了連結,上一版同前綴也是只放連結的行,也算舊行(不被逼著改 SEE)」。
- 實作(r1 對 C2 的修法)只認補連結。
- 重現:我在 `t_slots_push_old_lines` 同款的測試專案(`_slot_golive_repo`)上,把舊 `DEP:[[Systems/甲]]` 改成 `DEP:[[Systems/甲改名]]` 再暫存,跑 `--staged --slots`,rc=1。
- 把舊的 `DEP:[[Systems/甲]]、[[Systems/乙]]` 刪成只剩 `[[Systems/甲]]`,也是 rc=1。
- 兩種都被逼著改寫成 SEE,正是計劃寫著要避免的事。
- S6 條文只說「補一個連結算舊行」,沒有覆蓋這兩種情況。
- 處置:二選一,改計劃那句成「只認補連結,換連結或刪連結視為新寫」,或放寬實作。
- 現在 `--slots` 還沒進掛鉤範本,不擋任何人。
引句:「return any(old and old <= key[2] for old in old_keys.get(None, {}).get(key[:2], ())), False」
severity: major
blocking: 是 — 計劃是這批的設計依據,它跟實作互相牴觸,必須有一邊改過才能算照做。

**R2G2** 計劃〈擋〉的治理帳欄位與 doctor 條款沒跟著修正更新
- `計劃.md:120` 寫「`extra` 只放 `{"slots_lines","slots_missing"}`」,實作多了 `"check": "slots"`。
- 同一行說 `slots_missing` 是「{鍵:次數}」,實作現在還會記「核心一句」「SEE」,以及三選一用的 `test/repro/防回歸` 這種合成鍵名。
- 這些是格名,不全是必有鍵。
- `計劃.md:118` 寫「掛鉤沒帶 `--slots` 時 doctor 也講一句」,實作現在只有完整 doctor 講,`--ci` 路徑(推送前每次)不講。
- 這個行為是 r1 通才席 U4 的處置,但計劃和 S9 沒記。
- 三處只改實作、沒回寫計劃。天花板 7 那句新增倒是有寫進去。
引句:「return {"check": "slots", "slots_lines": len(sviol), "slots_missing": miss}」
severity: minor
blocking: 否 — 只是文字落後,行為本身是 r1 處置要的。

**R2G3** 單次跳過改用 `_ns_vault_rel` 這條修法(G3/A1)沒有測試咬住
- 我把 `_ns_skip_slot_extra` 裡的 `_ns_vault_rel(root, lst)` 換回「寫死第一個圖譜」,`-k slots` 仍是 99 passed。
- 「批次讀失敗回 None 才 fail-open」這條(K3)也一樣:把 `_ns_base_summary_lines` 的 `return None` 改成 `return []`,99 passed。
- 另外,`_nodehome_cat_blobs` 對含換行的路徑會整批回 None(`scripts/lumos:25198`),所以任何一個含換行的筆記檔名都會讓整次格子檢查 fail-open。這條沒有測試。
- intake 對這兩條只寫「HIT」,沒寫翻紅驗過。
- 目前沒有實際壞掉的行為,只是回歸沒人守。
引句:「vault_rel = _ns_vault_rel(root, lst) if lst else None」
severity: minor
blocking: 否 — 行為正確,只是沒有測試守住。

**R2G4** 路徑清控制字元、合併中單次跳過不算、推送時的收尾說明這三處也沒被測試咬住
- 逐一拿掉:`_esc_clean(p, 200)` 改回 `p`、`if mode_word == "這次推送":` 改成 `if False:`,`-k slots` 都是 99 passed。
- 合併中不算格子那條(B3)的 `if mh is not None and mh.returncode == 0:` 在檔裡出現 3 次,我沒能做單點翻紅。intake 已承認沒補測試。
- doctor 事後掃描那行 `_esc_clean(p, 200)` 也沒有案例帶控制字元的檔名。
引句:「out.append(f"  {_esc_clean(p, 200)}:{n}  {'; '.join(_esc_clean(m, 200) for _k, m in probs)}")」
severity: minor
blocking: 否 — 輸出清理類的修法,缺測試不影響行為。

**R2G5** `t_slots_push_old_lines` 文件字串宣稱的翻紅釘,有兩處與實測不符
- 我實跑的結果如下:
  - `_notelines_range_added` 不收 `pre2` → ① 紅,成立。
  - `_ns_slot_key` 把空白換成空格 → ③ 紅,成立。
  - 只放連結的鍵不帶連結集合 → ④ 紅,成立。
  - `_carry` 不帶 `by_path2` → ⑤ 紅,成立。
  - `_ns_slots_old_lines` 不收 `pre2` 來源 → ① 紅,成立。
  - `_carry` 的 `pre2` 拿掉 → 全綠。
  - 「第一個實體行對上也算」那道(`if not old and head is not None and head != line:`)單獨拿掉 → 全綠。
- 第二項的文件字串寫「只拿一道不紅」,承認有兩道擋同一件事。
- 但推送側(舊行來源是 `pre2`、`old_by` 的實體行)沒有任何多行舊條目案例。我手寫了「上線前寫多行、上線後補欄位的推送」和「上線前寫、改名後補欄位的推送」兩個探針,現行碼都 rc=0。所以沒有行為 bug,只是這兩個防線沒有咬住的測試。
引句:「for d_ in (by_path, old_by, by_path2, pre2):」
severity: minor
blocking: 否 — 行為正確,守衛缺口。

## 其餘確認(沒問題)

- 計劃〈擋〉的「提交時沒帶 `--slots` 就不跑」「推送只信格子自己的記號」「舊行判定的來源」「擋下訊息 20 條上限」、[S1]–[S5]、[S7]–[S10]、[S15],都跟實作和測試對得上。
- 天花板 7 新增那句我實跑驗證:把同一句缺格舊句複製三份再暫存,rc=0,跟那句描述一致。
- `A和B` 與 `AB` 比對鍵相同(去掉分隔字和空白),屬於天花板 7 說的「同核心一句」範圍。
- 單次跳過的 `check` 欄位:零違規時也會帶 `check: slots`、`slots_lines: 0`。治理帳消費端(`_GOV_FIELD_TYPES`、去重鍵)只把 `check` 當字串,沒有誤判。

最高嚴重度 major,blocking 1 條
