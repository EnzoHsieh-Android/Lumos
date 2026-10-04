severity: minor

審查範圍:/tmp/code-gls-r1.patch 全 1355 行逐 hunk 讀完;並在臨時目錄(/tmp/gls-x)用 python3.14 載入 scripts/lumos 實測(未動 repo)。固定席圖譜筆記:本次派工尾端沒有附 LUMOS-IMPACT 筆記段,故圖譜鏡頭只能就 diff 自帶的合約文字(判定類讀者只讀版控帳、白名單、不丟事件)對照代碼回答,見最後一段。

## F1 合讀函式用 splitlines 切行,含 U+2028 / U+0085 的事件整筆消失
severity: minor
blocking: 否
引句:「        for ln in text.splitlines():」
file: `scripts/lumos:33718`(同庫的 _drift_jsonl_iter 只在 \n 切行,註解明講「治理帳切行規則要一致」)
失敗場景:
1. 寫入端 `json.dumps(..., ensure_ascii=False)` 不會跳脫 U+2028、U+0085、U+2029;帶這種字元的 note/detail 以一行存進本機帳或版控帳。
2. `_gov_ledger_rows_by_time`(`scripts/lumos:1344` 起)用 `str.splitlines()` 讀,這些字元被當成換行,一行 JSON 被切成兩半,兩半 `json.loads` 都失敗,被 `except ValueError: continue` 靜默吞掉。
3. 實測:把 note="a b" 或 "a\u0085b" 的一筆合法事件寫入 .governance-local.jsonl,`_gov_ledger_rows_by_time` 回傳 0 筆(修法:改用 `text.split("\n")`,或直接重用 _drift_jsonl_iter)。
影響面:目前唯一正式消費者是 doctor 規格閘段(spec-gate-run 的 nodes/note),所以只會讓某份計劃的「最近一次紅綠弱」漏列;被替換掉的舊讀法同樣用 splitlines,所以不算新退步,但新函式被宣稱為「統計類讀者的單一合讀入口」,後續接手的讀者會繼承這個洞。當場能翻紅的重現:上面第 3 步;不阻擋。

## F2 兩個程序同時補 .gitignore:重複補行、中間夾空行(不會黏行)
severity: minor
blocking: 否
引句:「    have = {ln.rstrip() for ln in raw.decode("utf-8", "replace").splitlines()}」
file: `scripts/lumos:21050`(_ensure_docs_gitignore 讀、算、追加三步沒有鎖)
失敗場景:
1. docs/.gitignore 內容為 `.ci-log.jsonl`(尾端無換行)。程序 A、B 同時進 `_ensure_docs_gitignore`,各自 `gi.read_bytes()` 都讀到舊內容。
2. 各自算出 missing=兩行,chunk 都以 nl 開頭(因 raw 不以 \n 結尾)。兩個 `open(gi,"ab")` 追加各是一次 write,O_APPEND 下不會交錯,所以沒有「黏成一行」。
3. 實測(兩執行緒用 barrier 卡在讀完之後)結果位元組:`.ci-log.jsonl\n.governance-local.jsonl\n.usage-local.jsonl\n\n.governance-local.jsonl\n.usage-local.jsonl\n`——兩行重複加一個空行。git 對重複行與空行無影響,下一次執行因為 have 已含兩行不再補,所以自癒;只是檔案變髒。
4. 另有一個窗口:`if not gi.exists()` 之後才 `_write_lf(gi, ...)`(覆寫式),兩程序同時建檔寫的是同一份內容,無損;但若第三方在兩步之間已寫入自己的內容,會被覆寫掉(窗口極窄,docs/.gitignore 本來不存在才進這條)。
結論:使用者可見後果為零,維持 minor;若要乾淨,追加前以 `open(gi,"r+b")` 重讀一次再算 missing,或接受重複。

## F3 本機帳讀取成本隨檔案線性成長,且 doctor 完整跑每次整本讀+解析+排序
severity: minor
blocking: 否
引句:「        for _d in _gov_ledger_rows_by_time(env.vault.parent):」
file: `scripts/lumos:2970` 附近(doctor 規格閘段)與 `scripts/lumos:1344`(整本 read_text)
失敗場景:
1. 本機帳沒有輪替也沒有尾端截讀;例行提交/推送/doctor --ci 每次追加十幾到三十筆(doctor --ci 一次寫 25 個 check-* warned 加 doctor-run)。版控帳讀法有 `_gov_tail_bytes` 的 24MB 封頂,這支合讀沒有。
2. 實測:300000 行、75.9 MB 的本機帳,`_gov_ledger_rows_by_time` 耗時 1.3 秒、全部讀入記憶體;每次完整 `lumos doctor` 都付一次。
3. 唯一的防線是 doctor 的「超過 5 MB 軟提醒」(`_local_ledger_doctor_msgs`),只提醒不處理。成本本機自付、不影響別人,也沒有失控的放大路徑,所以不升級。
補充:同一支函式把「版控帳 + 本機帳」整本讀兩次,比被替換的舊讀法(只讀版控帳)多付一份本機帳的量,這是分流的直接代價。

