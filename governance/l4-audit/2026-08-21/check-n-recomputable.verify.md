C1 [✅] doctor 掃 body 的 `lumos:count` 標記，用 `re=` 掃 `in=` glob 命中的檔案算實際數，跟 `count=` 比對，不符發軟提醒。 | 證據: scripts/lumos:1231(section N)、1236(`_CNT_RE`)、1244(`_CNT_RE.finditer(text)`)、1253-1264(os.walk + fnmatch 依 glob 過濾、cre.findall 累計 actual)、1265-1267(`if actual != claimed` → 加入 `_drift`)、1268-1272(`warn_soft(_drift + _bad, ...)`)。

C2 [✅] 標記為 HTML 註解，緊跟數字，含 `lumos:count=`/`re=`/`in=` 三欄位，範例格式相符。 | 證據: scripts/lumos:1152(範例 `<!--lumos:count=7 re=某正則 in=**/*.cs-->`)、1236(`_CNT_RE = re.compile(r"<!--\s*lumos:count=(\d+)\s+re=(.+?)\s+in=(\S+?)\s*-->")`)。

C3 [✅] 「共 5 處，實為 7」與 scripts/lumos 內建史料註解一致（claimed=5 < actual=7，方向與數值皆符）；具體節點內容因落在禁讀的 `docs/lumos-toolchain-knowledge/` 及案例原專案（另一 repo，本 repo 無 `PointsMall*.cs`）而無法直接複算，改以本 repo 內可讀的設計理由註解交叉核對。 | 證據: scripts/lumos:1145（「共 5 處」(實為 7)）。

C4 [✅] 「46 場景，實為 40」與史料註解一致（claimed=46 > actual=40）；同 C3，節點原文不可讀，改以同一行史料註解核對。 | 證據: scripts/lumos:1145-1146（「46 場景」(實為 40)）。

C5 [❌] 與 scripts/lumos 史料註解方向相反：註解寫「9 個元件(實為 8，少列一個)」即 claimed=9 > actual=8；本主張卻寫「8 個元件，實際為 9，漏列 AddressEditModal」即 claimed=8 < actual=9，claimed/actual 兩值對調。 | 證據: scripts/lumos:1145-1146（「9 個元件」(實為 8 少列一個)）— 與主張方向相反。

C6 [✅] 「TicketRepository.cs:173/392，實為 189/415」與史料註解逐字相符。 | 證據: scripts/lumos:1146（行號 173/392(實為 189/415)）。

C7 [❓] 史料註解中對應項目為「「8 場景通過」」，無括號附「實為」對照值，且數字（8）與主張中的「11 情境」對不上；本 repo 找不到「滿額贈」節點原文或對應測試/情境清單可複算（禁讀 `docs/lumos-toolchain-knowledge/`，且該案例屬另一專案）。搜過：`scripts/`、`governance/`、`.github/`、`docs/*.jsonl` 內關鍵字「滿額贈」「11 情境」，僅在 scripts/lumos:2757、scripts/test_lumos.py:2811 附近見到「滿額贈」字樣，均與情境數無關。 | 證據: scripts/lumos:1145（「8 場景通過」，無可比對數值）。

C8 [✅] 史料註解明確記載「2026-06-10 首跑就記過教訓「計數/清單型主張最會漂」，但★沒有配任何機制★，兩個月後照樣復發」，且同一段列出 5 項具體復發案例（共5處/8場景/46場景/9個元件/行號173-392），與「五次」數量相符。 | 證據: scripts/lumos:1144-1147。

C9 [✅部分] PRIOR-ART 段落確實引用 doctest 的「單一真相源」哲學、裁定方向為借法而非照搬（「這裡的借法是」字樣，符合 borrow-design 精神），且明確定位 Check N 不執行程式碼、只重算數字（對應「安全：不執行 shell、不 eval」）。惟「doctest 自 2001 年起」「doctest 會執行程式碼比對輸出」的明文對比，以及正式 `PRIOR-ART:` 欄位原文，落在禁讀的節點正文，本 repo 讀不到逐字版本，只能以 scripts/lumos 的設計理由註解交叉核對核心論點一致。 | 證據: scripts/lumos:1148-1150(PRIOR-ART 段)、1153(「安全:不執行 shell、不 eval」)。

