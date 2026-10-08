severity: major

# r1 spec對照-sonnet:審 r1-snapshot-tests.patch(鏡頭 spec-conformance)

方法:clone 凍結提交 620a6f73 到臨時目錄,基線 `-k drift_m1` 159 passed / 0 failed(約 33 秒)。再對 `scripts/lumos` 做 42 次單點還原/變異,每次只跑對應測試,看紅不紅。條款 S1–S18 各有一支測試(名稱與條款文字一一對得上),多數釘得深;下面列的是變異後仍全綠的洞。

## F1 S3「起點樹或終點樹任一邊的 about_code 列了它就是家」只測到終點樹
severity: major
blocking: 是
引句:「①家筆記 → 要處理;別篇正文 → 只列出;別篇摘要 → 要處理」
file: `scripts/lumos:29028`
敘述:
1. 條款 S3 與計劃〈做法〉2 都寫「起點或終點樹上的家」,例子是同一個提交把家筆記 about_code 裡刪掉 `a.py`、起點樹還列著,那篇仍是家、那行仍是要處理。
2. `t_drift_m1_layers_and_mode` 的家筆記 `Systems/Pay` 在起點與終點兩邊都列著 `src/pay.py`,只驗到「有列」,沒有任何一支測試造「只有起點樹列了」的情況。
3. 重現:把 `_drift_m1_homes` 的 `for env in envs:` 改成 `for env in envs[:1]:`(只看終點樹),`python3.14 scripts/test_lumos.py -k drift_m1` 得 159 passed / 0 failed。這正是計劃點名要防的繞過(改程式的同時把家筆記的 about_code 一起拿掉就從要處理降成只列出,block 不再擋)。
4. 修法:補一個測試——同一提交刪 `src/a.py` 的名稱並把 Pay 的 about_code 拿掉,斷言那行仍是 handle。

## F2 S6「head_sha 是被推送的終點」測試裡終點恰好等於 HEAD
severity: major
blocking: 是
引句:「①欄位在事件最外層、值對」
file: `scripts/lumos:29245`
敘述:
1. 計劃〈做法〉3 明寫 `head_sha` 要明傳終點,不讓 `_gate_event` 自己 `git rev-parse HEAD`,理由是多 ref 推送或 `--diff A..B` 時兩者不同。
2. `t_drift_m1_events_and_budget` 每次都是 `_m1_run(root, f"{base}..{tip}")` 而 `tip` 就是 HEAD,「head_sha == tip」用預設的 HEAD 也會成立。
3. 重現:在 `_drift_m1_ledger` 呼叫 `_gate_event_or_warn(...)` 時拿掉 `head_sha=tip`,`-k drift_m1_events` 得 14 passed / 0 failed。
4. 修法:另造一個 `--diff A..B` 且 B 不是 HEAD(HEAD 再往後多一個提交)的案例,斷言帳的 head_sha 是 B。

## F3 S4「要處理與只列出兩層都過表態分支」只測了要處理層
severity: minor
blocking: 否
引句:「③分兩次表態 A、B → {A,B} 已表態,不再列」
file: `scripts/lumos:29260`
敘述:
1. 該測試的 `Systems/N` 有 about_code,那一行永遠在 handle 層。
2. 重現:把 `_drift_m1_report` 裡 `listed, _l = _drift_split_acked(listed, acks, vault_rel)` 改成 `pass`,`-k drift_m1_ack` 得 12 passed / 0 failed;結果是只列出層的已表態句會每次重印(噪音,不影響 rc)。
3. 同測試也沒斷言表態檔的 `names` 是排序去重(改成 `[str(n).strip() for n in names]` 仍全綠)。

