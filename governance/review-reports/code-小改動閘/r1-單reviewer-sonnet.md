severity: major

## F1 小改動閘用 `--numstat` 算檔案清單,對「改名」的路徑格式沒特殊處理,把合法的小改動誤擋

severity: major
blocking: yes

`_small_change_check` 用 `git diff --numstat` 拿改動檔清單:

引句:「r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--numstat", git_range, "--"], capture_output=True, text=True, errors="replace")」

拿到的每一行直接切 tab、第三欄當路徑用:

引句:「path = nfc(path.strip())」

問題:`git diff --numstat` 對「改名」的輸出,第三欄不是真路徑,而是 `舊名 => 新名` 的合併語法(git 2.9 起 `diff.renames` 預設開,不用加 `-M` 就會這樣印)。實測(在 `/tmp` 開的乾淨 repo,跟本次審查唯讀規定一致):把 `src/a.py` 改名成 `src/b.py` 並加一行,`git diff --numstat` 印出的是 `1	0	src/{a.py => b.py}`;跨目錄改名則印成 `0	0	{src => lib}/b.py`。這個字串接下來被拿去做三件事,全部壞掉:

1. 算目錄數與落點比對:

引句:「dirs = {str(Path(f[0]).parent) for f in files}」

`Path("{src => lib}/b.py").parent` 是 `"{src => lib}"` 這種假目錄,不是真的 `src` 或 `lib`。

2. 落點內外判斷用 `_nodehome_key(f[0])`,這個合併字串永遠不會等於 about_code 裡宣告的真路徑,即使新檔名就是計劃的家。

3. 算原本行數(相對量)時拿這個合併字串去 `git show base:路徑`,一定讀不到(真實路徑不存在),`lt` 退化成 0,原本行數就算錯。

端到端重現(在 `git -C /Users/enzo/harness/lumos-toolchain worktree add --detach /tmp/seat-sc-reviewer HEAD` 建的乾淨 worktree 裡,拿 `scripts/test_lumos.py` 既有的 `_mk_spec_gate_repo`/`_sg_plan2`/`_sg_commit` fixture 組出最小案例):
一份全靠人驗的雙向門計劃,`lands_in: Systems/Home`,`Home` 的 `about_code` 正確宣告 `tests/test_y.py`(已經照改名後的新檔名寫);把 `tests/test_x.py` `git mv` 成 `tests/test_y.py` 並加一行(總共改動 2 行,遠低於門檻的 5 檔/300 行/20%),提交後跑 `spec-gate --push-check`:

```
=== --numstat(small_change_check 用這個) ===
2	0	tests/{test_x.py => test_y.py}

=== push-check rc: 1 ===
[spec-gate 推送前] ✗ — 1 份雙向門計劃沒過(雙向門不派審,推送閘是它唯一的閘):
    • Projects/甲_計劃.md:全靠人驗的雙向門計劃,這次改動不算小改動——落點外:tests/{test_x.py => test_y.py}(計劃 lands_in/related 那些節點的 about_code 沒列它)(補測試、縮小改動、或升成單向門走設計審;規則版本 1)
```

這正是「二維度、目的、擴散、相對量」四個維度裡「擴散」要保護的正常案例——改動遠小於門檻,about_code 也已經正確登記新檔名——卻被判「落點外」擋下。跟作者在計劃裡自己寫的驗收條件矛盾:小改動閘的整個存在理由就是「不至於要綁測試的小改動別擋」,但只要那次小改動裡帶了一次改名(哪怕只加一行),閘就一定判它落點外。

為什麼是 bug 不是風格:這不是邊界情況的模糊地帶,是這支函式處理它自己宣稱要處理的「一支檔小改動」時,對 git 一個非常常見的操作(改名)給出錯誤答案,而且是機械可重現、跟作者自己的驗收條件矛盾的錯誤答案。`_spec_gate_push_check` 用來偵測候選計劃的 `git diff --name-only`(見 scripts/lumos:5756-5757)本身對改名只印新檔名、不會壞,但 `_small_change_check` 另外自己重跑一次 `--numstat`,兩處對同一個 diff 用了行為不同的 git 選項,沒注意到那個落差。

