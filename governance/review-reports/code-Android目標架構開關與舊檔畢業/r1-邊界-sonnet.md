severity: major

我逐 hunk 讀完整份 diff。極端輸入下的行為(空清單、BOM、非 UTF-8、清單是目錄或捷徑、重複路徑、非字串元素、怪檔名)沒找到執行錯誤,詳見最後的「已走過沒問題的極端輸入」。找到的洞全在測試:有三個合理的改壞,測試照綠。我在 `006c398b8` 的臨時 clone(已刪)實跑確認。

**1.**
severity: major
blocking: 是
`scripts/lumos` 的 `_arch_legacy_at` 與 `_arch_legacy_apply`(diff 的 `+    return {nfc(x) for x in files}, "ok"` 與 `kept = [f for f in fs if nfc(f) not in legacy or nfc(f) in keep]` 兩處)。NFC 比對沒有任何測試守住,拿掉也沒有測試會紅。

- 我把這兩處的 `nfc` 都拿掉:`return set(files), "ok"`,以及 `f not in legacy or f in keep`、`grad += [f for f in kept if f in legacy]`。
- 跑 `python3.14 scripts/test_lumos.py -k t_arch_target_`,結果是 `165 passed, 0 failed`。
- 原因:四支新測試的檔名全是 ASCII(`app/Domain/Order/OrderOld.py` 等),NFD 與 NFC 寫法從沒對照過。
- 被保護的是必要行為。計劃做法 8 與 `_arch_legacy_at` 的 docstring 都寫了兩邊轉 NFC。
- 失敗場景:舊檔清單寫 NFD 檔名(手寫或貼自 Finder),git 回 NFC 路徑,或反過來。該檔不被當舊檔,改照目標規則審,對舊程式出假的規則違反。方向是多審,不是漏審。

引句:「+    return {nfc(x) for x in files}, "ok"」

**2.**
severity: major
blocking: 是
`scripts/lumos` 的 `_arch_legacy_doctor_line`。測試的資料剛好讓「已不存在」與「沒被判給目標節點」兩個計數都是 1,把兩個數字對調測試也過。

- 我把輸出改成 `(已不存在 {stray}、沒被判給目標節點 {gone})`,數字對調。
- 跑 `-k t_arch_target_legacy_doctor`,結果是 `5 passed, 0 failed`。
- 測試斷言是 `"已不存在 1" in hits[0] and "沒被判給目標節點 1" in hits[0]`,兩邊都是 1,分不出誰是誰。
- 被保護的是 S9 條款明寫的摘要內容。
- 失敗場景:實作把這兩個數字對調或接錯變數,doctor 就印出錯誤的清理指引,測試照綠。
- 同一支測試也沒測「清單上的檔被 `none` 命中」這個分支(`rules[i][1] == "none"`)。

引句:「+    return (f"舊檔清單 {len(legacy)} 支(已不存在 {gone}、沒被判給目標節點 {stray});清單上的檔架構對齊照鄰居審,刪掉一行就改照目標審", None)」

**3.**
severity: major
blocking: 是
`scripts/lumos` 的 `_arch_legacy_check_lines`。說明行裡的「其中 M 支這次有改動」沒有測試能區分真假。

- 我把 `len(gone & changed)` 改成 `len(gone)`。
- 跑 `-k t_arch_target_graduate_check_note`,結果是 `5 passed, 0 failed`。
- 原因:測試 A 只刪掉一行,而且那支剛好有改動,M 與 N 都等於 1。
- 沒有「清單少了行、但那支檔這次沒改」的案例(計劃 S6 要印的 M 就是在區分這種)。
- 失敗場景:清單少 3 行、其中只有 1 支這次有改,會印成「其中 3 支已照目標審」,誤導人以為 3 支檔被當場審過。

引句:「+        out.append(f"舊檔清單比起點少了 {len(gone)} 行,其中 {len(gone & changed)} 支這次有改動、已照目標審")」

**4.**
severity: minor
blocking: 否
⚠ 計劃 `Projects/Android目標架構開關與舊檔畢業_計劃.md` 的 S1、S2、S3、S4、S7、S8 綁了六支 `[test: t_arch_template_android_*]`,`scripts/test_lumos.py` 裡一支都不存在(`grep -c t_arch_template_android_all_combos` 得 0)。`lands_in` 列的 `Systems/android-arch-template` 也不存在。計劃狀態是 `doing`,產生器那半這次沒做。

- 我跑了 `lumos lint` 得 0 問題;`lumos doctor` 對這幾個名字沒有任何輸出,所以目前沒擋。
- 但那六條條款現在是指向不存在測試的綁定。交編排者確認這是否符合「筆記測試綁定要存在」閘的預期。

引句:「+- [S1] 當產生器跑遍六個開關的全部 64 種組合時,每一份產出的節點經 lumos lint 應回報 0 問題」

**已走過沒問題的極端輸入:**
- **清單內容:**
  - `{"files": []}`:`_arch_legacy_apply` 的 `if not legacy` 提早回傳,不報錯。
  - 重複路徑:集合吸收。
  - 非字串元素、頂層不是物件:算 `unreadable`。
  - 檔名含方括號、星號、中文、換行:只當字面字串查集合,不碰 fnmatch。
- **清單檔本身:**
  - 開頭 BOM:`_json_at_ref` 會 `lstrip("\ufeff")`。
  - 非 UTF-8:`strict=True` 讓它回 None,再由 `cat-file -e` 判成 `unreadable`。
  - 清單是目錄或捷徑(symlink):`git show` 的內容不是合法 JSON,同樣算 `unreadable`。
- **doctor 那行:** 只印計數與固定句,不印檔名,所以不會有看不見的字元。整段在 try/except 裡,出錯降成一行提醒,不會弄壞整個 doctor。
- **沒有任何目標節點:** `if not targets` 提早回傳。
- **派工鏡頭的檔數上限:** 舊檔先佔掉前 2000 支額度,後面的新檔會被切掉。這是既有上限,切掉時有「沒比到的檔照鄰居審」的說明行,所以不另標 finding。

**固定席逐條判定(都沒有破壞行為或合約):**
- `Issues/code-loop守衛main-direct盲區`、`Systems/pitfalls-code-loop`、`Systems/reversibility-governance-ledger`:新增的邏輯只在有宣告且有舊檔清單時才改派工鏡頭與分級,不碰 main-direct 路徑或可逆性帳。不影響。
- `Systems/lumos-cli-read` 的 INVARIANT(search 預設排除 superseded):這次沒動 search。不影響。
- `Systems/design-loop` 的 INVARIANT(處置閘第五步,審材必須是 `.md` 計劃):這次只動設計審派工鏡頭的目標段(`_dispatch_lens_spec_arch_text`),不動處置閘。不影響。
- `Systems/guard-kill` 的兩條 INVARIANT:這次沒動 guard kill。不影響。
- `Systems/測試假綠形態` 的 INVARIANT(還原翻紅釘要配前置斷言):新測試多數有現場斷言,但 finding 1 到 3 顯示翻紅釘不足。與該合約精神不衝突,只是覆蓋面不夠。
- `Systems/arch-alignment-lens`:新增段落與程式一致,畢業例外有寫進文件。文件與程式沒有對不上的地方。

最嚴重等級為 major
