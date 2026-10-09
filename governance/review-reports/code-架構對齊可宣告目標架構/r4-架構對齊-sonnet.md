severity: major

這輪一個 major、三個 minor。主線與範圍起點、特殊字元跳脫、JSON 輸出、狀態字串、角色警告都有沿用既有工具:共用 `_mainline_ref`、`_json_text_escaped`、`_kill_esc`,狀態字串改成 `git-failed`。沒有跨層直呼。

## 問 1 分層與依賴方向

新碼都放在 `scripts/lumos` 單檔裡,位置跟鄰居一致,也沒有新的跨層呼叫。

- `_lens_trusted_ref` 還是 `_mainline_ref` 加 `_lens_git("merge-base")`。呼叫方向跟 ``scripts/lumos:44938`` 的 `_lens_push_base` 一樣:先取主線,再算分叉點。`_review_roles`、分級、`code-loop check`、派工鏡頭都只是呼叫它。
- `_json_text_escaped(data, indent=None)` 取代 `_json.dumps(data, ensure_ascii=False)`。這跟 ``scripts/lumos:41838`` 的 `_pitfall_diff_mode` 同一條做法,沒有另寫跳脫函式。人讀輸出用 `_kill_esc`,JSON 用 `_json_text_escaped`,分工跟 ``scripts/lumos:13562`` 的 docstring 寫的一致。
- 新測試的夾具(`_role_git_repo`、`_arch_target_repo`、`_arch_lens`、`_arch_pitfalls`、`patch.object(m, "_lens_git", …)`)跟同檔既有測試相同。這個 `patch.object` 寫法在檔裡已有 9 處。

ARC4-1(major):這輪把推送前分級解析 diff 的迴圈改成只照 `\n` 切行,但同一段範圍的鏡頭端平行解析沒有一起改。

引句:「for line in r.stdout.split("\n"):」
file: `scripts/lumos:45378` 的 `_lens_changed_lines` 還是 `for line in r.stdout.splitlines():`。
- 它跑同一個 `git diff -U0`,套同一支 `_stack_changed_ok` 過濾,是 pitfalls 那段收集的鏡頭端複本。它的 docstring ``scripts/lumos:45368`` 自己寫著「★已知重複★」。
- 同一個 diff 現在有兩種切行規則。內容或檔名帶 U+2028 時,分級端的新增行是完整一行,鏡頭端會被切成「+前半」和當脈絡的後半。這跟 r3 COR3-3 修掉的是同一種漏掃,只是落在派工鏡頭的棧別觸發字。
- 同一個修法沒有套到所有相似解析處。`scripts/lumos:5989`(`_scan_diff_for_irreversible_hints`)和 `scripts/lumos:24378`(`_patch_file_changes`)也是 `splitlines`,但它們不是同一條掃描路徑。
- ⚠ 嚴重度請編排者裁。鏡頭端的影響比分級端輕(只是棧別題沒觸發,不是 tier 被繞過),但依「留下舊的平行實作」算 major。
severity: major
blocking: 是

## 問 2 命名與錯誤處理

- 回傳形狀 `(值, 原因)` 跟 ``scripts/lumos:45030`` 的 `_push_range_start`、``scripts/lumos:41140`` 的 `_lumos_config_at_ref` 一致。
- `git-fail` 改成 `git-failed` 是對齊。專案其他地方(``scripts/lumos:33173``、``scripts/lumos:39178``、``scripts/lumos:39203``)都用 `git-failed`。我也 grep 過,`scripts/lumos` 與測試裡沒有殘留的 `git-fail` 字串。
- 警告的形狀 `[目標架構] (目標架構)⚠ …` 跟 ``scripts/lumos:46462`` 的 `_arch_target_fail_text` 一致。

ARC4-2(minor):「沒有主線就退回讀起點」和「附固定說明」這兩步,在四個呼叫處各抄一份,而且各處細節不同。

引句:「if why == "no-mainline":」
引句:「warnings = [*warnings, _TRUSTED_REF_WHY[_why].replace("宣告範圍內的檔照鄰居審", "角色照自動判定")]」
- 出現的地方是 `_review_roles`(``scripts/lumos:26731-26737``)、`_arch_target_check_lines`、`_pitfall_diff_collect`、`_dispatch_lens_arch_text`。
- 前兩處退回起點,最後一處直接 `return ""`。
- 角色鏡頭那處用 `.replace()` 去改常數文字。常數措辭一改,替換會靜默失效。
- 鄰居的做法是一個警告一個常數,例如 ``scripts/lumos:41101`` 的 `_ARCH_TARGET_GIT_FAIL`。
severity: minor
blocking: 否

ARC4-3(minor):有兩個小不一致。

引句:「return None, ("no-common-ancestor" if r.returncode == 1 else "git-failed")」
- 同檔最像的 `_lens_push_base`(``scripts/lumos:44938``)對 merge-base 非 0 一律當「沒有」,最後退到空樹;而 `_push_rev` 的 docstring 寫「回傳碼分不出『沒有』與其他錯」,所以只認跑不起來和逾時。
- 新碼用 `returncode == 1` 區分共同祖先不存在與 git 失敗,對 git 來說是對的,但跟這兩個鄰居的口徑不同。
- 這邊比鄰居嚴謹,不要求改,記一筆。

## 問 3 第二種做法與平行實作

ARC4-4(minor):`_lens_trusted_ref` 的 docstring 解釋了為什麼不併進 `_range_base` 和 `_push_range_start`,卻沒提最接近的 `_lens_push_base`。

引句:「★為什麼不併進 _range_base、_push_range_start★(r3 架構對齊席)」
- `_lens_push_base`(``scripts/lumos:44938``)做的是同一件事:`_mainline_ref` 取主線、`merge-base` 算分叉點、失敗退回空樹並附說明。
- 現在專案裡有四支「主線加分叉點」的函式:`_range_base`、`_push_range_start`、`_lens_push_base`、`_lens_trusted_ref`。
- 語意上分開有理由(失敗時退回鄰居基準而不是空樹),但說明該一併點名 `_lens_push_base`。這支也是 `_lens_trusted_ref` 目前跟 `_push_range_start` 並存時,最容易被誤改的鄰居。

ARC4-5(minor):`_lens_emit_with_extra` 只有有附加段的分支改成無損跳脫,沒有附加段的分支沒改。

引句:「print(_json_text_escaped(data, indent=None))   # 傳輸層無損跳脫,同 pitfalls --json(r3 ARC3-4)」
- 沒有附加段時是 `sys.stdout.write(out)`(``scripts/lumos:46412``),`out` 來自 ``scripts/lumos:46547`` 等處的 `json.dumps(..., ensure_ascii=False)`,沒有跳脫。
- 同一個指令的 JSON 傳輸層因此有兩種做法。
- ⚠ 圖譜段的輸出會不會帶出被審分支可控的檔名,我沒有追到。若會,同一個 U+2028 風險仍在,且 ``scripts/lumos:46417`` 附近的 `out.strip().splitlines()[-1]` 會讀壞。
severity: minor
blocking: 否

不對齊共 5 條,其中 major 1 條

總結最嚴重 severity: major
