### ext-f1
severity: major
引句:「if d.get("phase") == "converged" and d.get("loop") and d["loop"] not in seen:」
佐證:file: `governance/autonomous_loop/replay_weekly.py:40`
說明:補漏凍結讀錯治理帳 schema。實際 `_loop_gov_mark` 寫的是 `kind="converged"` 與 `nodes=[loop_id]`，沒有 `phase` 或 `loop` 欄位。因此真實收斂紀錄永遠不會被選中，週跑宣稱的「已收斂但未凍結者自動補凍」完全失效；測試卻自行製造了不存在於正式寫側的 schema，所以沒有抓到。

### ext-f2
severity: major
引句:「allv = sorted(p.parent.name for p in rdir.glob("*/verdict.json"))」
佐證:file: `governance/autonomous_loop/replay_weekly.py:98`
說明:凍結路徑直接使用 `loop_id` 建目錄，但週跑只掃一層深的 `*/verdict.json`。合法 loop id 若含斜線，例如既有慣例 `codeloop/<branch>`，產物會落在兩層以上，永遠不會進入新凍必跑、輪替抽樣或完整性回放。相同的一層掃描也讓 `have` 判斷失效，修正 ext-f1 後還會每週反覆嘗試補凍這些 loop。

### ext-f3
severity: major
引句:「g = json.loads(Path(golden).read_text(encoding="utf-8"))」
佐證:file: `scripts/lumos:575`
說明:回放直接信任 golden 裡同時保存的輸入、雜湊集合與預期 verdict，卻不驗 golden 本身是否仍等於凍結時的 Git blob 或受保護指紋。只要 `verdict.json` 被修改，修改者便能同步改 `rows`、`all_row_shas` 和 `verdict`，回放仍會顯示一致。這使「凍結輸入閉包被動」最關鍵的一種資料損壞無法被偵測，golden 不能作為不可竄改的回歸基準。

### ext-f4
severity: major
引句:「out="$(cd "$REPO" && python3 governance/autonomous_loop/replay_weekly.py "$REPO" 2>>"$LOGDIR/replay-$TODAY.err" || true)"」
佐證:file: `governance/autonomous-loop.sh:247`
說明:週跑程式若在產出 JSON 前因 import、語法或未捕捉例外退出，`|| true` 會吞掉失敗，下一行仍寫入本週 stamp。結果是既沒有 LINE 異常通知，也不會在本週後續每日執行時重試，整個回放監測可靜默停擺一週。fail-open 可以不擋主流程，但不應把失敗工作標成已完成。

掃過但乾淨的面：severity 宣告行解析與低報拒絕／高報放行、`spec_path` 落帳、disposal severity/roster 尾巴的 readonly 抑制、G3 frozen SHA override、CLI 參數接線與現有測試調整。
