severity: minor

## F1 新共用讀取器 _gov_ledger_rows_by_time 只接 ValueError,遇到深層巢狀的壞行會整支拋 RecursionError
severity: minor
blocking: 否
引句:「            except ValueError:
                continue
            if isinstance(d, dict):
                rows.append(d)」
file: `scripts/lumos:1338`(`_gov_ledger_rows_by_time`);同檔 `scripts/lumos:11261` 另一個治理帳讀者已寫成 `except (ValueError, RecursionError)`,本支沒對齊)
失敗場景:
1. 任一本帳(版控帳或 .governance-local.jsonl)出現一行 200000 個 `[`(合併衝突、半寫、被惡意 PR 塞入皆可)。
2. doctor 的規格閘比例段呼叫 `_gov_ledger_rows_by_time(env.vault.parent)`,走到 `_json.loads(ln)`,拋 RecursionError(它不是 ValueError 的子類)。
3. 我實跑:對含該行的 docs/ 呼叫此函式,輸出 `RAISED RecursionError`。
4. 影響:doctor 該段被外層 `except Exception` 吞掉,整段規格閘紅綠摘要消失(退成 fail-open 提示);測試輔助 `_gov_events_all` 與之後任何統計類呼叫者直接炸。舊程式碼同樣只接 ValueError,所以不是新退步,但這支現在是「兩本合讀」的共用入口,範圍變大。
修法方向:`except (ValueError, RecursionError)`。

## F2 度量式撤除條件(S18)對已分流的閘變成「每台機器各算各的」,新複製的機器會讓 `== 0` 類條件誤成立 ⚠
severity: minor
blocking: 否
引句:「    # ★事件兩本合起來數,「最舊一筆」照舊只看版控帳★(治理帳例行紀錄分流_計劃〈做法〉6):」
file: `scripts/lumos:3973`(同函式 `_doctor_metric_lines`),度量白名單種類見 `docs/lumos-toolchain-knowledge` 的 RULE 文法(blocked/warned/skipped-env/hinted/acked)
失敗場景:
1. 某 RULE 寫 `[retire:度量 note-shape.hinted == 0 近4週]` 或 `check-s.warned == 0 近4週`(這兩個閘的 hinted/warned 已改寫不進版控的本機帳)。
2. 新 clone 的機器沒有本機帳,版控帳最舊一筆早於 4 週前,暖機護欄(只看版控帳 oldest)放行。
3. 該機器近 4 週版控帳內這些事件數是 0(分流後不再寫進去),`== 0` 成立,doctor 提醒「可以撤除」,但別台機器每天都在觸發。
4. 目前 docs 內我只 grep 到文法說明、沒有實際使用這類條件的 RULE,所以是潛在、非當下失敗;判不準是否要禁掉這些閘的度量式,標 ⚠。

## F3 本機帳萬一已被追蹤(曾被 git add -A 提交),doctor 完全不提醒,之後每次例行操作都弄髒工作目錄
severity: minor
blocking: 否
引句:「        if not tracked and ign == 1:
            msgs.append(f"{name} 沒被 .gitignore 忽略,會以未追蹤檔出現")」
file: `scripts/lumos:1370`(`_local_ledger_doctor_msgs`)
失敗場景:
1. 有人 `git add -A` 把 docs/.governance-local.jsonl 提交(diff 的 `_BOOKKEEPING_FILES` 註解自己就預期這情況會發生)。
2. 此後 `tracked == True`,上面條件整個為假,也不管 .gitignore 有沒有該行,不印任何提醒(gitignore 對已追蹤檔無效)。
3. 每次 doctor/show/commit 都 append 該檔,git status 永遠髒,正是本分支要消除的症狀,但 doctor 沒有出口。
4. 應該對 `tracked` 單獨提醒(「本機帳被追蹤了,git rm --cached」)。

## 補充觀察(不計 finding)
- `_ensure_docs_gitignore`:檔頭有 UTF-8 BOM 時,第一行 `﻿.governance-local.jsonl` 不等於 `.governance-local.jsonl`,會多追加一行重複規則(實跑確認:輸出多一個 `.governance-local.jsonl`),只重複一次、下次比對就齊了,無害。混合換行檔案以「有任一 CRLF 就全用 CRLF」追加,實跑 `b"a\nb\r\n"` 得到正確 CRLF 追加。目錄/唯讀 .gitignore 走 OSError 分支回 `[]`,靜默但不崩(我以 root 跑,唯讀情境未能真正驗證權限拒絕)。

