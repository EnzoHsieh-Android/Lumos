severity: blocker

## F1 `lumos rule-gap` 印出未消毒的 --desc/--rule,可終端注入(剪貼簿劫持/隱藏文字)
severity: blocker
blocking: yes
引句:「看待辦:lumos rule-gap」

這三輪修正都只把 `_esc_clean` 補進 `loop escape --list`(F2 一節)與 `lumos doctor` 的站名輸出,但逃逸帳同一批欄位(`desc`、`rule`)還有第三個讀者:`cmd_rule_gap`(現行檔 `scripts/lumos:20692-20757`)。它自己重新讀一次 `.escape-log.jsonl`(注解就寫在這份 patch 的上下文行裡:「rule-gap 保留自己找檔再套同一支判斷」,只套了撤回過濾那一支判斷,沒有套 `_esc_clean`),把 `ev.get("rule")` 存成 `rid`、`ev.get("desc","")[:60]` 存成 `v["desc"]`,最後在第 20749 行原樣印出:
`print("  " + rid + "(漏過 " + str(v["n"]) + " 次)—— " + v["desc"])`
——`rid` 與 `desc` 都沒有經過 `_esc_clean`。

攻擊路徑(已實跑重現,非推論):
- 誰:任何能執行 `lumos loop escape <迴圈編號> ...` 的人(門檻極低——迴圈編號只要存在於審查帳,不需要對 repo 有寫入權,不需要通過任何審查關卡)。
- 入口:`lumos loop escape 甲 --stage CI --severity major --desc <payload> --rule <payload> --sha x`(手動記帳指令,S2 佐證檢查照樣通過,因為給了 `--sha`)。
- 送什麼:`--desc` 或 `--rule` 帶 ANSI/C1 控制序列,例如 OSC52 剪貼簿寫入 `\x1b]52;c;<base64>\x07`,或 SGR 隱藏文字 `\x1b[8mHIDDEN\x1b[0m`。
- 拿到什麼:之後任何人(通常是維運者/審查員)在自己終端跑 `lumos rule-gap` 巡「還缺哪條規則」時,這些控制序列原樣輸出到他們的終端——若終端支援 OSC52,攻擊者可以覆寫受害者剪貼簿內容;也可用 SGR/游標控制隱藏或偽造輸出內容,誤導巡帳判斷。

重現(在唯讀 repo 的實驗複製 `exp3-資安/` 下跑,未動正式 repo):
```
python3 - <<'PY'
import subprocess, sys, tempfile, json
from pathlib import Path
d = Path(tempfile.mkdtemp()) / "kg"; d.mkdir()
for sub in ("Systems","Verification","Projects","MOC"):
    (d/sub).mkdir(parents=True)
(d/"MOC"/"idx.md").write_bytes(b"---\ntype: moc\n---\n# idx\n")
(d.parent/".canary-log.jsonl").write_text(json.dumps({"kind":"none","loop":"甲","token":"C1"})+"\n")
payload_desc = "d\x1b]52;c;bWFsaWNpb3Vz\x07"
payload_rule = "R\x1b[8mHIDDEN\x1b[0m"
subprocess.run([sys.executable, "scripts/lumos", "--vault", str(d), "loop", "escape", "甲",
    "--stage", "CI", "--severity", "major", "--desc", payload_desc, "--sha", "x", "--rule", payload_rule])
repo = tempfile.mkdtemp(); Path(repo,"docs").mkdir()
subprocess.run(["cp", str(d.parent/".escape-log.jsonl"), str(Path(repo,"docs",".escape-log.jsonl"))])
subprocess.run(["git","-C",repo,"init","-q"])
r = subprocess.run([sys.executable, "scripts/lumos", "rule-gap", "--repo", repo], capture_output=True)
print(b"\x1b" in r.stdout, repr(r.stdout[-200:]))
PY
```
實跑結果:`True`,stdout 尾段含原樣 `R\x1b[8mHIDDEN\x1b[0m(漏過 1 次)—— d\x1b]52;c;bWFsaWNpb3Vz\x07`——控制序列完整穿透到終端。

建議修法:`cmd_rule_gap` 印 `rid`、`v["desc"]` 前一樣過 `_esc_clean`(跟 `--list`、doctor 站名同一支),而不是只套撤回過濾那一半判斷。

---

已看,無:前兩輪點名的五處已核對、在這份累積 patch 的現行程式碼裡確實生效,`python3 scripts/test_lumos.py -k escape` 128 條全過:
1. **token 清洗**:`--list` 逐列印 token 時已包 `_esc_clean(r.get('token', '?'), 20)`。
2. **路徑字元**:`_plan_for_loop` 開頭即擋——引句:「迴圈編號帶路徑字元不查」(命中 `/`、`\`、`..` 任一子字串即回 `None`),已用帶 `../` 的編號實測不會查到 Projects 外的檔案。
3. **C1 控制碼**:`_esc_clean` 判斷式已從只擋 `\x7f` 改成整段擋——引句:「含 8 位元 C1 控制碼(r2 資安席)」,`\x80`–`\x9f`(含 CSI `\x9b`)都會被換成空白。
4. **doctor 站名**:S14 段按階段彙總那行已包 `_esc_clean(k, 40)`,不會再讓帶控制碼的站名原樣印進健檢輸出。
5. **撤回先擋符號連結**:`_escape_withdraw` 裡 `_escape_log_guard(log)` 呼叫已搬到讀取 `_escape_raw_rows(env)` 之前——引句:「先確認帳檔不是符號連結再讀(r2 外家找洞席)」,帳檔是符號連結時撤回擋下訊息裡不會再出現「沒有 token」這種先讀了帳才會印的字樣(對應 `t_escape_review_r2_fixes` 已驗)。