## F2 逃逸帳「近 N 天」判斷用字串比較 ISO 時間戳,不同時區位移時跟實際先後順序不一致

severity: major
blocking: yes

引句:「cutoff = (_dt.datetime.now().astimezone() - _dt.timedelta(days=C["escape_days"])).isoformat()」

引句:「if str(e.get("ts", "")) < cutoff or not e.get("plan"):」

`ts` 跟 `cutoff` 都是帶時區位移的 ISO8601 字串(例:`2026-09-10T23:30:00+08:00`),但比較用的是 Python 字串 `<`,不是先轉 `datetime` 再比。字串字典序比較只有在所有位移相同時才等於實際時間先後;位移不同時會反過來。

實測(純 Python,不動 repo):

```python
a = "2026-09-10T23:30:00+08:00"   # 換算 UTC 是 09-10 15:30
b = "2026-09-10T16:00:00+00:00"   # UTC 是 09-10 16:00,比 a 晚
a < b            # False —— 字串比較說 a 沒有比 b 早
datetime.fromisoformat(a) < datetime.fromisoformat(b)   # True —— 實際上 a 真的比較早
```

也就是說,只要逃逸帳裡混進不同位移寫法的時間戳(例如同一支工具鏈以後在 UTC 的 CI 環境也寫入逃逸帳,或使用者所在時區改變),`_small_change_check` 判斷「近 90 天有沒有同落點逃逸」時就可能把明明在窗口內的一筆記成窗口外而放行本該擋下的推送,或把窗口外的舊帳誤判成窗口內而多擋一次。目前 `docs/.escape-log.jsonl` 裡現存記錄全部是 `+08:00`(用 `grep -o` 核對過,file: `docs/.escape-log.jsonl`),所以現在還沒有實際觸發,但這是這次新加的比較邏輯本身的缺陷,不是資料現況能保證不出事的東西——`_auto_escape` 寫入處(scripts/lumos:902、8637)本身沒有強制單一時區,純粹靠巧合。

為什麼是 bug 不是風格:這是拿來決定「這個落點最近是不是出過事」的判斷式,判斷錯會讓四個維度之一(歷史)的結論反過來,而修法只要 `str(ts) < cutoff` 換成 `_dt.datetime.fromisoformat(str(ts)) < _dt.datetime.fromisoformat(cutoff)` 就能修掉,成本很低,沒理由留著。

## F3 二進位檔改動在小改動閘裡不算進「相對量」,可以無限大而不觸發擋

severity: minor
blocking: no

`git diff --numstat` 對二進位檔印 `-\t-\t路徑`(兩個破折號代替行數):

引句:「files.append((path, int(la) if la.isdigit() else 0, int(ld) if ld.isdigit() else 0))」

`"-".isdigit()` 是 False,所以二進位檔的新增/刪除行數一律記成 0。落到相對量檢查:

引句:「if churn <= C["max_abs_lines"]: continue」

churn 永遠是 0,0 ≤ 300 恆成立,直接 `continue` 跳過——不管那支二進位檔實際換了多大(例如整支圖片、壓縮檔被整個替換)。擴散(檔數/目錄數/落點)那道維度還是會擋,所以不是完全沒有守門,只是「相對量」這一維度對二進位檔永遠失效。列為 minor 是因為程式碼裡 about_code 通常宣告的是原始碼檔,二進位檔多半本來就會落在「落點外」被擴散那關擋下;真正繞得過的情況(計劃的家本身就是一支二進位檔)很窄,但邏輯上確實是這支函式自己宣稱的四維度裡少了一維的覆蓋率,值得記一筆。

---
LUMOS-IMPACT: a04732b05bdd870115e0e1f85e2c7f0c00b16262..HEAD
