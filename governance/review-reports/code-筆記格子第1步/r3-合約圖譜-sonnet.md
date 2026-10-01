severity: minor

這份修正差異把第 2 輪 19 條處置大致都做到了,也沒破壞固定席節點宣稱的行為。我找到 2 條 minor:一個推送時的檢查漏洞,以及一組沒有測試咬住的修法。我另外對修法跑了 9 組拿掉實驗,每組跑 `-k slots_push_old_lines`。

**①r2-intake 19 條處置**

- 19 條逐條對 diff 與實跑,都做到了。
- 計劃已改寫的句子:
  - 〈擋〉只放連結只認補連結。
  - 文字鍵規則。
  - 治理帳 `check` 與格名。
  - `doctor --ci` 不唸。
- 這幾句與程式對得上:`_ns_is_old`、`_ns_text_key`、`_ns_slot_extra` 與 `_ns_slots_doctor_lines` 的 `not ci` 分支。
- 治理帳格名「三選一記成 `test/repro/防回歸`」與 `slot_check_keyed` 的 `"/".join(grp)` 一致。
- R2B5 的 `_ns_vault_rel` 說明已改成「`_vault_in` 找到、且有追蹤檔的圖譜優先」,與程式一致。
- 天花板 10 到 13 重編號:全 repo 搜不到殘留的舊編號引用。計劃內的「見天花板 5」「見天花板 8」仍指對的條目,開擋步改成「見天花板 12」也對。
- 跑 `python3.14 scripts/test_lumos.py -k slots`:111 passed, 0 failed。

**②新測試是否咬住(拿掉修法實跑)**

下列拿掉後測試都翻紅:
- 只放連結的舊行改成任何連結都算舊行:④、⑪紅。
- 文字鍵不分空白位置:⑩紅。
- 還原「只改續行時回頭查整條」:⑦紅。
- 實體行來源改用整條比對:⑦紅。
- 範本不給 SEE:⑪紅。
- 標點表把「和與及見」也去掉:⑩紅。
- 拿掉實體行併入整條那段:有一條紅。

**R3G1**
severity: minor
blocking: 否 — 提交時 `--staged --slots` 那道已擋得住,只有繞過掛鉤(`--no-verify`)或單次跳過時才會漏。
引句:「if not is_old and head is not None and head != line:」
推送時,「上線前寫的單行舊句,上線後只在後面接一段續行」會被當成舊行放行。
- 原因:`_ns_old_keys` 把推送範圍逐提交的實體行放進 `phys`,新條目的第一個實體行又拿去比 `phys`。
- 重現:在 `rw` 的 clone 上用 `/tmp/r3g_t.py`(以 `T._ns_repo` 建庫,用測試裡的 `_nh_commit` 等工具函式提交)。
  1. 上線前提交 `WHY:舊的一句話`。
  2. 提交帶 `--slots` 的掛鉤。
  3. 上線後提交同一行,加上續行 `  後面新接的一大段沒有出處也沒有因`。
  4. 執行 `_ns(root,"--diff",f"{base}..{tip}")`。
  - 輸出 `RC 0`,沒擋。
  - 同樣的內容在提交時(測試 ⑦)會被擋。
- 這個方向的缺口沒寫進天花板;天花板 10 寫的是相反方向(多行重排成一行)。
- `_ns_slot_line_problems` docstring 把兩道保護都說成接得住搬家,沒提這個例外。
- 修法:把這個缺口寫進天花板,或讓 `phys` 的第一行比對只在新條目是單行時才用。

**R3G2**
severity: minor
blocking: 否 — 只影響守衛強度,行為本身沒錯。
引句:「kw = {"extra": dict(_ns_slot_extra(sviol), check="slots" if not (viol or errs) else "shape+slots")} if sviol else {}」
- 治理帳 `check` 記成 `"shape+slots"`(R2A3)沒有任何測試咬住。我把它固定成 `"slots"` 後,`slots_push_old_lines` 子集仍全綠 13 passed。
- 同一類:R2A1 在 `_note_shape_report` 與 doctor 兩處對路徑加 `_esc_clean`,測試只涵蓋 `_ns_slots_format`(新測試 ④)。這兩處拿掉不會有測試紅。我只推論未實跑。
- 新測試 ⑨(帶別名的舊 DEP 補欄位)對 `_NS_SLOT_LINK_RE` 的別名處理不敏感。我把別名排除後 ⑨ 仍綠,因為兩邊文字相同,測試靠不到這項修法。
- 修法:補一條「同時有形狀違規與格子違規」的帳斷言(檢查 `check == "shape+slots"`),再補一條別名連結場景的反例。

**R3G3**
severity: minor
blocking: 否 — 計劃用詞比程式窄,不影響行為。
引句:「空白跟中日韓字相鄰的整個去掉、英文單字之間壓成一格」
- 程式的條件是「相鄰非 ASCII 字元」(`[^\x00-\x7f]`),不限中日韓。
- 計劃寫的「標點去掉」,程式實際只去 `→,，、。;；|｜`,英文 `.` `:` 不去。
- 修法:計劃把「中日韓字」改成「非 ASCII 字元」,把「標點」改成實際那一組。

**④固定席節點**

- 這份差異只動格子比對與輸出的輔助函式(`_ns_slot_key`、`_ns_old_keys`、`_ns_slot_line_problems`、`_ns_slots_format`、`_note_shape_report` 的路徑清洗與 `check`)。
- 固定席各節點的合約行為都沒被破壞,逐項如下。
  - `Systems/筆記內容閘.md`:
    - 「共用抽取器回給既有使用者維持兩欄」沒有被動到。
    - 路徑 NFC 只當比對鍵的規矩也沒被碰,`_esc_clean` 只改顯示。
    - 掛鉤範本仍不帶 `--slots`,「上線後不擋任何人」的宣稱成立。
  - `lumos-cli-read` / `lumos-cli-lifecycle`:lint 與 `slot_check_keyed` 的簽章沒變。
  - `pitfalls-code-loop`、`bound-tests-gate`、`guard-kill`、`design-loop`、`測試假綠形態`:未碰其邏輯,判不影響。

最高嚴重度 minor,blocking 0 條
