# code-dref r1 架構對齊席
sha256 已核對 = cb5b11f0c29170ffda4f24392c8318f7c86f3e1e577b8933da5c847ebfb75d38。

### arch-f1
severity: blocker
引句:「lines, _s, e_fm = load_raw_for_edit(path)」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:52`
說明:_node_decisions 每次用 load_raw_for_edit 重讀檔,不複用 env.notes[rel].fm_lines(全檔 8 處 parse_decisions 含 E2 都走記憶體)。load_raw_for_edit 是寫入前置、拒 BOM/CRLF,把硬拒絕吞成靜默 []。純讀查詢(backlog/candidates)對格式稍偏節點候選悄悄消失。

### arch-f2
severity: blocker
引句:「if d.get("valid", True):   # 只看翻案(valid:false)決策」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:259`
說明:parse_decisions 欄位一律存字串,既有寫法都 str(d.get("valid","true")).lower()=="false"。這裡 d.get("valid",True) 當 bool,存字串 "false" 非空恆真→永遠 continue→coverage_scan 抓不到任何翻案決策,promote 覆蓋提醒形同沒寫。

### arch-f3
severity: major
引句:「"valid": bool(valid), "already_filled": already})」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:139`
說明:同 truthy 誤用另一發作點。_dref_candidates 把 d.get("valid",True) 塞候選 tuple,bool() 三種情況全 True,candidates 的 [已翻案] 標記永不顯示。

### arch-f4
severity: major
引句:「fm.insert(last + 1, f"{indent}- {quoted}")」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:338`
說明:promote 加正欄段手寫重複 _append_decision_ref 的清單插入邏輯(找 quote/縮排/區塊末非空行/insert),兩份各自維護同一件事=重造已有工具。

### arch-f5
severity: major
引句:「del fm[target_j]」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:241`
說明:_dref_remove_ref 只 del 那行不檢查清單清空;既有 edit_fm_remove 清完若 list 空連 key 行移除(裸鍵被 YAML 解 null,doctor/lint 判讀比沒鍵更糟)。promote 手刪 _ai 段同樣漏這清理。

### arch-f6
severity: minor
引句:「print(f"擋下:圖譜裡找不到節點 {rel_in}", file=sys.stderr)」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:128`
說明:全檔 10 處「找不到節點」都同一模板(含為什麼/下一步 lumos search),dref 五原語改用更短的「找不到節點 {rel_in}」,偏離白話三段式。

## 對齊良好的面
- _dref_parse/norm/same 正規化 tuple+空-did 守衛同 E2 _hits 手法;add-ai 正確重用 _append_decision_ref;_dref_candidates 讀 tidx fwd 結構對;_DREF_E2_FIELDS 對齊 E2 typed_in;巢狀 add_subparsers 同 about-code/guard;dangling rc2+括號理由同 rc 語意。
