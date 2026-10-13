# r1 收貨紀錄(一般分級:單審+架構對齊,同門 sonnet;外家未派)

兩席引句全數錨定,載體選單審。

## 機械重現表

| finding | 重現命令/查證 | 結果 |
|---|---|---|
| U1 | 讀 `scripts/lumos` `cmd_loop_next`:`width` 傳進 `cmd_loop_status(..., min_seats=width)`;改成 `gate_width` 後 `t_loop_next_width_matches_roster` 的 code-w4 釘「印 1 人、閘最少 3 人」,把閘改回跟名冊走該條翻紅 | HIT |
| U2 | 新測試原本只直呼新函式;補呼叫端早退、無共同祖先、fork 遠端三案,並在 scratchpad 把候選改回掃全部遠端,三條斷言翻紅 | HIT |
| U3 | 掃全部 `refs/remotes` 時過期 fork 含 HEAD 會讓 `merge-base == HEAD` 早退;同上變異實測 | HIT |
| A1 | `_codeloop_default_base` 自列候選,與 `_mainline_ref`、`_push_mainlines` 皆不同;改為呼叫 `_push_mainlines` 只加本機 main/master | HIT |
| A2 | 筆記寫「不再另查 _TIER_PARAMS」與程式 `or width` 退路不符;名冊呼叫兩次 | HIT |
| A3 | 手冊段落講「第一次凍結材料之前」卻放在第 5 步 | HIT(⚠ 位置判斷,搬到第 1 步) |

## 處置

- 折入 6 條(全部)。放行:無。refuted:無。
