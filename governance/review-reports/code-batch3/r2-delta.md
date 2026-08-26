# cb3 r2 delta 席報告

材料 sha256 已核對 = 5e0531a0264ca3688a07ae8d41b0480e582ac573e2249dafaee70bc2e6e44017。r2-delta.patch 對應 commit b4b8558;判定針對凍結材料本身。

### d-f1
severity: blocker
引句:「if loop and auditor and outcome is None:」
佐證:file: `scripts/lumos:4020`
說明:寫側觸發放寬留了對稱新逃生口——凍結材料裡沒有任何檢查禁止把 --outcome 跟審查欄位混在同一筆 record;多帶 --outcome converged,outcome is None 為假整段跳過,報告與嚴重度底線全失效。對 b4b8558 版本活體重現:兩筆 caught --loop LEGACY-EXPLOIT --auditor t1/t2 --severity clean --findings 0 --outcome converged(全程無 --report,severity 憑空宣稱),loop status --gate 直接印 GATE PASS。正是 r1 s1-f1/ext-f1 要關的攻擊面;省略 --round 堵死了,掛 --outcome 這條等價路沒堵。工作目錄已有未 commit 的互斥修法在補,但不在凍結材料裡。

### d-f2
severity: major
引句:「_os_rp.replace(_tmp, target)」
佐證:file: `scripts/lumos:588`
說明:重凍改成暫存→歸檔→replace→留痕,但最後 _os_rp.replace 沒包 try/except(反而原本 target.write_text 有包)。monkeypatch os.replace 丟 OSError,重跑 freeze,UNCAUGHT OSError 直接炸出而非「擋下:」乾淨訊息。不會謊報成功(gov_mark 在後),但舊 golden 已搬走、新內容沒換上位,此 loop 暫時沒有任何 verdict.json,使用者見 traceback 而非一貫錯誤風格。

### d-f3
severity: clean
引句:「if loop and findings_set is not None and not (round_id and auditor):」
佐證:file: `scripts/lumos:4022`
說明:寫側觸發放寬後 legacy/light 仍記得帳,只是行為變了(設計預期)。t_canary_severity_writeside 13 斷言全過;autonomous-loop.sh 唯二 record 呼叫都帶 --outcome 落豁免分支。問題不是記不了,是 d-f1 的豁免口開太寬。

### d-f4
severity: clean
引句:「if str(rid).startswith("__") and any("findings_set" in r for r in latest):」
佐證:file: `scripts/lumos:10558`
說明:讀側配套 fail-closed 正確;round-less 各自成 __seqN 組,latest 恆單筆;混用被更早守衛攔。t_disposal_severity_tail 6 斷言全過,含新增拒判釘。兩層防線無互打。

### d-f5
severity: clean
引句:「if str(rid).startswith("__"):」
佐證:file: `scripts/lumos:513`
說明:s2-f1 崩潰在算出判定輪後、查 spec_sha_frozen 前擋掉 round-less rid,乾淨訊息,崩潰點之前攔截。

### d-f6
severity: clean
引句:「_engine_stale = g.get("engine_rev") != _REPLAY_ENGINE_REV」
佐證:file: `scripts/lumos:616`
說明:過期拆布林旗標只跳重算,帳集合比對與卷證完整性照跑。t_loop_replay_freeze_and_golden 18 斷言全過,含 ⑨b「過期+帳被竄改=紅」。

### d-f7
severity: clean
引句:「print(f"擋下:歸檔失敗({e})——多半是同秒有另一個重凍在跑,等一下再試", file=sys.stderr)」
佐證:file: `scripts/lumos:583`
說明:s2-f4 的 rename race 包了 try/except;但稍後 replace(d-f2)在「target 還不存在、兩邊都第一次凍結」的相鄰情境沒等價保護,該 TOCTOU 改版前後都存在,非本輪新引入,提出給人知道範圍邊界。

### d-f8
severity: clean
引句:「if Path(rp).is_absolute():」
佐證:file: `scripts/lumos:535`
說明:s2-f5 絕對路徑在呼叫 _replay_git_blob 前先攔,正確理由;無專門新釘(走既有②③步驟),邏輯本身對。

### d-f9
severity: clean
引句:「f" --report <席報告.md>"」
佐證:file: `scripts/lumos:5665`
說明:s3-f1 模板補 --report,新增「record_cmd 真跑」釘測;t_loop_next 組 27 斷言全過,legacy 分支模板同步驗。

