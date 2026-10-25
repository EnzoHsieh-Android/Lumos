severity: major

## F1 紀錄讀改寫不再清洗孤立代理字元,judge 在寫回時崩潰並回 1(固定席:android-e2e-acceptance 的 PITFALL 與 judge_ui 的 WHY)
severity: major
blocking: 是

引句:「rec, err = _e2e_load_json(p, scrub=False)」

file:`scripts/lumos:40670`(`_e2e_record_update`)走到 `scripts/lumos:28457`(`_write_lf` 的 `text.encode("utf-8")`)。

失敗場景:
- 紀錄檔的放行理由裡有 JSON 轉義的孤立代理字元 `"bad\ud800"`,同一份指紋再跑一次 judge。
- 修補把紀錄讀回改成 `scrub=False`,為的是保住人寫的換行與 tab。
- 但這同時拿掉了孤立代理字元的清洗。`json.dumps(ensure_ascii=False)` 之後,`_write_lf` 丟 `UnicodeEncodeError`。
- judge 帶 traceback 結束,回傳碼是 1。1 的合約是「寫了紀錄但沒通過」,實際上什麼都沒寫。
- 範本腳本把這個 1 當成 judge 的結果回傳。
- 專案自己在 `Systems/android-e2e-acceptance.md` 已把「孤立代理字元讓寫紀錄時整支崩」列為要防的一類(WHY 行 15)。這次修補只想保住換行與 tab,卻把這一類又放了回來。

重現(在 /tmp 的 clone 內暫加一支測試跑 `python3.14 scripts/test_lumos.py -k zz_probe`;做法:先跑一次 judge 寫出紀錄,把紀錄的 waivers 改成 `[{"by":"human","reason":"bad\ud800"}]`,再對新 run_id 跑 `_e2e_judge`):

| 版本 | 結果 |
|---|---|
| 修前 73f36793 | rc=0,stderr 空,有寫紀錄 |
| 修後 aba0d9cd | rc=1,stderr 結尾是 `UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 1198: surrogates not allowed`,沒寫紀錄 |

建議:換行與 tab 保留,只清孤立代理字元,不要整個關掉清洗。

歸因:有證據的修復回歸(兩版同一案例,修前通過、修後崩潰)。

## F2 `_e2e_config_at` 改走 `_lumos_config_at_ref` 後,讀 HEAD 的 macrobench.json 會收 BOM,跟 `_macrobench_config` 讀工作目錄的寬容度不一致
severity: minor
blocking: 否

引句:「d, st = _lumos_config_at_ref(root, rev, strict=True, rel=".lumos/macrobench.json")」

file:`scripts/lumos:60172`(`_json_at_ref` 會對內容做 `.lstrip("\ufeff")`)對上 `scripts/lumos:39398`(`_macrobench_config` 用 `read_text(encoding="utf-8")`,BOM 會讓 `json.loads` 丟錯)。

失敗場景:
- HEAD 提交的 `.lumos/macrobench.json` 開頭帶 BOM。
- 修前 `_e2e_config_at` 回錯誤「不是合格的 JSON:Unexpected UTF-8 BOM」,跟 `_macrobench_config` 一致。
- 修後 `_e2e_config_at` 回 `({'e2e': {}}, None)`,工作目錄那條仍然拒收。
- 修前的註解明寫「同一個檔兩條讀法容忍度要一樣」,這條約束被悄悄拿掉,新 docstring 也沒提 BOM。

重現:對有 BOM 的 macrobench.json 提交,分別在兩版的 `scripts/lumos` 上呼叫 `_e2e_config_at(repo, "HEAD")` 與 `_macrobench_config(repo)`。

| 版本 | `_e2e_config_at` | `_macrobench_config` |
|---|---|---|
| 修前 | 回錯誤 | 回錯誤 |
| 修後 | 回設定 | 回錯誤 |

實際影響很小:範本腳本 `load_config` 先過 `--check-config`,帶 BOM 的設定到不了 judge。所以只降為 minor。建議在 `_e2e_config_at` 對 BOM 補一道拒收,或把這個差異寫進 docstring。

歸因:有證據的修復回歸(兩版同一輸入,結果相反)。

## F3 `kill_group` 的 docstring 與範本檔頭仍寫「還在才 KILL」,跟新行為(一律補 KILL)矛盾
severity: minor
blocking: 否

引句:「還在才 KILL。收集腳本的子程序各自成組,它們得靠收集腳本自己收,所以不能一開始就 KILL。」

file:`scripts/templates/android-e2e-run.sh:80`(docstring 同一段第一行寫「寬限到了一律補 KILL」,第二行寫「還在才 KILL」)。檔頭 `scripts/templates/android-e2e-run.sh:11` 的 `LUMOS_E2E_STOP_GRACE` 說明寫「等完還在才 KILL」,也是舊語意。

