severity: minor

# 通才席(測試品質)報告:r4 測試修補(r4-repair-tests.patch)

做法:我在自己的臨時 worktree(5fc4e715)裡做翻紅檢查,共改壞 25 處,清過 `__pycache__`,每處只跑對應的測試。
- 在 `scripts/lumos` 與收集腳本上各拿掉一個守衛,這輪新增的各組測試都有翻紅。
- 翻紅的組:孤立代理字元、負數、警語不被截、佔位人名、`--json` 帶 `stability_unjudged`、SIGHUP/SIGQUIT、收尾中再中斷、錄製啟動空窗、ps 失敗一次、正常結束不留原始日誌、傾印不入原因、擋在碰裝置之前。
- 我沒有跑修前版本。`-k android_memstab_collect` 的 107 案在 5fc4e715 全綠,所以下面幾條都是「測試沒守住」,不是「程式壞了」。

## 發現

**1. SIGINT(Ctrl-C)路徑完全沒有測試,收尾裡擋第二次 Ctrl-C 的守衛拿掉也不紅**
severity: major
blocking: 是
引句:「for sig, label in ((signal.SIGHUP, "SIGHUP(關掉終端機分頁)"), (signal.SIGQUIT, "SIGQUIT(Ctrl-\\)")):」
- 失敗場景:收集腳本的 `cleanup` 寫著「連按兩次 Ctrl-C 也不留日誌」,`main` 也接 `KeyboardInterrupt`。但這輪新測試只送 SIGHUP、SIGQUIT 和 SIGTERM,沒有任何一支送 SIGINT。
- 翻紅檢查(都在 `-k android_memstab_collect_signals` 上跑):
  - 把 `INTERRUPTS + (signal.SIGINT,)` 改成 `INTERRUPTS`:11 passed,0 failed。
  - 改成只忽略 SIGTERM:11 passed,0 failed。
  - 把 `except (Terminated, KeyboardInterrupt)` 改成 `except (Terminated,)`,跑整個 `android_memstab_collect`:107 passed,0 failed。
- 後果:Ctrl-C 是人最常用的中斷方式。第二次 Ctrl-C 若打斷收尾,`logcat.raw`(日誌常含帳號、權杖)與裝置上的錄製都收不掉,CI 抓不到。
- 對照:「收尾中再來一次中斷」那支只用 SIGTERM。拿掉整個 SIG_IGN 迴圈它會翻紅,所以只有 SIGTERM 那一條受保護。
- 修法:再加一支 SIGINT 第一次與收尾中第二次 SIGINT 的測試。
- 歸因:有證據的原有漏查。這輪修補補了守衛卻沒補上它的 SIGINT 腿;只在修後版本驗,修前版本未跑。

**2. `ps_fail_once` 的前置斷言證明不了故障真的被注入,假工具打字錯誤也會假綠**
severity: minor
blocking: 否
引句:「check("前置:ps 被問了不只一次(第一次失敗)", int((fake / "ps.count").read_text()) >= 2, (fake / "ps.count").read_text())」
- 正常流程(沒設 `ps_fail_once`)也會先問一次 alive、等待迴圈再問一次,`ps.count` 本來就至少 2。這條前置在沒有注入故障時也綠。
- 翻紅檢查:把假 adb 的 `n_ps == 0` 改成 `n_ps == 99`(故障永遠不觸發),跑 `-k android_memstab_collect_record_alive`:6 passed,0 failed。
- 對照:把 `perfetto_alive` 在 `rc != 0` 時改回 `return False`,同一測試翻紅,所以結果斷言本身有牙。缺的只是「第一次 ps 真的回了非 0」的證明。
- 規則(03-寫回圖譜.md 〈實作測試品質〉第 4 條):「宣稱測併發、巢狀或寫入失敗,就要建立該情境及前置斷言」。
- 修法:讓假 adb 在故障那次另寫一個標記檔,前置斷言它存在。
- 歸因:有證據的修復回歸(這輪新測試自己的缺口)。

