---
type: system
status: doing
created: 2026-08-22
updated: 2026-08-22
self_audit: sonnet/2026-08-30
aliases:
  - 圖譜同步點名
  - sync nudge
  - 同步覆蓋
tags:
  - type/system
  - status/doing
summary: |-
  FLOW:改 code→(Stop hook 當輪點名)→git commit(pre-commit Gate 3 過關前點名)→git push(pre-push 整批點名)
  KEY:「動過圖譜」不等於「動對篇」——三個位置都用 lumos impact --sync-check 算「跟改到的 code 直接相關(固定席:合約/事故/直接相依)、這次卻沒動」的筆記,點名前 8 篇;Claude 側只提醒不擋、★Codex 側(2026-09-05)改了碼沒寫回時回 block 一次讓模型續做補筆記(stop_hook_active+session 標記雙護欄;見 [[Projects/Codex行為精修_計劃]])★,逃生門仍是 --no-verify(有繞過帳)
  KEY:刻意不硬擋:單體大檔(scripts/lumos)一次牽 30+ 篇,硬擋會把人訓練成反射 --no-verify
  DEP:[[Systems/lumos-cli-read]]
  TEST:t_precommit_sync_nudge_names_missing_pinned_nodes(動錯篇點名/動對篇不點名)
verified_by:
  - "[[Verification/2026-09-05_Codex行為精修f02後測]]"
---
# graph-sync-coverage

# graph-sync-coverage

> 白話:以前「改 code 沒動圖譜」的閘只看「有沒有任何一篇圖譜檔一起 commit」,隨便動一篇就過,真正該改的那篇沒改它看不出來——這就是 Enzo 說的「偶有沒能同步完全」。現在不加新機制,把原本只供人看的 `lumos impact --sync-check` 接到三個時機點名。

## 三個時機
| 時機 | 在哪 | 印什麼 |
|---|---|---|
| Claude / Codex 改完 code、這輪結束 | `scripts/hooks/claude/check-graph-sync.py`(Stop hook;Codex 註冊時帶 `--harness codex`,同條件擋一次) | 即使這輪動過圖譜,仍點名「直接相關且帶合約/事故、這輪沒動」的篇(★2026-08-30 自足審計訂正:現況=單次 `impact --diff HEAD --sync-check --json`(工作樹 vs HEAD)取固定席前 8 篇——原「每檔 impact --file、最多 4 檔」是重構前舊貌,src_files 參數已是殘跡★) |
| `git commit` | `scripts/hooks/pre-commit` Gate 3 | `impact --diff staged --sync-check`,固定席優先、自由席補滿到 8 篇(pre-commit/pre-push 實際帶的旗標是 `--sync-only`,蘊含 sync-check 且只印點名) |
| `git push` | `scripts/hooks/pre-push` | 同上對整批 range——分開幾個 commit 各自過關、整批漏掉的在這裡浮出 |

## 為什麼不硬擋
本 repo 改 `scripts/lumos` 一次,固定席就 30+ 篇。硬擋等於每次都擋,人會養成 `--no-verify` 反射,比現在更糟。提醒要具體到篇名才有用——之前的提醒只說「筆記沒動」,現在說「這篇、這篇」。

## 怎麼用
`lumos impact --diff staged --sync-check`(commit 前自己先看)、`lumos impact --diff <range> --sync-check`(推前)。