失敗場景:
- 照檔頭設定寬限的人,會以為領頭在寬限內自己退了就不會再有 KILL。
- 實際上領頭退了之後,同組裡還在做收尾的成員會立刻被 KILL。

建議:檔頭與 docstring 改成「寬限結束後一律對整組補 KILL」。

歸因:有證據的修復回歸(文件沒跟著行為改)。

## 本案特定鏡頭的結論

**程序群組編號被重用**
- 會變得更危險,但實際窗口極窄,不標 finding。
- 修前 `kill_group` 在 `p.poll()` 已有回傳碼時直接 return,不再碰群組編號。修後會對已回收領頭的 `p.pid` 補一次 `killpg(KILL)`。
- 群組裡已經沒人時,編號理論上可被新程序重用。
- 但能走到這條路的只有兩種情況:
  - 領頭剛被 `wait` 或 `poll` 回收,同組成員還在,此時編號有效,正是修補要的情況。
  - 在 `communicate` 回傳之後、`return` 之前的幾個位元組碼內收到中斷。
- 這兩種都要靠編號循環到同一個值才會誤傷別人,我沒有可重現的案例。
- `start_new_session=True` 保證不會打到自己的群組。

**寬限中被中斷,往上丟之後會不會再對同一組送訊號**
- 不會。`on_term` 與 `on_int` 先呼叫 `stop_listening`,之後的訊號都被忽略。
- `run()` 的 `finally` 會把該程序從 `GROUPS` 移掉,主流程 `except` 裡的 `for p in list(GROUPS)` 因此是空迴圈。
- 逾時分支(`except subprocess.TimeoutExpired`)裡丟出的例外會直接往上,不經同一個 `try` 的 `except BaseException`,所以也不會重送。
- 唯一殘留的窗口是 `kill_group` 第一行 `poll()` 與 `try:` 之間的幾個位元組碼。我不標,因為給不出可重現的輸入。

**`say()` 換成 /dev/null 之後,擋下訊息去哪了**
- 之後的 `die` 與 judge 逾時的「擋下」都會進 /dev/null。
- 只有 EIO(終端被關)、EPIPE 與已關閉的檔案這類永久性斷線會觸發換掉,斷線時本來就沒有人能看到。
- 檔案寫滿(ENOSPC)這類暫時性失敗理論上也會永久靜音,但沒有具體失敗場景,不標。
- judge 子程序繼承的是檔案描述符 2,不受 `sys.stderr` 替換影響。
- `steps.json` 與紀錄仍照寫,回傳碼是 2。

**`rel` 參數與 BOM**
- 見 F2。`rel` 只拼進 `f"{ref}:{rel}"`,呼叫端都是常數,沒有注入問題。
- 角色鏡頭與目標架構呼叫端沒變,預設值不變。

## 三問

**1. 原問題的修復效果有何行為證據?**
- 我把修後的測試檔放到修前的程式上跑 `-k android_e2e_run_script`,結果 37 通過、3 失敗。三條失敗的案例原本有問題,正是本輪三個修補的對應案例:
  - 錯誤輸出斷了回傳碼照樣是 2,修前回傳碼是 120。
  - 逾時後寬限中又被中斷,不理 TERM 的子程序要收掉,修前該子程序仍存活(pid 33086)。
  - 同組裡不理 TERM 的成員要收掉,修前仍存活(pid 33266)。
- 修後同一支測試 40 通過、0 失敗(`-k android_e2e_run_script`)。
- 因此以下三項已確認:s1、s2(KILL 補送)、s3(回傳碼 2)。
- 放行理由原樣保留(s4)與 s5 的不寫提醒,我讀了測試與程式,沒有另跑修前紅。屬於未判定「修前紅」的部分。
- s4 的保留效果在 F1 的輸入上附帶出新的回歸。

**2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常跑完回 0、沒過回 1、TERM 中斷時 trap 收尾有跑、裝置鎖放掉:同一支測試修後全綠。
- 錯誤路徑裡的 `kill_group` 與 `GROUPS` 收尾沒有二次送訊號。
- 相鄰的紀錄讀改寫路徑不成立,見 F1。
- BOM 路徑不一致,見 F2。

**3. 新發現的同一案例,修前與修後各是什麼結果?**
- F1:修前 rc=0 且有寫紀錄;修後 rc=1,`UnicodeEncodeError`,沒寫紀錄。
- F2:修前兩條讀法都拒收;修後 `_e2e_config_at` 收、`_macrobench_config` 拒。
- F3:文件不一致,無執行行為可比。

**未驗範圍**
- 全套 `-k android_e2e`、macrobench、android_memstab、role_card、arch_target 我沒有重跑。
- 程序群組編號重用沒有實測。
- 實機的 Maestro、adb 與 Gradle 路徑沒有驗。
- 暫存目錄已刪;我另外留下的 `gctl-run-*` 現場有一份來源不明,沒動。

總結:最嚴重是 major,blocking 1 條(F1)。
