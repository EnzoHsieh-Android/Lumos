severity: major

# 代碼審 r1 正確性-opus 席(存量漂移改法,base 19162c1e,審材 a/b patch)

實驗環境:`git clone --shared` 到本席自己的臨時目錄(HEAD 53b6389c),直譯器 /opt/homebrew/bin/python3(3.14)。新測試 `-k drift_fix` 在該 clone 全綠(100 passed)。下列重現腳本都借 test_lumos.py 的既有夾具(_df_repo、_df_fix、_nh_file、_df_commit)。

## F1 c2 的 --keep 無視 --dry-run,預覽照樣寫表態檔與治理事件

severity: major
blocking: 是
引句:「return cmd_drift_ack(env, rel, line, "c2", o["reason"])      # 照留:等同帶清單的 c2 表態」
file: `scripts/lumos:28072`
file: `scripts/lumos:28082`

1. 輸入:`lumos drift fix Issues/K 3 --kind c2 --keep --reason "還沒解決等上游" --dry-run`(K 是開著、連到已收尾計劃的 Issue)。
2. 路徑:`_drift_fix_args_err` 不看 dry_run(`_DRIFT_FIX_OPTS` 裡沒有它),所以不擋;接著 28071 行 `kind == "c2" and o.get("keep")` 就直接呼叫 `cmd_drift_ack` 回傳。這一步在 28082 行檢查 dry_run 之前,dry_run 旗標從頭到尾都沒被讀到。`cmd_drift_ack` 會拿鎖、追加 `governance/drift-acks.jsonl`、記一筆 `drift-check acked` 治理事件,最後印出「git add governance/drift-acks.jsonl && git commit」。
3. 違反的約定:[S9]「`--dry-run` 不拿鎖、不寫檔也不寫帳」;argparse 的說明寫「只印改前改後,不寫筆記、不寫帳」;計劃第 1 節第 4 步也這樣寫。使用者照 scan 印出的 `--keep` 指令先加 `--dry-run` 想預覽,結果表態已經落地;照印出的提示提交之後,這筆 c2 就被豁免了。
4. 重現(本席 clone,腳本 rep/r1.py):
   ```
   acks before: False
   rc 0
   ✓ 表態記下了(DACK-771c5546):Issues/K.md 第 3 行照留(…);當時連著 Projects/Done_計劃
   acks after: True {"id": "DACK-771c5546", … "kind": "c2", … "related": ["Projects/Done_計劃.md"], "seq": 1}
   ?? docs/.governance-log.jsonl
   ?? governance/
   ```
   要翻紅,可在 t_drift_fix_c2_close_or_keep 加一條:帶 `--dry-run` 跑 `--keep` 之後,斷言 `drift-acks.jsonl` 不存在。現在這條會紅。
5. 現有測試沒抓到的原因:[S9] 的 dry-run 斷言只跑了 c3;[S11] 的 --keep 斷言沒帶 --dry-run。

## F2 表態綁關係測試第⑦格宣稱的翻紅釘是假的:拿掉字串清單檢查照樣全綠

severity: minor
blocking: 否
引句:「同號改成任一筆涵蓋就算 → ⑥紅;不檢查 related 是字串清單 → ⑦紅;比對綁行號 → ⑧紅。」
file: `scripts/test_lumos.py:53651`
file: `scripts/lumos:27403`

1. ⑦的現場用的是 `related="Projects/Done_計劃.md"`,是字串,不是清單。拿掉 `_drift_related_ok` 之後,`{nfc(x) for x in a["related"]}` 會把這個字串拆成一個個字元的集合。現在的清單 `{"Projects/Done_計劃.md"}` 不是它的子集,結果照樣「沒涵蓋」,⑦照樣綠。
2. 翻紅實驗(本席 clone):把 `_drift_related_ok` 改成 `return True`,清掉 __pycache__ 後跑 `-k drift_ack_binds`,結果是 `✓ ⑦序號最大那筆的 related 不是字串清單:當成沒涵蓋`、`12 passed, 0 failed`。
3. 這道檢查真正擋的是清單裡混了非字串,例如 `related: [1]`。沒有它的話 `nfc(1)` 會丟 TypeError,整支 scan、check、doctor Z 都跟著倒。但⑦的輸入走不到這條路。這正是圖譜「測試假綠形態」合約說的第④型:現場走不到被測分支。

## F3 驗證失敗時教的 git checkout 救法,會連帶抹掉同一篇先前還沒提交的工具修復;修復帳留下已不存在的紀錄,照指示「重跑」也跑不動