**3. `ps` 的誘餌行沒有「pid 前綴相同或包含 pid」的案例,精確比對拿掉也不紅**
severity: minor
blocking: 否
引句:「lines = ["999 surfaceflinger"]   # 別的行程:不能被當成錄製還活著」
- 失敗場景:收集腳本把比對從裝置端的 `grep -w` 搬到主機端。現在 `perfetto_alive` 只靠 `line.split()[:1] == [pid]` 這一道。假 ps 唯一的別行程是 `999 surfaceflinger`,和 4321 毫無重疊。
- 翻紅檢查:改成 `line.startswith(pid)` 或 `pid in line`,跑 `-k android_memstab_collect`:107 passed、0 failed(`pid in line` 另跑 `-k android_memstab_collect_record`,6 passed、0 failed)。
- 預期:錄製早停、別的行程 `43210 x` 還活著時,應判成錄製提早結束。
- 實際:兩種鬆比對都被當成還活著,測試不紅。
- 修法:在誘餌裡加 `43210 other` 與名稱含 4321 的行。
- 歸因:有證據的修復回歸(grep 換成主機端比對,誘餌沒跟著補)。

**4. 隔離 `XDG_CONFIG_HOME` 的修補沒有任何測試會因它翻紅**
severity: minor
blocking: 否
引句:「GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", XDG_CONFIG_HOME=str(fake / "xdg-empty"),」
- 手動驗證:`HOME` 底下 `.config/git/ignore` 寫 `.lumos/`,設 `GIT_CONFIG_GLOBAL=/dev/null` 時 `git check-ignore -q .lumos/artifacts/x` 回 0(被全域忽略表蓋住);再加 `XDG_CONFIG_HOME=/nonexistent` 回 1。所以修補有道理。
- 翻紅檢查:把這個參數整個拿掉,跑 `-k android_memstab_collect_edges`:19 passed,0 failed。
- 原因:這台機器沒有 `~/.config/git/ignore`,測試也沒有造出被污染的 `HOME`。這個隔離只在使用者剛好有那個檔時才有作用,而測試不會製造那個條件。
- 修法:一支測試把 `HOME` 指到帶有 `.config/git/ignore` 的暫存目錄,斷言「產物目錄沒被忽略」那條照樣回 2。
- 歸因:有證據的修復回歸。

**5. `ps_no_grep` 案例已與 `record_dies_early` 完全相同,註解與案例名稱都過時**
severity: minor
blocking: 否
引句:「# grep 沒篩掉別的行程:只剩腳本自己比對 pid 那一道(代碼審 r2 通才席)」
- 腳本現在不送 grep,假 ps 在 `"grep" not in c` 時一律印全部行程。`ps_no_grep` 旗標因此失去作用,那一整段和前一個 `record_dies_early` 案例做同一件事。
- 假 ps 裡的 `want = c.split()[-1]` 和 `hit` 分支也成了死碼。
- 緊鄰的案例名稱「ps 照 pid 過濾時錄製判成還在跑」同樣描述一個已不存在的行為。
- 這會讓人以為有兩道不同的防線。
- 修法:刪掉重複的案例與死碼,把誘餌加強(見第 3 條)。
- 歸因:有證據的修復回歸(簡化不徹底)。

**6. 新加的 `_ms_orphans` 只套用到部分測試,同檔其他地方仍是手寫版,且四處等待沒檢查是否逾時**
severity: minor
blocking: 否
引句:「left_lc = sp.run(["pgrep", "-f", f"{fake}/adb logcat"], capture_output=True, text=True).stdout.split()」
- `t_android_memstab_collect_cleanup` 仍手寫 pgrep 加 kill 迴圈(同檔,多處),並靠 `left += left_lc` 補丁。helper 與手寫版並存,兩邊以後會漂移。
- 新測試裡 `_ms_wait_for(...)` 的回傳值全被丟掉(SIGHUP/SIGQUIT、收尾中再中斷、啟動空窗、中斷空窗各一處)。等 30 秒逾時就直接往下送訊號。
- 後果:這時送出的訊號可能落在 Python 啟動、`main()` 裝好訊號處理之前,會變成誤紅,訊息指向收尾而不是環境慢。
- 修法:`check("前置:…", _ms_wait_for(...))`。
- 歸因:未判定,純慢機器推論,我沒有造出逾時現場。

