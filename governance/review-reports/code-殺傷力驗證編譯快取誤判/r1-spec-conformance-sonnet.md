severity: clean

# 實作是否照計劃條款(spec-conformance-sonnet,第 1 輪)

方法:在 `--shared` clone(5fc409a5)實跑條款測試 `-k guard_kill_no_`(3 綠)與 `-k guard_kill_mtime`(3 綠),並逐條拿計劃〈範圍〉〈做法〉S1-S4 對照凍結 patch。沒有 finding。

## 〈做法〉逐條核對
- 狀態:每平台組一份 `{"w":0,"r":0}`、每個不同指令的 baseline 後都更新 r。
  引句:「mstate["r"] = int(time.time())   # 每個測試指令的 baseline 都記(夾在配方之間)」
  佐證行:file: `scripts/lumos`(`cmd_guard_kill` 內 `baselines[cmd]` 賦值之前)。符合;baseline 被指令快取時不重跑故不更新,與「每次 `_kill_run` 跑完」一致。
- 等:睡 0.05 秒、上限 3 秒、時鐘往回撥不空轉。
  引句:「while int(time.time()) <= max(state["w"], state["r"]) and time.time() < deadline:」
  符合。
- 寫後確認:讀回、`int(mt) > floor` 記 w 回 True;否則等 1 秒、`os.utime(path)`(不帶時間)、最多 3 次補碰,共 4 次讀,失敗回 False;比的對象是 max(w, r),跟「等」一致。
  引句:「if mt > floor:」
  符合。
- 插的位置:套壞法(原文恰一次之後、寫檔前等;寫完確認)、跑完更新 r、還原前等、`git checkout` 成功後確認;revert 失敗 break、drifted/逃逸分支在等待之前就離開。
  引句:「# 還原前也要等:測試跑得快時,還原寫回的檔可能跟壞法同一秒、同大小」
  符合。
- 弱證據:旁路欄、stderr 整次一次(`mt_warned`)、收尾重算 weak 納入、`--json` 濾掉。
  引句:「res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty or res.get("_mtime_unsure"))」
  引句:「if k not in ("_logged", "_rid", "_mtime_unsure")」
  符合,且 kill-log 欄位未新增(不改 `--json`/log 欄位)。

## 條款
- S1(兩條同檔同大小、傷害後無害 → killed, survived;同大小傷害 → killed;清 PYTHONDONTWRITEBYTECODE):
  引句:「e.pop("PYTHONDONTWRITEBYTECODE", None)」
  實跑 `t_guard_kill_no_stale_build_cache` ①② 綠。符合。
- S2(a、b 兩支,run_cmd 寫紀錄檔驗秒數,含還原那一半):
  引句:「int(rows[2][1]) > int(rows[1][3]) and int(rows[2][2]) > int(rows[1][3])」
  ③ 綠,驗 a(還原寫回)與 b 的 mtime 秒皆晚於上一次測試結束秒。符合。
- S3(測試斷言 mtime 不晚於現在、無害壞法 survived):
  引句:「assert os.stat('prod.py').st_mtime <= time.time() + 0.5」
  實跑綠;實作碼全文無 `os.utime(path, (` 設未來時間(只有不帶時間的 `os.utime(path)`)。符合。變異驗證(改設未來時間翻紅)見計劃〈實作紀錄〉,本席未重跑。
- S4(替身一律失敗:stderr 一行、weak true、`--json` 無旁路欄、kill-log weak true;測試用帶 {method} 的指令):
  引句:「m._kill_after_write = lambda path, state: False」
  三項檢查皆綠。符合。

## 〈範圍〉沒做多
- 「不做」四項逐一確認:`_kill_run` 本體與其他呼叫點未動、無設未來 mtime、判法/回傳碼/`--json` 既有欄位未改(只多濾一個旁路欄)、未清使用者快取。
- 範圍外的非程式檔:Systems/guard-kill.md 加一行 CLI 說明(計劃〈要同步的文件〉點名)、Issue 轉 done 並補修法選定(計劃點名)、計劃檔本身、審查卷證與 canary-log(流程產物)。
- 小差異(不構成 finding):計劃寫「把 11-01 那行 REVISIT 改成指向本計劃」,實作是直接刪掉該 REVISIT 並在內文補指向本計劃的連結、Issue 轉 done;意圖一致(已修完不需再回頭)。

最高等級:clean