### d-f10
severity: clean
引句:「check("sevtail:round-less 處置帳讀側拒判 rc2(繞道關死)",」
佐證:file: `scripts/test_lumos.py:23279`
說明:s3-f2 假綠改成真被走到的分支(純 round-less 帶 findings_set 驗 fail-closed),移除 d-f4 檢查會翻紅,有鑑別力。

### d-f11
severity: clean
引句:「rpt_old = repo / "governance" / "review-reports" / "sevtail" / "r1-s0.md"」
佐證:file: `scripts/test_lumos.py:23255`
說明:s3-f3 加生效日前舊帳低報列,驗標「歷史帳」非「寫側 bug」,兩分流各有斷言。

### d-f12
severity: clean
引句:「cb3 s3-f4:刻意低報形(報告 blocker/帳 minor)——readonly 守衛若被拔,severity 尾巴會寫」
佐證:file: `scripts/test_lumos.py:23310`
說明:s3-f4 fixture 改 blocker 製造真低報,驗 readonly 仍不產檔;尾巴兩函式都在 if not readonly 下,實跑全過。

### d-f13
severity: minor
引句:「cb3 s3-f5:commit 過之後又被改(工作樹≠HEAD)→ 同樣拒凍(blob 錨定第二層)」
佐證:file: `scripts/lumos:447`
說明:s3-f4 本體是「測試覆蓋洞」非「程式邏輯洞」,447 行檢查早就在;折法補測試而非改邏輯是對的,列 minor 提醒折入敘述「兩層都拒凍」易誤讀為改過邏輯。

### d-f14
severity: clean
引句:「cb3 s3-f6:輸出含紅字樣但 rc=0 → 不判紅(and rc!=0 條件的負案例;」
佐證:file: `scripts/test_autonomous_loop.py:1275`
說明:s3-f6 新增 test_red_marker_with_rc0_not_red 負案例,實跑全過。

### d-f15
severity: clean
引句:「if d.get("kind") == "converged" and _nodes and _nodes[0] not in seen:」
佐證:file: `governance/autonomous_loop/replay_weekly.py:45`
說明:finder-f1 schema 改讀 kind/nodes[0]+isinstance 擋非物件;fixture 同步改真 schema+塞 null 行驗不炸。106 案例 OK。

### d-f16
severity: clean
引句:「return head + ";" + ";".join(parts)」
佐證:file: `governance/autonomous_loop/replay_weekly.py:178`
說明:s4-f2 改單行分號串接,新增 test_msg_single_line;各欄位塞的是 loop id 或固定文字不自帶換行。

### d-f17
severity: clean
引句:「cur["seen"] = sorted(set(cur.get("seen", [])) | {l for l in new if l in set(out["replayed"])} | set(sample))」
佐證:file: `governance/autonomous_loop/replay_weekly.py:147`
說明:s4-f3 只把真回放過的新包標 seen,新增 test_skipped_new_keeps_must_run_status 假鐘驗。

### d-f18
severity: clean
引句:「_os.replace(_tmp, cur_p)   # cb3 s4-f4:比照 backlog.py 暫存+原子換檔,半寫殘檔不歸零進度」
佐證:file: `governance/autonomous_loop/replay_weekly.py:155`
說明:s4-f4 游標原子換檔;此處 replace 在外層 try/except OSError 下,失敗走 errors 不裸奔,無 d-f2 問題。

### d-f19
severity: minor
引句:「print(f"擋下:loop 編號含路徑字元({loop_id!r})——golden 目錄以編號命名,不受理(目錄安全+週跑掃描只看一層)", file=sys.stderr)」
佐證:file: `scripts/lumos:490`
說明:extf-f2 斜線守衛正確,真帳零筆含斜線不誤傷;但無配對釘測,行為驗證只能手動重現,與本 delta 其他條的嚴謹標準不一致。

### d-f20
severity: clean
引句:「log "回放週跑:模組失敗無輸出,本週不蓋章明天重試(錯誤在 replay-$TODAY.err)"」
佐證:file: `governance/autonomous-loop.sh:252`
說明:extf-f4 蓋章前查 $out 有無 { 開頭,無則不蓋章;run_weekly 正常路徑不提前 print,判準不誤判。

### d-f21
severity: clean
引句:「red.append(f"golden 本體與版控不符({_gerr})——凍結檔的竄改偵測以版控為錨,先查 git diff -- {_grel}")」
佐證:file: `scripts/lumos:609`
說明:extv-f2/extf-f3 回放先對 golden 檔算 git blob,已提交但工作樹≠HEAD 列紅;⑧b/⑨b 兩組合都覆蓋。

## 掃過但乾淨的面
arch 三條 r1 判「刻意非疏漏」r2 未改行為本體只補註解;_report_severities/路徑解析/_SEV_ORDER 等 r1-s1 乾淨面未動;_hash_chain_check override/T6/M2 未波及(42 斷言過);T1 六欄斷言改法正確;週跑排程既有守衛未波及(106 案例 OK)。
