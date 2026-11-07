# r1 收貨(2026-11-08)

preflight-4: ran

## 首輪前掃(編排者自己逐句開檔驗,沒另派代理)

①未定義的詞:無。②壞引用:`lumos refcheck` 見下。③範圍自相矛盾:無。④機械宣稱驗語意:
- 「推送前閘在跑測試前 export `LUMOS_PUSH_ATTEMPT`」:`scripts/hooks/pre-push` 第 374 行 export,第 930/934 行才起測試子程序 → 成立。
- 「main 清 `GIT_*` 與關子程序上色兩段」:`scripts/test_lumos.py` main 開頭兩段 → 成立。
- 「`scripts/scenario_probe.py` 開子程序前拿掉 `CLAUDECODE`」:該檔 `env.pop("CLAUDECODE", None)` → 成立。
- 「預設切片的子程序帶 `LUMOS_FANOUT_CHILD`」:測試總檔多處讀寫這個標記 → 成立。
- 「Claude Code 殼裡 `CLAUDECODE=1`」:2026-11-08 本機 `echo` 印 1 → 成立(只驗了 CLI 入口 `CLAUDE_CODE_ENTRYPOINT=cli`)。

## 收貨

四席報告全數存檔、正規化、引句全錨定。全輪 24 條(major 12、minor 12)。id:tc 通才、co 正確性、bp 繞過、ar 架構對齊,加報告裡的 F 序號。

## 先查世界

- PRIOR-ART: 只重跑上次紅的——pytest `--lf, --last-failed` 只跑上次失敗的測試(https://docs.pytest.org/en/stable/how-to/cache.html )。採用:新增 `--lf`,推送前閘提示改印它,解「推送前閘自己教的下一步在對話裡被擋」。
- PRIOR-ART: 關鍵字太泛——本 repo `_keys_suite_select` 已有「單一名字選中超過三成就當全套」的門檻。採用同一個三成,在選完之後對最終清單判。
- PRIOR-ART: 逃生門留理由——本 repo `lint-waive --note`、`code-loop skip --note` 都要理由才放行。採用:逃生門的值就是理由、至少 10 字、原樣印出。
- 插入點、清變數順序、子程序測試環境是本 repo 內部接線,不涉外部做法。

## 逐條去向(全部折入)

| id | 一句 | 去向 | 重現 |
|---|---|---|---|
| tc1 | 插入點落在預設切片之後,無參數全套擋不到 | 折:做 3 明寫在 `_fanout_wanted` 之前 | HIT:`scripts/test_lumos.py` 第 49678 行切片分流在 49680 `_isolate_environment()` 之前 |
| tc2 | 子程序測試沒清環境、暫存目錄數共用的、5 秒易碎 | 折:S4 從頭組環境、私有 TMPDIR、拿掉 5 秒 | HIT:讀碼 `_fan_run` 只剔兩個變數 |
| tc3 | RETIRE-IF/REVISIT 的數字量不到 | 折:做 7 計數檔 | HIT:讀第一版不做 3 |
| tc4 | 訊息印逃生門、漏列 --serial -x --ff --seed | 折:做 4 不印變數名;做 1 列明這些不算條件 | HIT:讀碼 `_fanout_wanted` |
| tc5 | 拿掉 CLAUDECODE 的副作用沒盤點 | 折:做 8 寫進節點 | HIT:grep 只有 scenario_probe 讀它 |
| co1 | 清變數與判斷先後矛盾 | 折:做 3 判斷完才清、不跟 GIT_* 同段 | HIT:讀碼 main 開頭清 GIT_* 在 argparse 前 |
| co2 | 插入點在切片後 | 折:同 tc1 | HIT:同 tc1 |
| co3 | `-k ""` 空字串後門 | 折:做 1 用真值判斷;S1 加列 | HIT:讀碼 `_fanout_wanted` 用 or 判真值 |
| co4 | 推送前閘提示 `--ff -x` 被反擋 | 折:做 5 新增 `--lf`、改提示 | HIT:`scripts/hooks/pre-push` 第 1032、1035 行 |
| co5 | 子程序測試暫存與遞迴 | 折:同 tc2 | HIT:同 tc2 |
| co6 | 逃生門放行那行何時印沒定 | 折:做 6 只在本來會擋時印 | HIT:讀第一版範圍 3 |
| co7 | `-k t_` 子字串繞過 | 折:做 2 選完後三成門檻 | HIT:讀碼關鍵字篩選無上限 |
| co8 | 拿掉 CLAUDECODE 影響面 | 折:同 tc5 | HIT:同 tc5 |
| bp1 | `-k t_` 選中全部照跑 | 折:同 co7 | HIT:同 co7 |
| bp2 | 插入點在切片後 | 折:同 tc1 | HIT:同 tc1 |
| bp3 | 訊息把逃生門寫成現成指令、沒紀錄 | 折:做 4、6、7 | HIT:讀第一版範圍 2 |
| bp4 | 數字量不到 | 折:同 tc3 | HIT:同 tc3 |
| bp5 | 空字串判準 | 折:同 co3 | HIT:同 co3 |
| bp6 | `--suite keys` 多鍵聯集沒上限 | 折:做 2 對最終清單判;`--suite docs` 寫明豁免理由 | HIT:讀碼 `_keys_suite_select` 逐鍵 cap |
| bp7 | 對話裡 push 與其他繞法沒寫進天花板 | 折:天花板 2、3、5,不做 5 | HIT:繞過席實測 `env -u CLAUDECODE` 印空 |
| bp8 | 擋 --shard 與 --ff -x 跟推送前閘提示相衝 | 折:同 co4 | HIT:同 co4 |
| ar1 | 插入點在切片後 | 折:同 tc1 | HIT:同 tc1 |
| ar2 | 逃生門命名 ALLOW 與不留帳跟鄰居不同 | 折:做 6 寫命名理由、做 7 寫不寫治理帳的理由 | HIT:讀碼 `LUMOS_SKIP_REREAD_CHECK` 留 skipped-env |
| ar3 | 訊息首行沒照鄰居寫「擋下:」 | 折:做 4 | HIT:讀碼 main 既有擋下訊息 |

修補因果:首輪,無。
