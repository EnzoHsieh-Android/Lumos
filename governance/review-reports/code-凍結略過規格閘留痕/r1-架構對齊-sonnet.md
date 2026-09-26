severity: minor

## F1 略過 kind=spec-gate 的寫法跟既有三處不一致(區塊註解 vs 行尾註解)
severity: minor
blocking: no
引句:「if isinstance(d, dict) and d.get("loop") == loop_id and d.get("kind") != "spec-gate":」

同一件事——按迴圈編號讀審查帳時要略過規格閘留痕——專案裡已有三處先例,寫法都是「條件式同一行,行尾掛一句註解」:
- scripts/lumos:9090 `if d.get("loop") == loop_id and d.get("kind") != "spec-gate":   # 規格閘留痕不是審查輪(雙向門放行_計劃 S16):不計席、不判無效`
- scripts/lumos:9606 同款(註解相同)
- scripts/lumos:9914 同款(註解相同,只是少了「:不計席、不判無效」那半句)

這次在 `cmd_loop_replay` 的 `_load_rows`(patch 對應 scripts/lumos:608)改成兩行區塊註解放在 if 上一行,且展開成「規格閘留痕不是審查輪(雙向門放行_計劃 S16);處置閘本來就略過,凍結與回放要同一種讀法,不然整個迴圈被判成「有的帶輪次有的不帶」而拒凍(2026-09-26 兩份設計審過閘後凍結被擋)」。內容沒錯,但跟既有三處「行尾一句話」的慣例不同形狀,第四個做同一件事的地方沒有沿用鄰近寫法。不擋,建議收斂成跟 9090/9606/9914 同款的行尾註解,或反過來把那三處也升級成區塊註解說明——但這次至少該跟其中一種對齊,而不是自創第三種。

## F2 新增 isinstance(d, dict) 防呆,三個既有同款守衛都沒有
severity: minor
blocking: no
引句:「if isinstance(d, dict) and d.get("loop") == loop_id and d.get("kind") != "spec-gate":」

同一段邏輯的四個實例裡,只有這次(scripts/lumos:608)多加了 `isinstance(d, dict)` 判斷;9090、9606、9914 三處都是直接 `d.get("loop")`,沒有先檢查 d 是不是 dict(`json.loads` 理論上可能回傳非 dict,例如一行純數字或字串)。這代表要嘛三個舊的地方本來就該補但沒補,要嘛這次多此一舉——兩種情況都是「同一件事四個實例、寫法不一致」,審查材料本身沒交代為什麼這次要多包一層防呆、其他三處不用。不擋,但既然是同一函式家族的姊妹寫法,應該要嘛一起補、要嘛跟這次一樣省略,留言講清楚差異原因。

## F3 測試 fixture 的 vault git init 寫法跟同檔最近例子不同款
severity: minor
blocking: no
引句:「for _c in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],」

新測試 `t_loop_replay_ignores_spec_gate_rows`(scripts/test_lumos.py 新增段落)要用 `--freeze` 就要讓 vault 是 git repo,這件事同檔案裡 `t_loop_replay_freeze_and_golden`(scripts/test_lumos.py:33053 起)已經做過一次,寫法是:
```
for _c in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
           ["git", "config", "user.name", "t"], ["git", "add", "-A"],
           ["git", "commit", "-qm", "init", "--allow-empty"]):
    _sp0.run(["git", "-C", str(v.parent)] + _c[1:] if _c[0] == "git" else _c, capture_output=True)
```
新測試改成:
```
for _c in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
           ["commit", "-qm", "init", "--allow-empty"]):
    _sp.run(["git", "-C", str(v.parent)] + _c, capture_output=True)
```
少了 `git add -A`、也不再有前綴 `"git"` 再切掉那段繞路,結果等價但寫法沒跟緊唯一的既有先例(全檔目前只有這兩處需要「讓 vault 變 git repo 才能 --freeze」)。不擋,是否要回頭統一成同一種寫法留給作者判斷,單獨看這支測試本身沒問題。

已看,無:
- 新增的 PITFALL 摘要行(docs/lumos-toolchain-knowledge/Systems/design-loop.md 新增行)格式跟同節點既有 PITFALL/KEY 行(`PITFALL:[日期 標題]內容...[test:測試名]`)一致,日期、出處、[test:] 收尾都照抄慣例,沒有問題。
- `updated:` 欄位從 2026-09-25 改成 2026-09-26,跟本次改動日期一致,是既有慣例(改筆記當次同步 updated)。
- 新測試的 `check()` 訊息用語(「凍結:...」「回放:...」)、`row`/`sg` 兩筆帳的欄位形狀跟同檔案其他 loop-replay 測試(如 t_loop_replay_freeze_and_golden 裡的 row 結構)一致,沒有另創欄位。
- commit 訊息與其他變更(`docs/.canary-log.jsonl` 等治理帳快照)不在這份 patch 範圍內,未審。
