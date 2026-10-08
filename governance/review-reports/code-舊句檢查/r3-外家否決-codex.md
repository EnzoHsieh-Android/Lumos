severity: major

## F1 無關的超長行會誤擋推送，兩週帳又把它當成已判完

severity: major  
blocking: 是  
引句:「return bool(handle) or res["state"] in _DRIFT_M1_UNKNOWN or bool(res.get("long_lines"))」  
file: `scripts/lumos:29239`  
file: `scripts/lumos:29322`  
file: `scripts/lumos:29432`  
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:148`

1. `_drift_m1_scan_note` 先看行長、後看候選名稱，因此任何可見區域中的超長行都增加 `long_lines`；即使該行完全不含這次消失的名稱也一樣。
2. `_drift_m1_busy` 隨即把 `long_lines>0` 當成有問題。專案使用 `old_sentence=block` 時，一次本來零命中的推送會回 1，而且帳與終端沒有記是哪篇、哪一行太長，無法針對性處理或表態。
3. 帳仍寫 `state=done`、`handle=0`。兩週流程只把四種錯誤狀態計入「判不了」比例，並讓 `done` 進準度流程；這種實際未完整掃描、未來會硬擋的事件不進任何退場門檻。參考實作重跑若確認長行與候選無關，也只得到零筆，不會量出「正式 block 模式仍會拒絕」這個誤擋。
4. 最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy,types; p="/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/m1impl/scripts/lumos"; m=runpy.run_path(p,run_name="lumos_review"); r=types.SimpleNamespace(res={"long_lines":0,"handle":[],"listed":[]},check_time=lambda:None); L=m["_DRIFT_M1_LINE_MAX"]; m["_drift_m1_scan_note"](r,"Systems/Unrelated.md","# U\n"+"x"*(L+1),m["_drift_m1_name_index"]({"gone_func"}),{"gone_func":{"src/a.py"}},set()); z=m["_drift_m1_new_res"]("done"); z.update(r.res); z.update({"code_files":1,"candidates":1}); print({"long_lines":z["long_lines"],"handle":len(z["handle"]),"listed":len(z["listed"]),"state":z["state"]}); print({"busy":m["_drift_m1_busy"](z,z["handle"]),"進準度":z["state"]=="done","進判不了比例":z["state"] in {"timeout","git-failed","unreadable","error"}})'
```

輸出：

```text
{'long_lines': 1, 'handle': 0, 'listed': 0, 'state': 'done'}
{'busy': True, '進準度': True, '進判不了比例': False}
```

## F2 含分行字元的筆記路徑仍會印出指向錯節點的表態指令

severity: major  
blocking: 是  
引句:「if kind == "m1" and _drift_c4_show_name(path) != path:」  
file: `scripts/lumos:27809`  
file: `scripts/lumos:27855`  
file: `scripts/lumos:28185`  
file: `scripts/test_lumos.py:57260`

1. 新判斷只會攔下 `_drift_c4_show_name` 改寫的 Cf 字元及非 UTF-8 路徑；換行、U+0085、U+2028 等其他分行字元不會觸發「不印可照貼指令」。
2. `_drift_fix_hint` 因而產生含真實換行的命令；稍後 `_drift_print_hints` 又用 `_esc_clean` 把換行改成空白。使用者最後看到的命令指向另一個不存在的節點。
3. 在要處理層且 `old_sentence=block` 時，照貼官方提示無法完成表態，推送仍被擋。新增測試只覆蓋 RLO 與零寬字元，沒有覆蓋這個既有「路徑含控制字元不得印可照貼指令」的鄰接輸入。
4. 最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy,io; p="/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/m1impl/scripts/lumos"; m=runpy.run_path(p,run_name="lumos_review"); path="Systems/a\nb.md"; b=io.StringIO(); m["_drift_print_hints"]([{"kind":"m1","path":path,"line":3,"names":["gone_x"]}],b); out=b.getvalue(); print(repr(out)); print({"actual_node":repr(path[:-3]),"rendered_contains_actual":path[:-3] in out,"suppressed":"不印可照貼" in out})'
```

輸出：

```text
'改法:\n    改成歷史說法(例:「原本叫 <名稱>,已移除」)或刪掉這句;確定照留就 lumos drift ack \'Systems/a b\' 3 --kind m1 --name=gone_x --reason "<為什麼照留>"\n'
{'actual_node': "'Systems/a\\nb'", 'rendered_contains_actual': False, 'suppressed': False}
```

## 圖譜鏡頭逐條判定

- `Systems/lumos-cli-read`：search 的 superseded／stale 過濾路徑未改，未見破壞。
- `Systems/bound-tests-gate`：bound-filter 的新建目錄改為 0700，但合約測試執行、懸空判定及阻擋語意未改，未見破壞。
- `Systems/guard-kill`：回傳碼優先序與 JSON stdout 路徑未改，未見破壞。
- `Systems/授權與歸屬`：白名單、deinit 與 SPDX／MIT 檔頭未改，未見破壞。
- `Systems/測試假綠形態`：本輪測試有前置斷言，但超長行測試只造「長行真的含候選」、路徑測試只造 Cf 字元，未涵蓋以上兩個鄰接輸入；合約本身未直接改壞。
- `Systems/lumos-cli-lifecycle`：re-inject 與 sentinel 外內容保存路徑未改，未見破壞。
- `Systems/design-loop`：設計審處置閘及條款測試進度判定未改，未見破壞。
- `Systems/pitfalls-code-loop`：風險分級與 code-loop 問閘未直接修改；但以上兩項會讓其前面的 drift 推送閘產生不可量出的誤擋及錯誤修法，故本批不應放行。

最高等級:major