C10 [✅] Check N 區塊（1231-1285）只 import `fnmatch`（別名 `_fn`）並使用既有的 `re`/`os`/`Path`，逐行檢查該區塊無 `subprocess`/`os.system`/`eval(`。 | 證據: scripts/lumos:1234(`import fnmatch as _fn`)、1236(`re.compile`)、1253(`os.walk`)、1256(`_fn.fnmatch`)；區塊內 grep `subprocess|os.system|eval(` 零命中。

C11 [✅] 掃描量上限為 4000 檔／40,000,000 位元組（≈40MB），超限不硬失敗，落成 `_bad` 提示「收窄 in= 的 glob」。 | 證據: scripts/lumos:1237(`_MAX_FILES, _MAX_BYTES = 4000, 40_000_000`)、1262-1264(`raise RuntimeError("掃描量超上限")`)、1265-1267(`except RuntimeError as e: _bad.append(f"{rel} → {e}(收窄 in= 的 glob):{glob}")`，非崩潰，繼續下一標記)。

C12 [✅] 壞正則被 `re.compile` 的 `try/except re.error` 包住，轉成單條 `_bad` 提示後 `continue`，不會讓 doctor 崩潰；並有對應牙齒測試驗證不炸。 | 證據: scripts/lumos:1248-1251(`try: cre = re.compile(pat) / except re.error as e: _bad.append(...) / continue`)；scripts/test_lumos.py:5311-5315(`t_checkn_bad_regex_does_not_crash`，斷言 `"正則不合法" in r.stdout and "Traceback" not in r.stdout`)。

C13 [✅] 軟提醒經 `warn_soft` 輸出，函式本身註解明言「印出但不動 issues → 不影響 rc」，與硬擋的 Check T 性質不同；並有對應牙齒測試驗證 `--ci` 下 rc=0。 | 證據: scripts/lumos:470-471(`def warn_soft(...): # 軟提醒:印出但不動 issues → 不影響 rc(R3-MAJOR-3)`)；scripts/test_lumos.py:5301-5305(`t_checkn_soft_does_not_fail_ci`，斷言 `r.returncode == 0`)。

C14 [✅] `_CNT_RE` 只解析 `lumos:count=`/`re=`/`in=` 三欄位（數量型），全檔案（`scripts/lumos`）搜不到任何對「行號」型標記的解析或比對邏輯（`grep 行號` 命中的都是既有的 Check J/其他機制的行號用法，與 Check N 標記語法無關）；此區塊也沒有處理形如 `lumos:line=` 之類的標記。「正解方向是改寫成方法名/符號名」的具體措辭落在禁讀的節點正文，未能逐字核對，但實作事實（僅支援計數、無行號比對）成立。 | 證據: scripts/lumos:1236(`_CNT_RE` 只含 count/re/in 三組)；`grep -n "lumos:line\|lumos:lineno"` scripts/lumos 零命中。

C15 [✅] `test_lumos.py` 內確有 6 個 `t_checkn_*` 測試函式，且透過 `globals()` 中 `k.startswith("t_")` 機制自動納入執行；內容涵蓋壞正則不炸、glob 縮範圍、軟提醒不影響 rc 等情境。 | 證據: scripts/test_lumos.py:5283(`t_checkn_matches_when_count_correct`)、5290(`t_checkn_reports_drift`)、5300(`t_checkn_soft_does_not_fail_ci`)、5308(`t_checkn_bad_regex_does_not_crash`)、5315(`t_checkn_glob_scopes_the_count`，斷言 in= 真的縮範圍)、5323(`t_checkn_silent_without_markers`)；scripts/test_lumos.py:19995(`tests = [v for k, v in sorted(globals().items()) if k.startswith("t_")]`)。

✅12 ❌1 ❓1 ⏭0
