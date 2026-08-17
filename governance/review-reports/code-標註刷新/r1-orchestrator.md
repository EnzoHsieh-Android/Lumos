# code-標註刷新 r1 編排者對帳報告(carrier)

七席(4 sonnet 分鏡頭+Gemini 外家 finder+spec 對答案+Gemini 否決)findings 去重 21 條,3 條機械反證出局,18 條折入/2 條 accepted。逐條處置與錨定引句(逐字取自 r1-snapshot.patch):

## blocker(3,全折)

**f1 測試盲區:快照釘定路徑零覆蓋**(s3 測試席,mutation 實證:弄壞 pin_snapshot 八案全綠)
引句：「+        if not _setup(re_mod, args.repo, snap):」
處置=新測 t_refresh_snapshot_pinning:--snapshot c1 看不到 c2 節點(釘定壞=翻紅)+假 ref rc2。

**f2 測試盲區:atomic 宣稱無測**(s3,mutation 實證:改裸寫全綠)
引句：「+    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")」
處置=新測 t_refresh_atomic_and_lock:攔截 replace 令炸,原檔必須完好(裸寫翻紅)。

**f3 併發寫 goldset 靜默丟資料**(s2 資源席,實跑重現:一方標註消失+另方假成功)
引句：「+    tmp = p.with_suffix(p.suffix + ".tmp")」
處置=flock 寫入鎖(apply 全程/repin 鎖內重讀再寫)+pid 後綴 tmp;鎖占用快速失敗 rc1;測試釘住。

## major(9:7 折 2 accepted)

**f4 LUMOS 路徑 import 時凍死,跨庫 --repo 用錯版本**(s4 整合席,逐字重現)
引句：「+    re_mod.ROOT = root」
處置=_setup 同步改指 target repo 的 scripts/lumos(缺=顯性警告);eval 側同語意回退。

**f5 stale worktree 登記殘影**(s1 bug 席,實跑重現 prunable 殘留)
引句：「+    shutil.rmtree(_wt, ignore_errors=True)   # 失敗路徑不留殘目錄」
處置=worktree add 成功即註冊清理;無 vault 當場 remove+rmtree;測試斷言 worktree list 乾淨。

**f6 goldset_snapshot 帳面說謊(--live-vault 未釘仍記 sha)**(s1,實跑重現)
引句：「+        _pinned = _snap」
處置=_pinned 初始 None、僅釘定成功才記 sha;e2e 測試釘住(--live-vault 必須記 None)。

**f7 repin head 解析失敗短路,捏造 target 可寫入**(s1,實跑重現)
引句：「+    snap = target if (head and target != head) else None」
處置=head 空=rc2;target 過 rev-parse --verify 存在性驗證;非 git repo 測試釘住。

**f8 delta 失敗被吞照發「已產表」通知**(s2,實跑重現)
引句：「+        log "考卷($tag)未標率超線,已產 delta 表 retrieval-delta-$TODAY-sheet.md 等人放行補標"」
處置=rc+產物存在雙查後才通報;失敗走 ⚠ log 不發 LINE。

**f9 token 含引號炸 python 且被吞**(s5 外家席;同型 s7)
引句：「+t='$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)'」
處置=新增段改 env 傳遞(LINE_TOKEN);既有三處同型=本 diff 範圍外,記 pass note 待另案。

**f10 eval main() 接線零 e2e**(s3)
引句：「+        unj = collect_unjudged(gs, "held")」
處置=e2e 測試真跑 CLI:stdout 未標行+history 三欄+transition 輪;LUMOS_EVAL_HISTORY/LUMOS_EVAL_ROOT 測試導向旗標。

**f11 [accepted] $REPO vs $repo 於通知段**(s5/s7)——接受理由:line_notify 模組屬工具鏈本體,跨庫考卷用本體 $REPO 載入為既有刻意慣例(Landmark 無此模組);非錯配。
引句：「+import sys, os; sys.path.insert(0,'$REPO/governance')」

**f12 [accepted] delta 表 sheet/json 非 atomic 寫**(s2 自判可接受殘餘)——接受理由:觀測性產物可重跑重算,非權威金標;排程週頻率重疊機率低。
引句：「+    Path(out + "-sheet.md").write_text("\n".join(sheet), encoding="utf-8")」

## minor(9,全折/記錄)

**f13 degraded 半鏈未驗落地格式**(s3)→ 鏈測補:gemini 欄落 None。
引句：「+                     "gemini": votes.get("b"), "labeled_at": today,」
**f14 spec 放行介面縮水成生 JSON**(s6)→ merge 預設印逐筆人讀預覽(一致/人裁/兩席值)。
引句：「+    print(f"merge: 一致 {n_a} / 人裁 {n_d}{'(degraded)' if degraded else ''}", file=sys.stderr)」
**f15 合約候選④「計分無 LLM」零守護**(s6)→ 靜態 drift guard 測試。
引句：「+def _history_record(args, gates, ok, reports, unj, pinned_sha):」
**f16 S2 端到端鏈缺**(s6)→ t_refresh_full_chain:delta 真輸出→評審→merge→apply→repin 綠。
引句：「+    a = {"S01": {"Projects/Gamma.md": 2, "Systems/Hub.md": 1}}」
**f17 pin 失敗訊息「退回現況」於 refresh 路徑失真**(s1)→ 訊息拆分:pin 只報失敗,fallback 語句歸 eval main,_setup 明示硬性失敗。
引句：「+    print(f"⚠ snapshot worktree 失敗({r.stderr.strip()[:80]}),退回現況 vault", file=sys.stderr)」
**f18 search_universe 死碼(兩種母體概念並存=回鍋風險)**(s6 觀察)→ 刪除,測試改 _touched_search。
引句：「+def search_universe(q):」
**f19 edit_universe 存在性檢查非重構等價,註解「照舊跳」失真**(s4)→ 註解改明「S0 刻意行為變更」。
引句：「+        # 呼叫收斂進 edit_universe(與評測母體同源,標註刷新 T2);None=file-gone/不可解,照舊跳。」
**f20 T3 鍵存在斷言太鬆/T2 rate 自證**(s3 補充)→ 鏈測以真值鏈補強(repin 綠=count 歸零的行為驗證)。
引句：「+    check("count/denom/rate 齊", all(k in d for k in ("count", "denom", "rate")), str(d)[:200])」
**f21 rater-instructions 全卷框架對 delta 卷**(sheet 卷頭已註記,design-r1 已折;本輪確認實作落地)
引句：「+             "> ★本卷為 delta 片段,案例不連號屬正常★——只列未標候選,已判金標不重出。",」

## 機械反證出局(3)
- s5「build_goldset 缺 import sys」——檔頭第 6 行實有(grep 實證),外家無 repo 之誤。
- s7「mkdtemp 目錄致 worktree add 必敗」——空目錄實測 rc0+三快照重放各吐不同數=釘定在工作。
- manifest「autonomous-loop.sh:64 併發寫入」——該行為 heredoc import 無寫入(s1/s2 一致判誤報)。

## 驗證
修後全量 2723 passed / 0 failed;八案新測+四案修測全先紅後綠(兩條 blocker 的紅由 s3 席 mutation 實驗證成)。
