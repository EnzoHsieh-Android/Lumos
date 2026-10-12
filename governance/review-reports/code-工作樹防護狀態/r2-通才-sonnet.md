severity: minor

我逐 hunk 讀完整份 diff 和修補差異,在暫存的 repo 與附加工作樹裡實跑了 20 多種輸入。`python3.14 scripts/test_lumos.py -k hooks_path` 是 28 passed、0 failed。沒有 major 以上的發現,只有三條 minor。

### 1. 工作樹的 hook 讀不到時,該列掉成 unknown,說明是原始 Errno
severity: minor
blocking: 否
引句:「if ok and f.is_file() and not filecmp.cmp(f, eff, shallow=False):」
file: `scripts/lumos:26014`
- 輸入:附加工作樹的 `scripts/hooks/pre-push` 權限是 000,生效那份(主工作目錄)正常。
- 路徑:`filecmp.cmp` 丟出 PermissionError,被外層 `except Exception` 接住,走到 `add(layer, "unknown", str(e))`。
- 實測輸出:`❔ git-pre-push unknown [Errno 13] Permission denied: '/private/tmp/.../wt/scripts/hooks/pre-push'`。
- 後果:`unknown` 不進 `enforcement_summary` 分母,進場提醒也不點名(只點名 inactive 與 degraded)。這時真正生效的主工作目錄那份其實是好的,說明卻只剩一段 Errno,沒說是哪個檔讀不到。
- 發生機率低,它只影響自己工作樹裡那份檔。
- 歸因:未判定。修前版本用 `_same_bytes` 吃掉 `OSError`,同輸入會判成 degraded;所以這是 filecmp 取代 `_same_bytes` 的修補行為差異,可算有證據的修復改動,但嚴重度低。我沒有另跑修前版本的同輸入,只靠讀碼對照。

### 2. 測試有兩處判準不獨立,改壞實作還是綠
severity: minor
blocking: 否
引句:「check("★說明要講跑的是主工作目錄那份(%s)★" % layer, str(mh.resolve()) in ln or str(mh) in ln, ln)」
file: `scripts/test_lumos.py:46563`
- 輸入:說明字串開頭本來就是 `core.hooksPath={hp}`,而 `hp` 就是 `str(mh)`。
- 路徑:就算把「生效的是同 repo 另一個工作目錄那份 …」整段文字刪掉,這條斷言仍成立,等於永遠為真。
- 另一個缺口:沒有任何案例涵蓋「生效那份存在但不可執行」。把 `ok = eff.is_file() and os.access(...)` 的 `os.access` 拿掉,所有斷言照綠。我實跑確認現行實作對這種輸入回 inactive,只是測試守不住。
- 另一個缺口:sibling 分支下,生效那份 pre-push 沒帶 `--gate` 的情形沒有測試。我手跑確認結果正確(inactive 並點名生效那份),只是這條測試沒釘。
- 歸因:有證據的原有漏查。這些斷言從上一輪就在,修補沒碰它們。

### 3. 分支比主工作目錄舊時,degraded 會常駐
severity: minor
blocking: 否
引句:「add(layer, "degraded", det + f";本工作目錄的 {fn} 跟它不同,推送時跑的不是這份")」
file: `scripts/lumos:26015`
- 輸入:附加工作樹所在的分支早於主工作目錄的 hook 更新,所以兩份 `pre-push` 內容不同。
- 路徑:判成 degraded。實測 `⚠️ git-pre-push degraded ...跟它不同`,修前、修後都一樣。
- 後果:`lumos-entry-hook.py:172` 的 `_enforcement_alert` 每個 session 都會喊「防護有 1 層沒生效」,直到分支 rebase。這時推送實際跑的是比較新的主工作目錄那份,警告方向偏悲觀,可能造成警報疲勞。
- 這是作者刻意的設計(測試也釘它),不是 bug。我只把它列為觀察,不要求改。
- 歸因:有證據的原有行為,修補沒有改變它。

### 三問

