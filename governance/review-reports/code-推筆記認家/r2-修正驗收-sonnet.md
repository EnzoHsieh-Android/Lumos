severity: major

# r2 修正驗收——code-推筆記認家

1. **G2(★家★跟種類詞黏字串,r1 判 blocker)的程式碼修對了,但四個顯示點全部沒有任何測試釘住空白這件事**——`impact-hook.py` 兩處與 `scripts/lumos` 的 `cmd_impact`/`cmd_impact_diff` 都改成 `" ".join(t for t in (ab, mk) if t)`,人工檢查邏輯正確。但把四處全部還原成舊的字串直接相黏(`hm}{mk}` / `f"{ab}{mk}{ct} …"`),重跑 `t_impact_hook_shows_home_label` 6/6 全綠,`-k impact_home` 36/36 全綠——沒有一條斷言在檢查標記與種類詞之間有沒有空白,全部斷言都只用 `"★家★" in line` 這種子字串比對,跟 r1 合約席指出的「這正是本 repo 自己記過的『測試存在但沒在驗它宣稱要驗的』那個坑再犯一次」一字不差地又發生一次,只是換了個地方犯。
引句:「四處都用 `f"{ab}{mk}...}"` 直接串接,沒有分隔空白」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/hooks/claude/impact-hook.py:651`(修正後)
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/test_lumos.py:36944-36961`(全部斷言只用 `in`,對照組把 651/659 行與 `scripts/lumos:22115/22396` 還原成黏字串後重跑,6/6 與 36/36 仍全綠——已還原)
severity: major
blocking: 是

2. **G3(事故被家的標籤蓋掉,r1 判 major/blocking)的修法沒有任何測試,`_lens_kind_of` 全專案零測試覆蓋**——`scripts/lumos:22446` 新加的 `事故·家` 分支邏輯正確(已用 `_lens_kind_of({"kind":"incident","home":True})` 人工核對回傳 `"事故·家"`),但把整個函式還原成 r1 被抓到的舊版(`if v.get("home"): return _LENS_KIND["home"]`),重跑 `-k dispatch_lens` 65/65 全綠——全專案沒有一支測試構造過「同一節點同時是事故又是家」的 fixture 餵進 `dispatch-lens`。
引句:「一篇同時是事故又是家時,鏡頭把事故蓋掉」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/lumos:22446-22456`(還原成舊版後 `-k dispatch_lens` 65/65 仍全綠——已還原)
severity: major
blocking: 是

3. **G4(CJK 路徑全文掃描判不確認,r1 判 major)的正規表示式改對了,但沒有任何測試用中文路徑餵過**——`_PATH_IN_TEXT_RE` 已從 ASCII 白名單改成排除法(`scripts/lumos:21496-21500`),人工用 `scripts/腳本.py` 驗證確實掃到。但把該行還原成 r1 原文引句裡的那支舊 regex,重跑 `-k home`(318 案例)0 條翻紅——全部斷言都用純 ASCII 路徑(`src/pay.py`、`src/a.py` 之類),沒有一支測試碰過非 ASCII 檔名。
引句:「正文寫出完整路徑就算確認過的家」
引句:「_PATH_IN_TEXT_RE = re.compile(r"[A-Za-z0-9_.@+\-]+(?:/[A-Za-z0-9_.@+\-]+)+")」(還原用的原文字串,取自 r1 邊界席報告的引句)
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/scripts/lumos:21500`(還原成舊 regex 後 `-k home` 318/318 仍全綠——已還原)
severity: major
blocking: 是

