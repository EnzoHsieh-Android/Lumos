C1 [✅] daily-governance.sh 第26行以 --dry-run 6 呼叫 autonomous-loop.sh,launchd label/09:30單次喚醒(RunAtLoad=false)皆與主張相符 | 證據: governance/daily-governance.sh:26, ~/Library/LaunchAgents/com.enzo.lumos.daily-governance.plist(Label=com.enzo.lumos.daily-governance; StartCalendarInterval Hour=9 Minute=30)

C2 [✅] 真模式無報即以 exit 0 跳過(非錯誤)、dry-run fallback 用最近一份日報,邏輯與主張一致;但真模式此分支現為死碼(MODE≠--dry-run 已在第11-14行提早 exit 2 擋下,2026-07-29裁定停用--pr) | 證據: governance/autonomous-loop.sh:11-14,22-27

C3 [✅] SKIP_CAP=3、skip_n=0 起算,主流程 while 迴圈以 continue 選下一個 gap、達 SKIP_CAP 才結束 | 證據: governance/autonomous-loop.sh:87(SKIP_CAP=3),88-167(while迴圈),163(達cap結束),164(continue)

C4 [✅] gap_select.select 讀 report.gaps[](schema {weakness,suggestion}),經 backlog.add_gaps 以 weakness 去重、pop_top 依 value_score 排序取最高分(top-1) | 證據: governance/autonomous_loop/gap_select.py:59-70, governance/autonomous_loop/backlog.py:16-26(去重),36-40(pop_top排序取top1)

C5 [✅] pending_exists:dryrun 模式檢查 pending_dir 下是否有 *.md;非dryrun檢查 gh pr list --search head:auto/spec- --state open,有結果則視為已有pending、新gap只進backlog不展開(select()第63-64行擋下) | 證據: governance/autonomous_loop/gap_select.py:16-22,63-64

C6 [❌] covered.jsonl 的讀寫只在 gap_select.py 內(load_covered/mark_covered/requeue_unconverged/select),backlog.py 全檔無任何 "covered" 字樣、不涉及 covered.jsonl 讀寫 | 證據: governance/autonomous_loop/backlog.py(grep covered 零命中);governance/autonomous_loop/gap_select.py:25-38,41-56,59-70

C7 [✅] cross_audit.py 呼叫 ENDPOINT=https://dashscope-intl.aliyuncs.com/...(qwen3-max,國際endpoint),回傳含 status/worst_severity;status=="degraded" 觸發於 no_key(無金鑰檔)、HTTPError(reason=http_<code>)、逾時或其他例外(reason=timeout/error:...) | 證據: governance/autonomous_loop/cross_audit.py:15,81,89,105,107-108,111-112

C8 [✅] orchestrator_result.extract_json 從最後一個 '{' 往前試各種結尾,回第一個能 json.loads 成 dict 者,docstring 明講容錯「{clean,minor}」這類非JSON花括號干擾 | 證據: governance/autonomous_loop/orchestrator_result.py:3-18

C9 [✅] scripts/lumos cmd_loop_status:need 未顯式帶入時預設2(CLI --need 預設也是2),good(r)=kind∈(caught,none)且severity∈(clean,minor),converged=最後need輪皆good,converged時exit 0印「✅ CONVERGED」;唯一小差異是判準用kind∈{caught,none}而非僅caught,但none屬canary停用制的旁支值,本pipeline的canary record只用caught/missed,實務上等同主張所述 | 證據: scripts/lumos:4322(exit碼註解),4329-4330(need預設2),4455-4462(good/converged定義),4472(CONVERGED訊息),14289(--need預設2)

C10 [❌] max cap確有預設6(autonomous-loop.sh:7 MAXR="${2:-6}",且daily-governance.sh:26確實傳6)、N=1並發限制確有明文命名(96行log「N=1 gate」);但找不到「連續撞cap」的累計/計次邏輯——單次撞cap(converged≠True)即已在同一次執行中送出LINE告警並exit 0結束(非需連續多次才觸發) | 證據: governance/autonomous-loop.sh:7,96,170-192(單次未收斂即發LINE並exit 0,無連續次數計數)

C11 [❌] dry-run分支確實把spec+可信度報告寫入pending/(檔名沿用spec本身的<date>-<topic>.md命名)並發LINE;但--pr(真模式)分支只做git checkout/commit/gh pr create,並無LINE通知呼叫——LINE通知只在dry-run分支出現一次(259-275行對照,else分支268-275無LINE_TOKEN/line_notify呼叫) | 證據: governance/autonomous-loop.sh:259-267(dry-run含LINE),268-275(--pr分支,無LINE呼叫)

C12 [✅] requeue_unconverged:decay=0.7對value_score衰減、unconverged計數+1,達max_unconv=3時呼叫mark_covered轉入covered.jsonl(放棄自動、留人工),否則寫回backlog | 證據: governance/autonomous_loop/gap_select.py:41-56(decay=0.7, max_unconv=3, n>=max_unconv→mark_covered)

C13 [❌] 實際執行 python3 -m unittest scripts.test_autonomous_loop 顯示 Ran 53 tests...OK,非27個;檔內 grep 'def test_' 亦為53 | 證據: 指令輸出「Ran 53 tests in 0.140s / OK」;scripts/test_autonomous_loop.py(grep -c 'def test_' = 53)

C14 [❌] commit 9fcb761(2026-08-18)確實把LINE token內插('$(cat …)')改成LINE_TOKEN環境變數+Python os.environ.get讀取,日期與機制描述相符;但commit message明寫「六處」且diff只改動6處t=賦值,非主張所稱「七處」 | 證據: git log 9fcb761「fix(loop): 六處 LINE token 內插改環境變數傳遞」(2026-08-18);git show 9fcb761 -- governance/autonomous-loop.sh 顯示6處 t=os.environ.get('LINE_TOKEN','') 取代6處 t='$(cat …)'

C15 [✅] orchestrator-prompt.md 步驟2明寫「canary 限a/b/c、禁d」,步驟3每輪一律「用Agent工具spawn一個opus auditor」(無sonnet起手或missed次數升級的條件邏輯),對skill預設起手模型形成覆寫 | 證據: governance/autonomous_loop/orchestrator-prompt.md:39(canary限a/b/c禁d),46(用Agent工具spawn一個opus auditor)

✅8 ❌6 ❓0 ⏭0
