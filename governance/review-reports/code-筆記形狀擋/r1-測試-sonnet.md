severity: major

# 筆記形狀擋 r1-tests.patch 測試審查

方法:把 `clone-ns` 整份複製到 `/private/tmp/.../scratchpad/mut/repo`(另開 git 倉庫,不動原 repo),對 `scripts/lumos` 做逐項小改動(mutation),重跑對應 `-k` 子集,看斷言是否翻紅。凡「改壞程式、測試仍綠」的都附了實測指令與輸出。

## F1 refcheck 對釘版本的檢查沒有真的驗到「對那個提交」,只是碰巧仍對得上
severity: major
blocking: 是 —— 移除 `_refcheck_scan` 裡對釘版本另外驗證的整段程式碼,測試仍然全綠,代表這條斷言驗證不到它宣稱要驗的行為(S2 第二句「refcheck 對合法釘版本判對得上」)。

引句:「`'"missing": 0' in r.stdout.replace(" ", " ") or '"missing":0' in r.stdout.replace(" ", "")`」

`t_note_shape_pinned_ref_requires_real_sha_and_line`(`scripts/test_lumos.py` 對應 diff 行 196-199)在同一個 repo 裡直接用 `sha = HEAD` 當釘版本(從 `_ns_repo()` 建完就立刻 `rev-parse HEAD`,中間沒有再改過 `src/a.py`)。這代表「用釘的那個提交驗」跟「不驗、直接照現在的 HEAD 驗」在這個 fixture 裡答案完全一樣——因為兩者根本是同一個提交、同一份檔案內容。實測:把 `scripts/lumos` 裡 `_refcheck_scan`(`scripts/lumos:19941-19947`)對釘版本另外驗證那一段整段拿掉,讓 `path@sha` 形式的 token 直接落回下面「當一般 token 驗」的迴圈(此時驗的是「現在 HEAD 的 src/a.py 第 5 行」,不是「pin 那個提交的 src/a.py 第 5 行」),再跑同一支測試:

```
$ python3 scripts/test_lumos.py -k note_shape_pinned
lumos 測試(1 案例)
t_note_shape_pinned_ref_requires_real_sha_and_line
  ✓ ①合法釘版本:放行
  ...
  ✓ ②refcheck 對合法釘版本判對得上(不再當成一支叫 path@sha 的檔)

────────────────────────────────────────
10 passed, 0 failed
```
(mutation 內容:把
```python
    pinned = {(p_, l_) for p_, l_, _s in pins}
    for token, line, pin in pins:
        sha = _pin_commit(repo_root, pin)
        status, excerpt = _validate_repo_ref(repo_root, token, line, at_sha=sha) if sha else ("missing", "")
        claims.append({"token": f"{token}@{pin}", "line": line, "status": status, "excerpt": excerpt})
```
改成 `pinned = set()`,即整段刪掉。)
全綠——因為 fixture 沒有讓「釘的提交」與「現在 HEAD」的內容分岔,這條斷言測不出 `_refcheck_scan` 是不是真的照 `at_sha` 去驗那個舊提交,還是偷懶驗了現在的樹。要驗到真正的行為,fixture 應該在建立釘版本之後,再對 `src/a.py` 加/刪幾行(讓行號或內容改變),然後釘住較早那個提交,如果 refcheck 沒有真的用 `at_sha`,現在版本第 5 行的內容會跟釘住當時不同,才有機會翻紅。

## F2 「改名認成同一篇」測的是 git 內建行為,不是本次改動接上的 `-M`
severity: major
blocking: 是 —— 移除本次程式碼裡明確加的 `-M`(rename detection)旗標,測試仍然綠,代表這條斷言驗證不到 PRIOR-ART 裡講的「改名用 git 的改名偵測認成同一篇」這個接線是不是真的接上了。

引句:「`check("②改名認成同一篇:舊行不重查", rc == 0, out[-500:])`」

`t_note_lines_scope_rename_and_non_utf8`(diff 行 324-331)用 `git mv` 把 `A.md` 改名成 `A2.md` 再加一行,期待「舊行 `src/a.py:3` 不重查」(rc==0)。但這台環境的 git 是 2.39.2,`git diff`(非 `--raw`)自 2.9 起預設就會做改名偵測,不需要顯式 `-M`。實測:把 `_ns_diff`(`scripts/lumos` 裡的 `_ns_diff`,原本是 `"diff", "-U0", "-M", ...`)的 `-M`拿掉:

