severity: blocker

### F19 零值豁免可把 `blocker 0day` 當成零條剝掉

severity: blocker

blocking: 是 — 席報告可被機器當成 minor 記帳，總結卻夾帶 blocker 級結論。

引句:「_vis_lv = re.sub(r"(?i)\b(?:clean|minor|major|blocker)\b\s*[:：]?\s*0(?![\d.])", "", _strip_inline_markup(ln)[0])」

1. `0` 後只禁止數字或小數點，`總結: blocker 0day exploit` 會被剝成 `day exploit`，繞過殘留檢查。
file: `scripts/lumos:5232` 零值替換沒有要求計數單位或字串結尾。
2. 最小重現：該報告含兩行 `severity: minor` 時，`_report_severities` 回 `['minor', 'minor']`，`_report_normalize_issues` 回 `[]`。
3. 牽連 `Systems/loop-convergence-recording` 的寫側正規化硬擋；`cmd_canary` 直接信任此結果。

### F20 精確檔名未證明已安裝，讓同名自有 hook 漏過高風險掃描

severity: blocker

blocking: 是 — 任一非工具鏈 repo 的自有 `scripts/hooks/pre-push` 等同名程式可逃過 high 分級與代碼審。

引句:「and not (skip_vendored and _is_vendored_path(cur_file))」

1. 判別只確認「不是工具鏈本體」，沒有確認目標 repo 曾安裝這批檔，因此精確名稱被直接當成工具所有。
file: `scripts/lumos:13245` 自身判別只看 skill 檔；`scripts/lumos:17695` 對所有其他 repo 開啟跳過。
2. 最小重現：餵 `_pitfall_diff_collect` 一段新增 `scripts/hooks/pre-push`、內容為 `open("secret.txt")` 的 diff，回傳 `claims: []`、`tier: standard`。
3. 同一身分誤判也在 lint 層生效。
file: `scripts/lumos:17801` 會無條件濾掉同名 SARIF claim。

### F21 引號內前導空白仍可繞過同一行清單守衛並寫壞欄位

severity: major

blocking: 是 — `append` 會成功把未解析的 inline-list 字串持久化成清單項，留下壞的 `about_code`／其他清單欄位。

引句:「if (sval.startswith(("[", "{")) and not sval.startswith("[[")) or sval.count("[[") > 1:」

1. `strip_quotes` 不去除引號內前導空白，`" [src/a.ts, src/b.ts]"` 不以 `[` 開頭而穿過判斷。
file: `scripts/lumos:10651` 去引號後直接套用 `startswith`。
2. 最小重現：`edit_fm_append(['about_code: " [src/a.ts, src/b.ts]"'], 'about_code', 'src/c.ts')` 產出 `- "[src/a.ts, src/b.ts]"` 與 `- src/c.ts`，解析後首項仍非路徑。

### F22 安裝端複製所有檔，漂移測試卻只驗受版控檔

severity: major

blocking: 是 — `--no-pull` 或非 Git 來源中的工具自裝程式仍會被消費專案掃成自有程式，重新造成誤擋。

引句:「toolkit += [str(p.relative_to(src)) for p in base.rglob("*") if p.is_file()]」

1. 安裝端以 `rglob` 收所有檔案，跳過表與測試則以 `git ls-files` 收受版控檔，兩個母體不相同。
file: `scripts/lumos:13403` 會列舉未追蹤檔；`scripts/test_lumos.py:9464` 只列 Git 追蹤檔。
2. 最小重現：來源的未追蹤 `scripts/hooks/extra.py` 經 `lumos update --source <來源> --no-pull` 被複製後，提交其中的 `open(...)` 會升 high，但 `t_vendored_file_list_matches_what_install_ships` 仍綠。

## 前兩輪修法驗收

F1:修出新洞 — 目錄誤跳修掉，但精確同名檔未驗安裝身分，見 F20。  
F2:修出新洞 — lint 也套同一個未驗身分的精確檔名過濾，見 F20。  
F3:修到 — 刪除行已傳入跳過旗標。  
F4:修到 — `about_code` 已不在 `set` 的純量白名單。  
F5:修到 — 絕對路徑、逃出根目錄、缺檔與目錄皆被拒。  
F6:修到 — 寫入統一收回 append/remove。  
F7:修到 — 移除 `set` 後不再有未引號的純量覆寫路徑。  
F8:修到 — 事故筆記已明說只影響排序、不建波及連結。  
F9:修出新洞 — 目錄常數共用，但實際複製集合與驗證集合分叉，見 F22。  
F10:修到 — 特製 setter 與其不一致訊息已移除。  
F11:修到 — 相對目錄路徑改在目錄層計算。  
F12:修到 — 判別鍵出現在消費專案時會恢復掃描。  
F13:修出新洞 — 既有三種繞法堵住，但引號內前導空白仍可繞過，見 F21。  
F14:修到 — 重複單一值會原樣 no-op 並誠實回報。  
F15:修到 — 大小寫不符會拒絕。  
F16:修到 — append 以正規化路徑去重。  
F17:修到 — remove 使用同一套正規化鍵。  
F18:修到 — 授權測試改用共用目錄常數。  

風險掃描清單:誤報 — 唯一命中是 `_stack_changed_ok` docstring 的 `open(...)`，沒有取得檔案 handle。

總結:最高 severity blocker,blocking 共 4 條