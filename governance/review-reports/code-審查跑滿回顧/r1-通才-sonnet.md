severity: major

席:通才-sonnet(立場:簡單的守護者、複雜的敵人)。範圍:argparse 與 --help、doctor [I2]、retro-stats --json、loop next JSON、錯誤訊息裡的指令能不能照抄、回退、過度設計、圖譜鏡頭。
實跑環境:自建臨時 repo(照 _cr_repo 造帳,/tmp/r1sonnet/mk.py),對照基準用 d1784414 的 scripts/lumos;沒有碰 repo 內任何檔案與真帳。

### F1 「過期/沒有」時印出來叫人照貼的 `--template > 回顧檔` 會把已經改好的回顧檔清成空骨架
severity: major
blocking: 是 — 處置閘第八步 ✗(過期)時印出的最後一條「建議指令」就是覆寫指令,照抄執行會當場毀掉人剛補完的回顧檔;而「過期」恰恰是人改完檔之後才會看到的狀態。
- 輸入:迴圈已記人裁、已寫好 cap-retro.json 並 `--record`;之後改了檔(例如補一個標點)。
- 走到哪:`lumos loop status <編號> --disposal` → `_disposal_retro_step` 的過期分支。先印「改好、--check 過了重新 --record」,緊接著再印 `lumos loop retro crx --template > governance/review-reports/crx/cap-retro.json`。同一條指令也由 doctor [I2]、retro-stats(沒有/過期的 `cmd` 欄與文字列)、canary record 擋下訊息、cap-decision 成功訊息、loop next 提示、六處手冊逐字帶出。
- 壞在哪:`>` 由 shell 先截斷檔案,`--template` 不檢查檔案是否存在。重現(臨時 repo,在 repo 根貼上閘印出的那一行)後,檔案內容變成 `drafted_by: ""`、`families: [{"family": ""...` 的空骨架,原內容全失。另外 `--template` 回 2(例如還沒記人裁)時,shell 也已先建/清空該檔,留下 0 位元組的 cap-retro.json,之後 `--check` 只會報不是合法 JSON。指令的路徑是相對 repo 根,從別的 cwd 貼會寫到錯位置或因資料夾不存在而失敗。
- 引句:「print(f"    {_cap_retro_template_cmd(root, loop_id)}")」
- 引句:「return (f"lumos loop retro {_shlex.quote(loop_id)} --template > "」
- 重現(輸出已實跑):
  1. `python3 /tmp/r1sonnet/t2.py`
  2. 輸出中 `['[disposal] 跑滿回顧: ✗ — 回顧過期:...', '    改好、lumos loop retro crx --check 過了重新 lumos loop retro crx --record', '    lumos loop retro crx --template > governance/review-reports/crx/cap-retro.json', ...]`
  3. 接著貼該指令(cwd=repo 根),`after paste:` 印出的檔案內容是空骨架(`"drafted_by": "",`)。
- 回退影響:無(純輸出文字);但規格〈名詞〉「過期」的出口就是要人改檔,這條提示正好指向毀檔。

### F2 沒有人裁紀錄的迴圈,處置閘在審查帳有一列絕對路徑含 NUL 時由正常回報變成堆疊(對基準的回歸)
severity: minor
blocking: 否 — 要帳被手改成含 NUL 的 report_path 才會觸發;但違反規格「沒有人裁紀錄的迴圈處置閘行為與現狀完全相同」與「新程式路徑不丟堆疊」。
- 輸入:任一迴圈(沒有人裁紀錄也一樣),審查帳某列 `report_path` 是 `/etc/\u0000x`。
- 走到哪:`_loop_status_disposal` 新增的 `_retro_dir_pre = _retro_has_dossier(...)`(在所有既有步驟之前、無 try 包住)→ `_retro_norm_path` → `Path(s).resolve()`。
- 壞在哪:`ValueError: lstat: embedded null character in path`,整個處置閘丟堆疊。基準版同一帳同一指令:閘正常印「已過閘,可以收」。
- 引句:「for cand in (Path(os.path.normpath(s)), Path(s).resolve()):」
- 引句:「_retro_dir_pre = _retro_has_dossier(root, loop_id, rounds) if root is not None else None」
- 重現:`python3 /tmp/r1sonnet/t3.py`(新版:rc=1 + Traceback 結尾 `ValueError: lstat: embedded null character in path`);`LBIN=/tmp/r1sonnet/lumos_base python3 /tmp/r1sonnet/t3.py`(基準版:`閘:已過閘,可以收`)。

## 已查過、判無洞的角落(不列 finding)
- argparse/--help:cap-decision、retro、retro-stats 三個子指令註冊正確,`lumos loop retro --help` 正常;`retro` 同時給 --check --record 回 2 並講清楚;缺 loop_id 走 argparse 標準訊息。
- loop next JSON:cap-reached 才多一個 `cap_retro`(字串陣列),其餘 phase 沒有這欄;既有鍵與退出碼不變(實跑 rc=1、phase=cap-reached),屬純新增欄位,不破壞靠鍵名取值的消費者。文字模式在 `note` 後多印提示,不影響行解析以外的消費者。
- doctor [I2]:段 id 不與既有衝突(既有 I、新增 I2,位於 A1 之前),實跑印出 ⚠ 並附 `--template` 指令,不計入 issues;例外時降級成 warn_soft 不中斷。
- retro-stats --json:`totals/names/loops/families/actions` 形狀穩定、可 json.loads;`names[...]` 與 `loops` 內容重複(同一批 entry 兩處出現),屬冗餘,但沒有失敗場景,不列。
- 回退:照規格〈回退〉拆掉 canary record 檢查、第八步、loop next 多印、凍結的 retro_skip 即還原;`_KNOWN_GATES` 的 "loop-retro" 只影響 `gov --stats` 的「未出現閘」清單與寫入白名單,既有帳上的 loop-retro 事件拔掉後不會讓 gov 載入報錯;`_gov_routes_local` 不含 loop-retro,事件進版控帳,與讀側 GOV_LOG_NAME 一致。
- 過度設計:`_retro_canary_load`(自讀審查帳)與 `_retro_ledger_rounds`(重算輪數)是另寫的讀帳與輪數算法,與 loop next 的 `rounds_count` 不是同一函式,但規格〈實務隱患〉已明講原因(既有 `_loop_records` 遇壞帳會丟堆疊),不構成需要拔掉的重複;無需要刪的抽象。

## 圖譜鏡頭(LUMOS-IMPACT 固定席;派工尾端沒附節點筆記,我自跑 `lumos impact --diff ce2a961..HEAD` 取固定席逐條判)
- Issues/canary-record未落盤事件(⚠事故,合約 t_canary_record_persist):不影響。新擋點在 canary record 寫入之前、擋下時 rc 2 且不寫帳也不印 ✓,不碰讀回自驗路徑;擋下事件另走 `_gate_event_or_warn`。
- Systems/design-loop(處置閘第五步等 INVARIANT):不影響。第八步獨立附加,fails 清單只在有人裁紀錄且要回顧的迴圈才多一項「跑滿回顧」;回放與凍結三次呼叫以 retro_skip/spec_sha_override 印 —,不改既有判定與 rc(測試 t_cap_retro_existing_gate_steps_unchanged 綁)。
- Systems/loop-convergence-recording(守衛面:canary record、處置閘、loop next 提示):不破壞。無人裁紀錄的迴圈 canary record 放行(實跑 S1 前半);cap-reached 階段名與退出碼不變。唯一新增成本:每次帶 --loop --round 的 canary record 都整本解析審查帳(約 3MB),同輪後續席不讀治理帳,量級可接受。
- Systems/reversibility-governance-ledger / loop-retro 家:不影響。新閘名寫版控帳、`_gate_event` 回傳值有被檢查(寫不進去回 1);讀側遇深層巢狀 JSON 有接 RecursionError(對應 loop-convergence-recording 那條遞迴過深 PITFALL)。
- Systems/lumos-cli-* 、bound-tests-gate、guard-kill 等 INVARIANT:本 diff 只加新子指令與新段落,沒有改動它們宣稱的行為;未見受影響。

總結:最嚴重 major,blocking 1 條