```
$ python3 scripts/test_lumos.py -k note_lines_scope
lumos 測試(1 案例)
t_note_lines_scope_rename_and_non_utf8
  ✓ ①summary:算
  ✓ ①decisions 巢狀:算
  ✓ ①aliases:不算
  ✓ ②改名認成同一篇:舊行不重查
  ✓ ③讀不成 UTF-8:rc1 並指名那支檔

────────────────────────────────────────
5 passed, 0 failed
```
用裸 git 指令對照可以看到「有 `-M`」跟「沒有 `-M`」輸出的 diff 完全一樣(都判成 rename,只把新增那一行標成 `+`),因為這個環境沒設 `diff.renames=false`。也就是說:這條斷言目前只是在驗「git 自己的預設值」,不是在驗程式碼有沒有正確接上改名偵測——如果哪次改動不小心把 `-M` 拿掉、或有人在會影響到的 git 設定(`diff.renames=false`)環境裡跑,這條測試不會告訴你接線斷了。

## F3 「不存在路徑」只在沒有釘版本語法時測過,pin 語法壞掉但路徑不存在的組合會被擋,沒人測到
severity: minor
blocking: 否 —— 這是條款要求覆蓋卻沒斷言到的情境(S1 的「不存在路徑不擋」原則),但實際行為是否算違反 S1 有解讀空間(S1 條款字面上只講沒有 `@` 的形式),而且是舉例文字誤觸發、不是真程式檔被誤放行,傷害面小,先降級為提醒。

引句:「`("不存在的路徑", "舉例 `src/nope.py:4`", False),`」

`t_note_shape_line_refs_existing_code_new_only`(diff 行 156)只測了「不存在路徑」的裸寫/反引號形式(沒有 `@` 釘版本),`t_note_shape_pinned_ref_requires_real_sha_and_line`(diff 行 169-199)則全部只用真的存在的 `src/a.py` 搭配各種壞掉的釘法。兩邊都沒有測「不存在的路徑 + 格式不合法的釘版本」這個交集。實測(在 `/private/tmp/.../scratchpad/mut/repo` 用未改動的程式碼直接跑,不是 mutation):

```
$ python3 - <<'EOF'
import sys; sys.path.insert(0, "scripts"); import test_lumos as T
root = T._ns_repo()
T._ns_note(root, body="舉例 `src/nope.py@HEAD:5` 這種不存在的路徑帶無效釘版本")
T._ns_stage(root)
rc, out = T._ns(root)
print("RC:", rc); print(out[-400:])
EOF
RC: 1
擋下:這次提交的筆記有新寫的、程式碼推得出來的形狀(筆記形狀擋)——
  docs/kg-knowledge/Systems/A.md:18  釘版本不合法 `src/nope.py@HEAD:5`:...
```
原因是 `_ns_check_line`(`scripts/lumos:23601-23609`)判斷式是 `if not ok and (p in files or _ns_is_code(p, reader, files) or sha is None)`——只要 `sha is None`(釘法本身格式錯,如 `HEAD`/分支名/太短),不管路徑存不存在都會擋。跟「合法釘法但路徑真的不存在」那條路徑(此時 `sha` 有效但 `_validate_repo_ref` 判 missing,`ok=False` 但 `sha is not None` 且 `p not in files`,不會擋)行為不一致。這個組合(不存在路徑 + 壞掉的 pin 語法)沒有任何一條 S1/S2 測試涵蓋,建議補一個案例把它明釘下來(不管最後決定要擋還是不擋)。

## 總結
三條發現都圍繞同一個模式:fixture 沒有讓「正確實作」與「退化實作」在測試裡產生不同結果。F1(refcheck 釘版本)與 F2(改名偵測)是實測驗證過的假綠——拿掉對應的程式碼路徑,測試依然全綠;F3 是條款組合情境沒被任何測試觸及,目前行為是否合規要看 S1/S2 怎麼裁,先列為 minor 提醒。其餘 S3-S5、S7-S8、S11-S12 相關測試(t_note_shape_current_state_prefix_requires_source、t_note_lines_merge_commit_new_lines_only 的③、t_note_shape_new_code_file_wakes_old_refs 的②)有用 mutation 逐一驗過對應邏輯(移除 exclude_remote、移除 golive 過濾、讓 lint 誤套 FLOW 規則),都正確翻紅,沒有發現假綠。