## F4 兩本帳之間被 kill 的狀態:一致,不會重複也不會誤算(正面走查,不算缺陷)
severity: minor
blocking: 否
引句:「    for path, batch in ((vault.parent / ".governance-log.jsonl", tracked),」
file: `scripts/lumos:1526`
走查:`_append_governance_log` 先寫版控帳、再寫本機帳。(a) 在版控帳寫完後被 kill:版控批已完整落盤,本機批整批不存在——讀者看到的是「少了例行觀察」,不會有同一事件兩處都在,故不會重複計數。(b) 在版控帳寫到一半被 kill:留下半行,讀者(`_drift_jsonl_iter` 與合讀函式)遇到非法 JSON 行一律略過;但半行沒有結尾 \n,下一個追加者的第一筆會接在半行後面成為壞行,該筆事件一併丟失——這與分流前同一本帳的行為完全相同,沒有變差。(c) 與 doctor-run 對應的 gov --stats「修好了 vs 還在」統計在本機批遺失時少一個 run 標記,只影響統計文字。結論:無新增損壞模式;此條僅為記錄,不要求修。

## pitfalls manifest 逐條判定
1. `scripts/test_lumos.py:38466` E702(分號):誤報——該行是 diff 裡的未動 context 行(t_delguard_logs_ok_too 內既有的 `...write_text(...); g("add", "-A")`),不是本次新增;本分支沒有引入新的分號多語句。
2. `scripts/lumos:1454` open( 沒有 with:誤報——該行是 `with open(path, "a", encoding="utf-8") as f:`,例外路徑由 with 釋放,外層 `except OSError: return False`。
3. `scripts/lumos:1531` open( 沒有 with:誤報——`with open(path, "a", encoding="utf-8") as f:`,外層 `except OSError: pass`,兩本各自一個 try,本機帳失敗不連累版控帳(測試 t_gov_split_local_write_failure 也釘了)。
4. `scripts/lumos:21064` open( 沒有 with:誤報——`with open(gi, "ab") as f:`,失敗回 `[]`。
四條皆非真隱患(第 1 條與本 diff 無關)。

## 已走過沒問題的範圍
- 多程序同時追加同一本帳(提交前 hook、推送前 hook、doctor --ci):_gate_event 每筆一次 write、一行不超過 4096 位元組(_gate_event_fit 已封頂),O_APPEND 下不交錯;_append_governance_log 同批多筆是先緩衝再於 close 時一次 write(批小於 8 KB),批大時可能在緩衝邊界切開,但這與分流前一模一樣,分流後只是把例行事件移到另一本,各本的併發寫者數量不增反減(版控帳少了例行寫者)。
- 讀者遇到另一程序正在追加的半行:合讀函式與 `_drift_jsonl_iter` 對非法 JSON 行一律略過;未結尾的最後一行若恰好是合法 JSON 前綴不會被誤判成物件(實務上截斷的 JSON 不可能是合法物件)。
- 排序鍵:帶時區與不帶時區混合、不可解析(排最前)、OverflowError/OSError 都在 try 內;時間相同時 Python sorted 穩定,版控帳在前、本機帳在後,spec-gate-run 只寫本機帳,所以「後寫者勝」在同秒內仍成立。
- 子程序與逾時:doctor 對本機帳的 `git ls-files` / `git check-ignore` 各有 timeout=10,逾時 `subprocess.run` 會殺子程序並丟 TimeoutExpired(SubprocessError),被 `except (OSError, _sp.SubprocessError)` 接住並 continue;其餘例外被 doctor 外層 `except Exception` 轉成 fail-open 一行。rc=128(不在 git 內)不提醒,符合 docstring。最壞情況每個檔 20 秒、兩個檔 40 秒,僅 doctor 完整跑才付。
- 判定類讀者(_codeloop_read_from_ledger、dispositions fallback、fix-check、design-loop 血緣、_loop_close_stamps、_escape_released_loops、_lint_new_autopass_count)仍只讀版控帳,而 _GOV_LOCAL_PAIRS 不含 code-loop / fix-check / design-loop(測試 t_gov_split_pairs_drift 釘住);lint-new 的 fail-open 不在白名單內,仍進版控帳。度量段(S18)事件兩本合算、最舊一筆只看版控帳,暖機護欄不被本機帳提早放行,邏輯與註解一致。
- 圖譜鏡頭(無固定席筆記可逐條對):diff 沒有改變「擋人/略過/繞道/自動放行進版控帳」這條合約——白名單要求 (閘,種類) 命中且 hard 恰為 False,其餘一律回 False 進版控帳;_BOOKKEEPING_FILES 與 cochange 排除清單同步補了兩本新帳,舊 .usage-log.jsonl 凍結不 untrack(不會讓別台機器 pull 出事)。
- 無上限成長以外的資源問題:所有新 open 都在 with 內;`_usage_log` 與 `_ensure_docs_gitignore` 的檔案操作皆 try/except 包住,不會讓只讀指令(show/context)因本機帳不可寫而失敗。

總結:本分支併發與資源面沒有阻擋項,僅有切行規則不一致、init 同時補忽略會重複行、本機帳無封頂三處小問題。