## F4 S5/做法「沒副檔名的檔要讀首行」沒有任何端到端測試
severity: minor
blocking: 否
引句:「定義快取測試的專案:沒有沒副檔名的檔;src/m<k>.py 各定義兩個名稱,筆記提到其中一個。」
file: `scripts/lumos:28952`
敘述:
1. 計劃寫「沒副檔名的檔要讀首行、每次都讀」,例:改 `scripts/lumos`(`#!` 含 python)當 Python 看。測試只在 `t_drift_m1_code_path_scope` 對 `_drift_m1_code_kind("scripts/lumos", "#!/usr/bin/env python3")` 單點斷言,沒有一個真的 git 範圍裡改到沒副檔名 Python 檔的案例。
2. 重現:把 `_drift_m1_classify` 裡 `if _nodehome_code_kind(p) == "shebang?":\n            need += vers` 改成 `if False:`,`-k drift_m1` 得 159 passed / 0 failed。本工具鏈主程式就是這一型檔,無測試守著它會被讀到。
3. S5 條款子句「快取檔不是自己的」「快取讀寫失敗當沒有快取」也沒有測試(只測了 group/other 可寫、壞 JSON、目錄不可信);「不是自己的」需要換 uid 造不出來,可接受,「寫失敗」可用把快取目錄設唯讀造。

## F5 S2 撤除節:六個範圍宣告字只驗了「下面」、節尾語意沒驗「含子節」
severity: minor
blocking: 否
引句:「②> 下面…歷史紀錄 之後的行不列」
file: `scripts/lumos:28706`
敘述:
1. 條款寫 6 個範圍字(下面、以下、本節、這一節、整篇、之後)與「到節尾,含子節,遇到同層或更高層標題才停」。測試 body 只有「下面」、且每節都是平級 `##`、沒有子標題。
2. 重現(三個獨立變異,各自 `-k drift_m1_history` 13 passed / 0 failed):(a)`_DRIFT_M1_SCOPE_WORDS` 縮成 `("下面",)`;(b)`_drift_m1_retired` 裡 `marks = [(a, lv) for a, lv in marks if lv < lvl_now]` 改成 `marks = []`(遇任何標題就停,子節不看);(c)`_drift_m1_retire_heads` 的 `any(s[1] for s in stack)` 改成只看最內層(節開頭撤除不含子節)。
3. 相對地,「banner 只認 `>`」「撤除行少 `(`」「54 字眼少一個」都被紅到,這幾處釘得好。

## F6 〈做法〉寫了、沒有任何測試碰到的行為(逐條)
severity: minor
blocking: 否
引句:「rc, out = _m1_report(_m1_res(cand=0, text_defs=["src/big.py"], too_long=1), "warn")」
file: `scripts/lumos:29160`
敘述:
1. 「這次有 J 支非 Python 程式檔改動(只看路徑)」那行(`res["other_files"]` 印出):測試 patch 內完全沒有這串字。
2. timeout 且已找到部分發現時印「以下只是已找到的部分」:測試 patch 沒有;`t_drift_m1_whole_word` ④ 造出 timeout 且有發現,但只斷言 state,不看輸出。
3. `LUMOS_SKIP_DRIFT_CHECK=1` / 淺層 clone / 範圍解析失敗時 `m1` 也不跑、不另補帳:沒有測試斷言 m1 沉默。
4. 推送起點算不出來(`base` 是 tuple)→ `m1` 記 git-failed(S6「列不出改到哪些檔」):重現——把 `_drift_old_sentence_check` 的 `if isinstance(base, tuple): raise _DriftM1Stop("git-failed")` 改成 `if False:`,全 159 綠。
5. 帳的 `rows[].names` 排序(`_drift_m1_rows`)拿掉 `sorted` 仍全綠。
6. `drift fix --keep` 經 `cmd_drift_ack` 寫 c2 時名稱傳 None(做法〉3 表態):無測試。
7. 名稱去重鍵、20 筆截斷是共用碼,有測到;`_drift_config` 第四個回傳值在 doctor 端的使用沒有測試(patch 只改了既有測試的拆包)。
8. 〈做法〉「終點語料太大的檔用文字抽」只用「剖不動」造(`src/broken.py`),終點語料裡「超過 4 MB」那一支沒有測;`big.py` 是被改到的那支,不是語料裡沒改到的大檔。
9. 「治理帳沒有共用鎖、要在 Issues/治理帳多個寫入者都沒上鎖 登記 m1」屬筆記面,不在測試 patch 範圍,交給圖譜席。

