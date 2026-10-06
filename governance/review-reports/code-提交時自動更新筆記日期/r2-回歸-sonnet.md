severity: minor

## F1 分派層兜底例外會讓後面的筆記整批不寫,違反「其他照寫」
severity: minor
blocking: 否
引句:「        except (ValueError, RuntimeError) as ex:」
`cmd_updated_sync` 的迴圈裡 `rc = max(rc, cmd_set(env, rel, "updated", today))` 沒有 try;寫入原語(`atomic_write_verify` 自驗失敗丟 RuntimeError)一丟就跳出整個迴圈,被 main 的新兜底轉成 rc2。結果:第 2 篇寫入失敗時,第 3 篇起都沒寫,與計劃說明「任一篇失敗印原因、其他照寫,最後 rc 非 0」不符;已寫的前幾篇也沒有「改了哪幾篇」的輸出。兜底只解決了「不印堆疊」,沒解決「一篇一篇、失敗不連坐」。另外這個 except 路徑沒有任何測試(diff 的測試只補淺複製、早一天、訊息),要用 monkeypatch 或唯讀檔造一個 RuntimeError 才踩得到,現況刪掉整段 except 測試照綠。
建議:把 try/except 搬進迴圈內逐篇接,印 `擋下 <rel>:原因`、rc=2、繼續下一篇,並補一支測試。

## F2 updated 是非法日期(2026-02-30)時被靜默略過,doctor 永遠不列
severity: minor
blocking: 否
引句:「lag = (_dt.date.fromisoformat(g) - _dt.date.fromisoformat(u)).days」
`re.fullmatch(\d{4}-\d{2}-\d{2})` 放行 `2026-02-30`,`date.fromisoformat` 丟 ValueError 就 continue。舊版字串比較 `u < g` 會列它(updated-sync 剛好能把它修成今天);新版這種壞日期永遠不出現在 doctor 也不進 --stale,也沒有任何提示。機率低、只提醒性質,可接受,但最好改成「解析失敗的 updated 一律當落後列」(壞值本來就該被修)。

## 判斷(其餘鏡頭,無 finding)
- `_git_is_shallow`(`file: scripts/lumos:5937`):git 不存在或 cwd 不存在是 OSError → False;`rev-parse --is-shallow-repository` 在子資料夾也有效;`_vault_repo_root` 會往上找 .git,圖譜在子資料夾沒問題;timeout 預設 None 不會丟 TimeoutExpired。git 不存在時 False 之後 `git_last_change_dates` 回 {},結果是 []。正確。
- 一天容忍:真的落後剛好一天(updated 昨天、正文今天才改)永遠不列,屬已知取捨;下一次再改就會超過一天,或隔天就被列。可接受。
- 時區:`%cs` 是提交者時區的日期,u 是本機日期,最多差一天,被容忍吸收。
- 測試 ④ 在午夜:`y` 與 GIT_COMMITTER_DATE 各自呼叫一次 `date.today()`,只有兩次呼叫跨過午夜才會 lag=2 而紅,窗口是微秒級,可忽略。
- 假綠檢查:我實跑 `-k t_doctor_updated_stale` 5 項、`-k t_updated_sync` 9 項全綠。③ 在舊碼下 updated=2026-09-11 < 淺複製全同一天,會被列,所以對舊碼會紅;④ 舊碼 `u < g` 會列昨天,同樣會紅;① 的 2026-09-11 vs 今天 lag 遠大於 1,保護 `lag > 1` 方向。沒發現假綠。
- 圖譜鏡頭:機械反查三格皆空,無固定席需逐條答;計劃筆記同步了淺複製與一天容忍,內容與程式一致。
引句(正確性):「        if lag > 1:」
引句(測試):「check("③淺複製:不印 updated 落後", "updated 落後" not in r.stdout + r.stderr」
引句(圖譜):「淺複製不判(席位用 depth 1 clone 重現整張日期表變同一天)」

兩條 minor 非阻擋(例外兜底連坐且無測試、非法日期靜默略過);淺複製與一天容忍本身正確,測試無假綠。