**① 原問題的修復效果有何行為證據?**
- 我取修前版本(`eae32d2d`)的 `scripts/lumos`,和現行版本放在同一個附加工作樹實跑對照。
- 原問題「附加工作樹裡 hooksPath 指向主工作目錄會判 inactive」:現行版本實測 active,說明寫出生效那份的路徑。見下方案例 2。
- R2 兩個修復在現行版本都成立,見案例 A 與 B。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 主工作目錄自己、hooksPath 是相對的 `scripts/hooks`:`sib` 為 None,仍走舊路徑,判 active,而且不多跑 git。
- 經 symlink 路徑指向主工作目錄:active。
- 從工作樹的子資料夾執行:active。
- 指向另一個附加工作樹(wt2):active。
- 大小寫錯的路徑(`/TMP/…`):active,因為兩邊都 `resolve()`。
- `~` 開頭但不存在的路徑:inactive,因為 `vp.is_dir()` 為假,回 None。
- 殘留的已刪工作樹資料夾,以及 repo 內的子資料夾 `main/dead/scripts/hooks`:inactive,`--show-toplevel` 不等於 `other`。
- 不同 clone:`--git-common-dir` 不同,回 None。這一條只靠讀碼和測試的「無關 repo」案例,我沒另外造 clone。
- 生效那份不可執行:inactive。

**③ 新發現的同一案例,修前、修後各是什麼結果?**
- 發現 1:修前 degraded(`_same_bytes` 吞掉 OSError),修後 unknown。這一組沒有另跑修前版本。
- 發現 2:是測試判準問題,與修前修後的程式行為無關。
- 發現 3:修前、修後都是 degraded,結果一致。

### 本案特定鏡頭

- **(a)「同一個 repo、另一個工作目錄根」能不能被騙或誤判:**
  - 另一個 clone、殘留資料夾、子資料夾這三種,我都實跑確認會回 None。
  - symlink 與大小寫不影響結果,因為兩邊都 `resolve()`,而且 git 輸出也是真實路徑。
  - 主工作目錄本身在 `_hooks_path_is_ours` 就先短路。
  - 一個可接受的偏差:`root` 是主工作目錄、hooksPath 指向 wt2 時也判 active,因為它確實是同 repo 另一個工作目錄根。
  - git 2.39 支援 `--path-format`。更舊的 git 會讓 `_rev` 回 None,退回舊的 inactive,這是安全方向。
- **(b) git 呼叫次數與最壞等待:**
  - `sib` 在迴圈外只算一次,最多 3 次 `_lens_git`,每次 3 秒,最壞約 9 秒。
  - 只有 hooksPath 有設、不是自家、而且名稱是 `scripts/hooks` 且目錄存在時才會走到。
  - 實測整個 enforcement 約 0.82 秒(修後)對 0.76 秒(修前)。
  - 進場 hook 有自己的 `_inner_budget`,超時會 fail-open 回 None。逾時時 `_rev` 回 None,會退回 inactive,和修前同樣是誤報,不是新退步。
- **唯讀:** `_rev` 只呼叫 `git rev-parse`,不改任何東西,filecmp 只讀檔。
- **衍生資料:** `--json` 的 rows、`enforcement_summary` 分母與進場提醒,都只認 `status` 欄位,沒有新值域。degraded 本來就在 `_enforcement_alert` 的點名清單裡,不會多出未處理的狀態。

### 圖譜鏡頭

- `lumos-cli-read`:新增的筆記段落講的是 enforcement 行為,不碰 search 的 INVARIANT,不影響。
- `lumos-cli-lifecycle`:`_hooks_path_is_ours` 沒被放寬,deinit 與 teardown 的拆除守衛不變,不影響 re-inject 的 INVARIANT。
- `guard-kill`、`bound-tests-gate`、`授權與歸屬`:這份 diff 沒碰 guard kill 的 rc 優先序與 JSON 純度、bound-tests 閘、授權檔白名單。唯一牽連是 `scripts/lumos` 檔頭,這份 diff 沒改它。
- `測試假綠形態`:這條要求還原翻紅釘要有前置斷言證明現場成立。新測試用 `str(mh) in ln` 當說明斷言,正是發現 2 指出的不獨立形態,但沒破壞該合約。
- `pitfalls-code-loop`、`loop-convergence-recording`:只是列為牽連,沒有宣稱被這份 diff 破壞的行為。

### 未驗範圍

- 沒有實測 symlink 的 `other` 與 git 回傳路徑不一致的組合。
- 沒有實測裸 repo 與 submodule,只靠讀碼判斷。
- 沒有實測 git 版本低於 2.31。
- 沒有實測 git 呼叫真的逾時的路徑。

**環境註記:** 審查席的寫檔守衛只放行 `/tmp/lumos-seat-work/code-工作樹防護狀態/通才-sonnet/`,不是派工詞寫的 `…/通才-sonnet-r2/`,所以我的實驗用了前者。實驗結束後已自行刪掉,`lsof` 沒有程序占用。

總結:最高等級 minor