4. **G5(about_code 路徑逃脫讀取 repo 外檔案,r1 判 major/blocking)的安全修法用實際攻擊重現驗證有效,但沒有任何自動化測試釘住這個具體行為**——親自造了一個 `about_code: ../../../secret.env` 的節點跑 `home_audit.py sample`,確認修好的版本正確擋下(stderr 印「路徑跑出專案外面」,JSON 裡 `head` 欄位替換成警告文字,沒有洩漏 `secret.env` 內容)。但只把 `cmd_sample` 裡呼叫 `safe_under` 那段換成直接 `repo / p["file"]`(繞過檢查,`safe_under` 函式本身完全沒動),重跑全部 `-k home_audit` 16/16 仍全綠——唯一存在的 `t_home_audit_lumos_path_must_be_inside` 測的是 `--lumos` 那個完全不同的呼叫端(A2),不是這條 about_code 讀取路徑本身。
引句:「能讀到 repo 外任意檔並外洩進版控」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/governance/eval/home_audit.py:121`(`target = safe_under(repo, p["file"])`——繞過此行後 `-k home_audit` 16/16 仍全綠,已還原)
severity: blocker
blocking: 是

5. **G7(人裁檔編號不在批次裡會算出超過 100% 錯誤率,r1 判 major)的修法有效,但沒有任何測試釘住** ——`cmd_tally` 新增的 stray-id 檢查(`governance/eval/home_audit.py` 的 `stray = sorted(wrong - ids)` 段)邏輯正確,人工核對能擋下 r1 原始重現案例的形狀。把這段整段拿掉重跑 `-k home_audit`,16/16 仍全綠——`t_home_audit_tally_counts` 的 ⑤⑥⑦ 三個斷言都只用「wrong 的 id 全部包含在 rows 裡」的情境,沒有一個測案例塞進不存在的編號。
引句:「錯誤率…= 3 對 ÷ 總共 2 對 = 150.0%」
file: `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/governance/eval/home_audit.py:186-193`(stray 檢查段——拿掉後 `-k home_audit` 16/16 仍全綕,已還原)
severity: major
blocking: 是

6. **G6(「從參考道搬進必推」測試假綠,r1 指名要驗)與 G8(健檢舊帳零測試覆蓋,r1 指名要驗)兩條指定重點,修正皆屬實**——已依任務指示分別拿掉 `lane_raw.remove(lane)`(scripts/lumos:21600)與 `_nodehome_ledger` 算 unmentioned 那一段(scripts/lumos:18669-18671),兩次都精準翻紅(前者「③不會同時留在參考道」失敗、後者「①健檢列出…」失敗),證明這兩條是本輪唯一兩處「新測試真的釘住原問題」的地方,不是假綠。此條列出供對照,非扣分項。
引句:「而且從參考道拿掉(同一篇只出現一個地方)」
引句:「整段拿掉照樣全綠——它跟提交前那半是兩份獨立實作」
severity: clean
blocking: 否

## 我驗了哪幾條修正、各自結論

- **G6**(測試假綠·搬進參考道):拿掉 `lane_raw.remove(lane)` → 翻紅(③失敗)。**真的修好,測試真的釘住**。已還原。
- **G8**(健檢零覆蓋):拿掉 `_nodehome_ledger` 算 unmentioned 那段 → 翻紅(①失敗)。**真的修好,測試真的釘住**。已還原。
- **G1**(regen-no-home 擋錯 planned 節點,r1 blocker):拿掉 `status in _NODEHOME_HOME_STATUSES` 過濾 → 翻紅(②失敗)。**真的修好,測試真的釘住**。已還原。
- **G2**(★家★黏字串,r1 blocker):還原四處字串拼接成黏一起的舊寫法 → `t_impact_hook_shows_home_label` 6/6、`-k impact_home` 36/36 全綠不翻紅。**程式碼修對了,但測試完全沒釘住**(finding 1)。已還原。
- **G3**(事故被家蓋掉,r1 major):還原 `_lens_kind_of` 成舊版 → `-k dispatch_lens` 65/65 全綕不翻紅。**程式碼修對了,但零測試覆蓋**(finding 2)。已還原。
- **G4**(CJK 路徑判不確認,r1 major):還原 `_PATH_IN_TEXT_RE` 成 ASCII 白名單 → `-k home` 318/318 全綠不翻紅。**程式碼修對了,但零測試用過非 ASCII 路徑**(finding 3)。已還原。
- **G5**(about_code 路徑逃脫,r1 major/blocking):實攻擊重現確認修法真的擋得住外洩;繞過 `safe_under` 呼叫點 → `-k home_audit` 16/16 全綠不翻紅。**功能真的修好,但這個具體行為零測試覆蓋**(finding 4)。已還原。
- **G7**(人裁檔錯誤率超 100%,r1 major):拿掉 stray-id 檢查段 → `-k home_audit` 16/16 全綕不翻紅。**功能真的修好,但零測試覆蓋**(finding 5)。已還原。

改動過的檔案(`scripts/lumos`、`scripts/hooks/claude/impact-hook.py`、`governance/eval/home_audit.py`)在每次 mutation 後均已用 `cp` 還原並以 `diff -q` 核對與原始位元組完全一致。

```
$ git status --short
 M docs/.governance-log.jsonl
 M "governance/review-reports/code-推筆記認家/r2-sha.txt"
 M "governance/review-reports/code-推筆記認家/r2-snapshot.patch"
```
(以上三個修改都是被審材料本身、非本次驗收動作造成——本次驗收未新增任何未還原的異動。)
