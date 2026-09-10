severity: major

### F19 about_code 的「已經有就不動」在 symlink 別名下失效,append 會建出指向同一檔的重複項
severity: minor
blocking: 否 — 只影響 about_code 的排序加分,不建波及連結,不動核心行為
引句:「純字面,不查檔案——remove 要能清掉檔已刪的舊項」
佐證:file: `scripts/lumos:10904` `_about_code_path` 用 `target = (root / v).resolve()` 會穿透 symlink 存出解析後路徑,但 `_about_code_norm`(:10897)是純字面正規化、不查檔案,兩者對同一實體檔可算出不同鍵。
最小重現:repo 根建 `real/a.ts`,`link -> real` 的 symlink,筆記已有 `about_code:\n  - link/a.ts`,執行 `lumos --vault kg append Systems/S about_code link/a.ts`——預期「已經有,檔案沒動」,實測 rc0 印「多了一項 real/a.ts」,檔案變成同時有 `link/a.ts` 與 `real/a.ts` 兩筆指向同一支檔。這正是 r2 F16(`src/../src/a.ts` 疊出第二筆)想關掉的同一類洞,只是換了 symlink 這條路徑繞過去;而且事後 `remove about_code link/a.ts` 只會清掉 `link/a.ts` 那筆,`real/a.ts` 留著清不掉(必須知道兩種寫法各刪一次)。

### F20 席報告「等級字後面緊接 0」豁免正則會誤剝跟計數無關的 0,讓真的 blocker/major 宣告溜過總結句擋下
severity: major
blocking: 是 — 直接讓「總結句不得藏高於檔級的等級」這道守衛對特定文字失效,而這道守衛的用途是 canary 記帳寫側拒收沒正規化的席報告
引句:「_vis_lv = re.sub(r"(?i)\b(?:clean|minor|major|blocker)\b\s*[:：]?\s*0(?![\d.])", "", _strip_inline_markup(ln)[0])」
佐證:file: `scripts/lumos:5232` 正則只認「等級字後面緊接一個 0」,不要求這個 0 是在「其中 major M 條」這種計數語境裡,任何「等級字+可選冒號+空白+字面 0(後面非數字/小數點)」都會被剝掉。
最小重現:`lumos report-normalize <file>`,file 內容為:
```
severity: clean
總結:有 blocker 0 台原型機測試通過,問題很嚴重
```
預期:應被判「總結句提到的等級(blocker)高於檔級宣告(clean)」而擋下(這正是本輪 commit 訊息自己講的「非零照樣算夾帶」的精神,「0 台」量的是台數不是 blocker 顆數)。實測:CLI 印「已是正規化格式,不用改」,rc0,直接放行——句子裡明文寫著「有 blocker」「問題很嚴重」的報告會被判定合格。

### F21 「about_code: [a]」這種沒有逗號的同行清單被擋,但錯誤訊息說「看不懂同一行裡的逗號」
severity: minor
blocking: 否 — 行為仍是 fail-closed(檔案沒動、rc2),只是訊息內容跟觸發原因對不上
引句:「工具看不懂同一行裡的逗號,」
佐證:file: `scripts/lumos:10641` `_list_scalar_value` 的判準是「值以 `[`/`{` 開頭且不是 `[[`」,跟輸入裡有沒有逗號無關;單一元素、零逗號的 `[a]`/`{}`/`"[a]"` 一樣會走進這條丟出「看不懂同一行裡的逗號」的訊息。
最小重現:筆記 frontmatter 寫 `tags: [a]`,執行 `lumos --vault kg append Systems/S tags b`——實測 rc2,訊息「tags 寫成同一行的清單([a]),工具看不懂同一行裡的逗號,硬加會把整串當成一項寫壞」,但 `[a]` 裡根本沒有逗號。

## 前兩輪修法驗收
F1:修到 — 實測 CLI:消費專案 `scripts/hooks/my_own_deploy.py`/`scripts/templates/render.py` 照樣進 claims 且 tier=high,同批 `scripts/hooks/claude/impact-hook.py`(精確清單內)被跳過
F2:修到 — `scripts/lumos:17800` 附近 `if _skip_vendored: lint_claims = [c for c in lint_claims if not _is_vendored_path(...)]` 放在 `if aligned:` 分支之前,兩條路都會濾到
F3:修到 — `_stack_changed_ok` 三個呼叫點(刪除行/新增行/claims 掃描)都已補上 `_skip_vendored` 參數,讀碼逐一核對過
F4:修到 — 實測 CLI:`lumos set Systems/S about_code src/c.ts` 直接 rc2「about_code 不能用 set 改」,既有兩筆清單原封不動
F5:修到 — 實測 CLI:`append about_code /etc/hosts` 與 `append about_code ../outside.ts` 均 rc2 擋下、檔案沒動
F6:修到 — set 的可改清單已不含 about_code(訊息列出的純量清單裡沒有它),append/remove 是唯一入口,「兩套規則」的前提已拆掉
F7:修到 — set 已不收 about_code,含「: 」的路徑改走 append + fmt_list_item 加引號,測試④驗證讀回一字不差
F8:修到 — 承接 r2 三席既有判定(邊界/整合/架構對齊),本輪程式碼未再觸碰該筆記,無新變動需要重驗
F9:修到 — `_vendor_toolchain` 與 `_deinit_remove_vendored` 都改用共用常數 `_VENDORED_TREE_DIRS`,不再各寫一份目錄清單
F10:修到 — `_set_about_code` 這條路本身已被拿掉(set 不再收 about_code),命名不一致的前提不存在了
F11:修到 — `_stack_ext_counts` 改成 `os.walk` 逐層算一次 `rd = relpath(dirpath, _base)`,不再對同一層重算
F12:修到 — `_is_toolchain_repo` 用 `skills/lumos-project-notes/SKILL.md` 判別,測試④與既有 fail-closed 方向一致,讀碼確認未變
F13:修到 — 逐一測試整串加引號、逗號前後多空白、`[[A]] , [[B]]` 等繞法,`_list_scalar_value` 均正確擋下;我另外找的洞(F21)是訊息文字不準,不是判準本身失效
F14:修到 — 實測值已存在時 append 不改寫格式、印「已經有」,不再印「多了一項」;但同類「不動」的保證在 symlink 下失效,見 F19(新洞,不算 F14 本身沒修到)
F15:修到 — 大小寫不敏感磁碟上 `SRC/A.TS` 被擋且訊息指出磁碟上的真實寫法,讀碼與測試⑬一致
F16:修到 — 實測 `about_code: src/../src/a.ts` 再 append `src/a.ts` 確實判「已經有」不疊項;F19 是同一失敗模式在 symlink 這條新路徑上重新出現,判「新洞」而非「F16 沒修到」
F17:修到 — cmd_remove 的 about_code 分支改用 `_about_code_norm` 找項,`./src/gone.ts` 能清掉 `src/gone.ts` 的舊項,讀碼與測試⑫一致
F18:修到 — 授權標頭測試已改用 `getattr(m, "_VENDORED_TREE_DIRS", ())`,不再手寫第三份目錄清單

風險掃描清單那 1 條(`scripts/lumos:17660` 的 `open(`):誤報 — 命中的是 `_stack_changed_ok` docstring 裡「命中 open(...)」這句解釋自我餵食問題的中文註解文字,不是可執行的檔案開啟呼叫。

總結:最高 severity major,blocking 共 1 條
