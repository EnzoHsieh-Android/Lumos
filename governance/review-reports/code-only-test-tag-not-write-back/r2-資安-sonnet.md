severity: minor

# 第 2 輪資安審查(只看可被利用的洞)

## 1. 不可信輸入流到危險操作(設定檔 JSON 解析、正則)
已看,無。設定檔經 `_note_shape_config` 的 json.loads 包在 try 裡,壞值一律退成 block;`_NODEHOME_TEST_TAG_VALUE_RE` 是單一字元類加 `+` 的 fullmatch,長度先卡 200,沒有巢狀量詞。`_slot_scan` 只用 str.find 與既有的 `_SLOT_KEY_RE`,沒有新的動態正則、沒有 eval 或 shell。
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
file: `scripts/lumos:27738`(`_note_shape_config` 的 json.loads 區段,實際行號以 `grep -n "def _note_shape_config" scripts/lumos` 為準)

## 2. 權限與守衛繞過
豁免開關讀的是「被推的版本」的 `.lumos/config.json`,同一個推送裡改設定的人能決定豁免開不開,這是設計上的接受面;逐路徑看:
- 貢獻者把設定改成讓豁免開:同一份設定也讓測試名核對在同一推送裡跑成 block,所以不是繞過。
- 貢獻者把設定改成讓豁免關(test_refs 設 warn 或 off):退回舊行為(換標記算內容有變),只會讓寫回更容易被滿足,等於回到上輪之前的狀態,不是新洞。
- 豁免開、但測試名核對實際沒擋:`_ns_test_refs_collected` 有三條降級路徑——工作目錄索引對不上被推版本時 `trmode = "warn"`、任何例外時 fail-open 回 "off"、`LUMOS_SKIP_NOTE_SHAPE=1`。這三種情況豁免已經開了(`cfg["tag_exempt"]` 在 cmd_home_check 一開始就定死),但標記值的核對沒有真的擋。此時能藏進 `[test:…]` 的內容限於通過字元集(英數與少數符號、單行、200 字內)的英文句子,被 strip 掉後該行的實質改動不算「內容有變」。
- 這是縱深防禦缺口:豁免的前提(核對會擋)在執行期沒有被再確認一次。CI 的工作目錄就是終點,索引不會對不上,且不吃本機環境變數,所以最終仍會被 CI 擋。
severity: minor
blocking: 否 + 推論;攻擊路徑:誰=能推分支的貢獻者;從哪=推送前掛鉤本機(測試索引對不上或例外或設定 SKIP);送=把英文句子包成 [test:…] 加在筆記裡同時改程式;拿到=該筆記改動不被當作寫回、內容變更偵測被洗掉,本機閘放過;但 CI 會擋,無法直接利用,所以不到 major。建議:`cmd_home_check` 在 `_ns_test_refs_collected` 實際降級(warn/off)時把 `cfg["tag_exempt"]` 一併關掉,或在降級路徑讓豁免跟著失效。
引句:「cfg["tag_exempt"] = _nodehome_tag_exempt(cfg_text)」
file: `scripts/lumos:30013`(`_ns_test_refs_collected` 內 `trmode = "warn"` 的降級段)

## 3. 密鑰與個資
已看,無。diff 沒有讀寫任何秘密、沒有新的 log 輸出內容帶使用者資料;治理帳只寫模式與計數。
引句:「cfg = _nodehome_config(root, cfg_text, from_snapshot=True)」

## 4. 加密與傳輸
已看,無。沒有網路、加密、雜湊或簽章變動。
引句:「def _nodehome_tag_exempt(cfg_text):」

## 5. 執行邊界
已看,無。新增碼全是純字串處理(`_slot_scan` 產生器、`_nodehome_strip_test_tags`),沒有 subprocess、沒有檔案路徑拼接、沒有反序列化新格式;讀設定仍走既有的 `reader(".lumos/config.json")`(快照讀,已有捷徑檔防護)。程式碼圍欄內的行原樣保留,攻擊者無法用圍欄藏內容(`_visible_lines` 判可見)。
引句:「cfg_text = reader(".lumos/config.json")」

## 6. 行動端
已看,無。本次不涉及行動端。
引句:「def _nodehome_mark_note_content(repo_root, groups, vault_rel, tag_exempt=False):」

## 新依賴
無新增依賴(只用已 import 的 re、json)。

## 對表態記錄的反駁
py-eventloop na 的宣稱與本 diff 無關,不影響上面結論。

總結:全份最高等級 minor