## 已驗且未列的

- `_ms_collect` 改成 `**kw` 後預設值只剩 `_ms_prepare` 一處,沒有行為差異。
- NaN 分支移除:`_ms_root` 的 `json.dumps` 預設照樣寫出 NaN 字面,案例仍走到同一個分支。
- text=False:`java_growth`、`instance_limit`、`exits` 會讀 `rt` 的案例都已傳 `text=True`,其餘案例本來就不讀 `rt`。
- 「等日誌跟上」那輪拿掉 `marker`:原本的 `or` 讓它從未生效,沒有行為損失。
- 時間對齊:`perfetto_slow` 睡 5 秒、測試 1 秒後送訊號;`ps_slow` 睡 4 秒、1.5 秒後送訊號;`term_slow` 睡 3 秒、輪詢 0.05 秒。餘裕大,我沒有發現假綠情境。
- `t_android_memstab_collect_cleanup` 的 SIGTERM 與逾時兩段用了「`pgrep` 找到就殺」的收尾:`left += left_lc` 已把紅時只收一組的缺口補上。
- 「擋下不碰裝置」那組測試能偵測到:我在 `main` 開頭插一次假的 `shell(...)`,`collect_edges` 裡三條斷言翻紅。
- 單點翻紅都成立的新增測試:
  - 孤立代理字元、負數(-5 與位元組負數)、警語不被截、佔位人名(check 條目、舊寫法、test_data 三處)。
  - `--json` 帶 `stability_unjudged`。
  - SIGHUP/SIGQUIT 回 2、驅動與日誌串流不成孤兒。
  - 收尾中再 SIGTERM。
  - 錄製啟動空窗(pkill 路徑)。
  - 失敗原因不帶傾印。
  - 正常結束不留 `logcat.raw`。
- 效能:新測試各約 12 秒(signals)、4 秒(start_window)、3.5 秒(result_fields)、7 秒(heap_timeout);`pgrep -fl gctl-ms` 沒有殘留程序。
- 效率側:`text=False` 省下的重複啟動確實成立。

## 修補鏡頭三問

1. 原問題的修復效果:除第 1、2 條外,上述各組修補在修後版本有翻紅證據。我沒有跑修前版本,「修前結果」一律未判定。
2. 修補處的相鄰路徑:SIGTERM、SIGHUP、SIGQUIT 的第一次中斷與收尾中第二次 SIGTERM 成立;SIGINT 路徑未驗(第 1 條)。
3. 新發現案例的修前修後對比:第 1~4 條都只在修後版本跑,未判定是否為修補造成的回歸;第 1、4 條的守衛本來就是這輪新增的。

## 圖譜鏡頭

- `Systems/測試假綠形態.md` 的 ★INVARIANT★:「修 bug 的『還原翻紅釘』必須配一條前置斷言證明現場成立」。第 2 條違反它(ps 失敗那條前置斷言在沒注入故障時也綠),第 4 條也算同類(隔離沒有造出被污染現場)。其餘新測試的前置斷言成立,我都用翻紅檢查驗過。
- 其他固定席節點(`bound-tests-gate`、`guard-kill`、`lumos-cli-read` 等)不受這份測試差異影響:沒有碰這些節點宣稱的行為。

## 清理

已用 `git worktree remove --force` 移除我的 worktree,並刪除臨時目錄;`lsof +D` 事前沒有程序佔用。

最嚴重 severity:major,blocking 共 1 條(第 1 條)。