## pitfalls manifest 4 條逐條判
1. `scripts/test_lumos.py:38466` ruff E702(分號多語句):誤報。該行是 `t_delguard_logs_ok_too` 內既有的 `(root / "src" / "m.py").write_text(...); g("add", "-A")`,`git blame` 顯示為舊提交 0e715a45c,本 diff 在那一段只是上下文行,不是本分支新增。
2. `scripts/lumos:1454` open( 資源:誤報,是 `with open(path, "a", encoding="utf-8") as f:`(`_gate_event`),with 保證關檔。
3. `scripts/lumos:1531` open( 資源:誤報,同為 `with open(path, ...)`(`_append_governance_log` 分流寫入迴圈),with 保證關檔。
4. `scripts/lumos:21064` open( 資源:誤報,`with open(gi, "ab") as f:`(`_ensure_docs_gitignore`),with 保證關檔。

## 圖譜鏡頭
任務文中的 LUMOS-IMPACT 固定席筆記尾段未附上(prompt 沒有那段內容),本審無法逐條判固定席筆記,只憑程式碼自行查證:
- 判定類讀者(`_codeloop_read_from_ledger`、dispositions 回退、fix-check 事件、design-loop rewrite/converged、lint-new fail-open、loop close stamps)仍只讀版控帳,且名單 `_GOV_LOCAL_PAIRS` 沒有 code-loop/fix-check/design-loop/lint-new,我 grep 全 repo(含 .github、scripts/*.sh)沒有其他外部消費者讀 governance-log。
- CLAUDE.md 要求的鐵則 5「每支檔有家」、doctor 與筆記同次寫回:diff 只含 .gitignore、scripts/lumos、scripts/test_lumos.py 與 `git diff --stat` 所見的筆記/卷證檔,筆記檔內容不在本 patch 內,無法審。

## 已走過沒問題的範圍
- `_gov_ledger_rows_by_time` 排序鍵:ts 缺、非字串、`9999-12-31T23:59:59`(無時區,ValueError)、`0001-01-01...`、只有日期、`Z` 結尾,實跑全部不拋、落到 (0,0.0) 或有效時間;含時區的 9999 年可轉 timestamp(253402318799)。同時間保留讀入順序,版控帳在前。空檔、單行無結尾換行、CRLF 行(splitlines 處理)、BOM 首行(json 失敗被略,舊行為)、目錄當帳檔(IsADirectoryError 屬 OSError)都走 continue,不崩。
- `_local_ledger_doctor_msgs`:git 不在 PATH(FileNotFoundError 屬 OSError,continue)、非 git 目錄(ls-files 與 check-ignore 回 128,`ign == 1` 不成立不提醒)、逾時(TimeoutExpired 屬 SubprocessError)都安全;`_LEDGER_MB_CAP` 在 run_doctor 同層先定義;外層另有 try/except Exception。
- `_gov_routes_local`:`hard` 非布林、缺欄、gate/kind 為 list 或 None 都回 False(進版控帳);`_gate_event_build` 固定寫 `bool(hard)`,所以走 `_gate_event` 的事件 hard 一定是布林。
- `_append_governance_log` 兩本各自開檔、各自吞 OSError,本機帳壞掉不影響版控帳(測試 S4 也涵蓋)。
- `_gate_event`:docs 目錄不存在在更早的地方就回 None,不會因本機路徑多一條分支而改行為。
- `_ensure_docs_gitignore`:docs/ 不存在不建、空檔、尾端無換行補換行、`/.governance-local.jsonl`、`*.jsonl`、`!` 取消忽略這類等效/反向寫法不會被誤判為已有(會追加精確行,行尾追加使其後者生效),`.gitignore` 是目錄時 read_bytes 拋 OSError 回 `[]`;新建 vault 時 `_init_additive_setup` 先於 scaffold,scaffold 以完整清單覆寫,不衝突。
- standalone vault(vault 即 repo 根)時帳檔原本就落在 vault.parent(repo 外),不是本案新增,不列。
- `_doctor_metric_lines`:只有本機帳時 `oldest` 為 None 走暖機不判;只有版控帳時行為與舊相同。
- `cmd_gov` 新舊兩本共用 `_gov_row` 映射,load 對不存在檔略過;`_usage_log` 改寫新帳,舊 .usage-log 凍結不追蹤變動,未見讀者依賴舊帳。
- `_BOOKKEEPING_FILES`、`_COCHANGE_DEFAULT_EXCLUDE` 補入兩本新帳,與舊帳並列。
- 測試改寫:`_gov_since` 以多重集合差取代筆數切片,避免同秒跨帳先後不定;其餘改成兩本合讀的斷言與被測行為一致。

總結:本分支分流邏輯與白名單守得住,極端輸入下只有新共用讀取器對深層巢狀壞行不夠強韌、度量條件的跨機器一致性、以及本機帳被誤追蹤時缺提醒三項低風險問題,沒有阻擋合併的缺陷。