severity: minor
blocking: 否
引句:「return (f"寫入後內容跟預期不同(或這一筆還沒處理掉)——在 repo 根目錄跑 git checkout -- {cx['repo_rel']} "」
file: `scripts/lumos:28040`

1. 輸入:一篇驗證紀錄 valid_under 有兩項都含「未提交/還沒提交」。第一次 `drift fix … 5 --kind c4 --old … --new …` 成功(修復帳記 S1,沒提交)。第二次修第 6 行時驗證失敗(用 `LUMOS_DRIFT_FIX_FAULT=verify` 模擬;真實情況是任何讓 handled 不成立的寫入)。
2. 乾淨檢查允許「指紋等於修復帳最後一筆」,所以第二次能在工具留下的未提交改動上動手。但失敗訊息只教 `git checkout -- <路徑>`,這會回到 HEAD,不是回到第二次修之前的狀態。
3. 重現(rep/r3.py)輸出:
   ```
   fix1 rc 0
   fix2 rc 2  擋下:寫入後內容跟預期不同…git checkout -- docs/kg-knowledge/Verification/E.md 還原後重跑
   after checkout, 甲 fix still there? False
   ledger rows: 1 ledger last sha == disk? False
   rerun fix2 rc 2  擋下:Verification/E.md 第 6 行現在不是 c4…
   ```
   第一項的修復被抹掉了,修復帳仍記著它。照訊息原樣重跑第二項會失敗,因為發現回到了第 5 行。
4. 計劃第 1 節第 6 步寫的是「第 1 步保證了…(或只有工具自己的改動),git 一定退得回來」。括號裡這種情況,git 退回的是 HEAD,不是「這次修之前」,這句說法跟行為對不上。

## F4 改法提示與提交提示把筆記路徑原樣塞進 shell 指令、不加引號,檔名帶空白就貼不動

severity: minor
blocking: 否
引句:「base = f"lumos drift fix {node} {line} --kind {kind}"」
file: `scripts/lumos:27570`
file: `scripts/lumos:28094`

1. 輸入:筆記 `Issues/Login fails.md`(開著、連到已收尾計劃)。`drift scan` 印出 `lumos drift fix Issues/Login fails 3 --kind c2 --close --status done --reason "<…>"`。
2. 照貼(rep/r4.py 用 shlex 切):rc 2,「擋下:行號 要給整數,收到的是「fails」。」`_drift_c4_print` 的指令與 `git add {_DRIFT_FIXES} {cx['repo_rel']}` 也有同樣問題。
3. 這些是 [S10] 要人「照貼」的單一產生處。同檔已有前例用 `_shlex.quote` 處理照抄指令(`scripts/lumos:11230` 附近)。本 repo 目前沒有帶空白的檔名,但消費專案(Obsidian 圖譜)常見。

## 其他查過、判定不成立或不報的點(摘要)

- 同一篇連修:c3 之後接 c4、c4 兩項一項一項修,乾淨檢查靠修復帳指紋放行。實測可行,新測試⑦也有涵蓋。
- 兩個 fix 同時改同一篇:鎖內比指紋,後到的會回「判定之後這一篇被改過」(測試③的現場成立)。不同篇之間的序號在鎖內取,不會重號。
- 寫一半:筆記寫完、帳沒寫(例外或被 kill)時,下次乾淨檢查因為指紋對不上帳而擋下。方向安全,只是訊息說成「不是 drift fix 自己留下的」。帳檔殘行在下次追加前會補換行,讀取端也會略過壞行。
- 新舊互讀:舊版讀新表態只比對鍵、不看 related,對舊版來說等於照舊豁免;而 c2、c3 在閘上本來就只列出、不擋。新版讀沒有 related 的舊表態,依設計不再算數。
- 轉正日期:`%as` 取作者自己時區的日期,台北作者凌晨 1 點的提交得到的是台北日期。改名、匯入時「第一次出現的提交」會擋下要人給 `--date`,這是計劃明文寫的。
- E5 改走 `_revisit_lines`:逐項比對舊迴圈的日期、摘要、條件式期限算法,完全等價。
- 改句不越界:`_guard_prose_ops` 與 c1 判定共用 `_guard_planned_prose` 和同一份區段切分。圍欄裡的行、別的段落都不會命中,改完 c1 一定全部消失。

## 圖譜鏡頭固定席逐條判定

- Systems/guard-kill(kill 的 rc 優先序、--json 輸出純度):diff 沒碰 `guard kill` 的程式,只改了 settle、改句與日期推導。**不影響**。
- Systems/lumos-cli-read(search 預設排除 superseded):E5 呼叫的是既有的 `_search_visible_lines`,本身沒改,search 的濾網也沒動。**不影響**。
- Systems/lumos-cli-lifecycle(re-inject 只改 sentinel 之間):沒碰 reinject。簿記名單多了一個帳檔,跟 sentinel 無關。**不影響**。
- Systems/bound-tests-gate(code-loop check 逐支真跑合約測試):閘的程式沒動。`_BOOKKEEPING_FILES` 多了修復帳,只影響留痕豁免與掃描排除,不改變「紅、懸空就擋」。**不影響**。
- Systems/授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT、主檔檔頭帶 SPDX 與 MIT 全文):第一個 hunk 從 2210 行開始,檔頭與白名單都沒碰。**不影響**。
- Systems/測試假綠形態(還原翻紅釘要有前置斷言證明現場成立):**有牴觸**,見 F2。⑦宣稱的翻紅釘在現場走不到被測分支,實測還原後照樣綠。其他新測試大多有①前置格,本席抽驗的 ②③⑥⑧⑩ 都走得到。
- Systems/design-loop(處置閘第五步):沒碰 loop 與處置閘。**不影響**。
- Systems/pitfalls-code-loop(RISK):簿記名單是它的消費者之一。`.jsonl` 在 pitfalls 那端本來就依副檔名排除了,新增的帳檔對它沒有實際效果。**不影響**。

最高嚴重度:major