## 已做的翻紅驗證(全部紅,可視為釘得住)
- S1:終點語料排除測試檔 → ③④紅;S9:檔名不查終點樹 → ②紅、改成 `-M` 配對 → 三處紅、governance/ 算進程式檔 → 六處紅。
- S3:rc_m1 看 gate → ④⑥紅;摘要行不進要處理 → ①紅。S4:只看最新表態、比對忽略原文 → ③紅。
- S5:快取讀不驗權限 → ⑩紅;evict 不看 mtime → ⑪紅;`mkstemp` 換固定檔名 → ⑫紅(148 次寫入中真的有失敗)。
- S6:rows 不截、nodes 不截 → ⑥紅;no-base 記 passed → 兩處紅;`_DRIFT_M1_UNKNOWN` 少 unreadable → 三處紅。
- S7 不過 `_drift_sh` → ②紅;S8 旗標只認 `p.add_argument`、finally 不收、拆包收巢狀 → 各自紅;S10 每 1000 行看時間、完全不看時間、先篩丟中文名稱 → 紅;S12 scan 用全集 → 紅;S13 兩段順序對調 → 紅;S16 終點語料不補 loose、太大當剖不動 → 紅;S18 不擋控制字元 → 紅。

## 前置斷言與環境脆弱度
- 前置斷言:各測試都先斷言 `state == "done"`、候選數或 `parsed > 0` 才驗被測分支,多數帶「①前置」字樣,做得好。缺前置的是 F1(沒造「只起點樹列」)與 F2。
- HOME:`_M1Home` 用 `os.environ["HOME"]` 換成暫存目錄,`~/.cache/lumos/*` 不碰真家目錄;`_m1_run` 子行程也傳 `HOME`。判定上沒發現讀真快取位置的路徑。
- 時間:用假時鐘(`now=`、剖檔計數)而不是真睡;`deadline=100` 配 `now=lambda: 0` 是確定性的。⑪ 用 `time.time() - _DRIFT_M1_DEFS_TTL - 3600` 造舊檔,不依賴日曆。
- `t_drift_m1_code_path_scope` 用 `exec_module` 載入 `governance/eval/drift-exam/old-sentence/old_sentence_exp.py`;沒有該檔時只印一行跳過,不紅。有該檔則跟它的 `_excluded` 綁,參考實作改動會讓本測試連動(可接受,屬設計)。
- `t_drift_m1_defs_cache` 造 4 MB 以上字串與 240000 行檔,整組 2.7 秒,無壓力。⑬ 的抽法雜湊 `ef2e1f3e18464d23` 只依賴 `_drift_py_names` 輸出集合、輸入不含 `except*`/`type`,跨 Python 小版本穩定(本次以 3.14 測)。

## 圖譜鏡頭固定席
- lumos-cli-read(search 預設排除 superseded):diff 不碰 search;不影響。
- bound-tests-gate(綁定測試真跑):新 m1 條款測試名 `t_drift_m1_*` 一支一條款,名稱存在於 test_lumos.py;這次實際跑過 159 條斷言全綠;不影響閘,但 F1/F2 表示「綁了不等於釘住」。
- guard-kill:m1 不動 guard kill 的 rc 與 JSON;不影響。
- 授權與歸屬:測試 patch 沒動 `_VENDORED_TOOLKIT` 或 SPDX 檔頭;不影響。
- 測試假綠形態(★INVARIANT★ 還原翻紅釘要配前置斷言):本 patch 各測試多半守住了這條(見上),但 F1、F2 是「前置沒造到分支」型的第④型假綠,對該合約是輕微違反,已標。
- lumos-cli-lifecycle(re-inject)、design-loop(處置閘、條款綁測試):條款 S1–S18 各自有 `[test:…]`,測試方法名與條款一致;不影響。
- pitfalls-code-loop:測試 patch 改動 `t_private_dir_trust_shared_across_four_sites` 把 `_lens_cache_write` 換成盯 `_home_cache_write` 並新增兩處家目錄寫入點,守衛面擴大而非縮小;不影響。

最高等級:major
