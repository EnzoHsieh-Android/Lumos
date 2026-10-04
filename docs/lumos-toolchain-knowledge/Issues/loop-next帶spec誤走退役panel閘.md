---
type: issue
status: done
created: 2026-10-04
updated: 2026-10-04
aliases:
  - "panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放"
about_code: []
related:
  - "[[Systems/loop-convergence-recording]]"
  - "[[Projects/probe輪退場_計劃]]"
  - "[[Issues/loop-next吐不可宣告的tier]]"
tags:
  - type/issue
  - status/done
  - scope/loop-engineering
summary: |-
  PITFALL:2026-08-26 以後開的審查編號,`lumos loop next <編號> --spec <凍結 patch>` 一律被「panel 閘僅供舊迴圈回放」擋下 rc2,lumos-code-loop 手冊第 1 步教的正是這個寫法 [出處:2026-10-04 治理帳分流代碼審與 2026-10-04 回頭條件寫下時就成立代碼審兩次撞到,當時都改成不帶 --spec 繞過] [根因:cmd_loop_next 代問閘時寫死問 panel 閘,panel 閘退役後只剩拒判] [修法:新編號(_panel_retired_for 判定,與 panel 閘自己拒判同一支)改問處置閘] [test:t_loop_next_spec_uses_disposal_gate_for_new_loops]
  PITFALL:測試總檔開頭把退役日凍在 9999,整套測試從沒在「新迴圈」語意下跑過 loop next 帶 --spec,所以退役一個多月都沒被抓到 [出處:2026-10-04 寫翻紅測試時發現] [根因:為了讓既有 panel 行為測試不受退役影響而全域覆寫環境變數] [防回歸:新測試自己把退役日拉到過去,新舊兩種語意各驗一次] [同族:[[Systems/測試假綠形態]]]
---
# loop next 帶 --spec 誤走已退役的 panel 閘

## 症狀

`lumos loop next code-xxx --tier high --orchestrator claude --spec governance/review-reports/code-xxx/rN-snapshot.patch` 回 rc2,印:

```
擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放,這個編號是之後才開的新迴圈——
```

lumos-code-loop 手冊〈什麼時候用〉第 1 步就是這樣寫,照做必擋。過去兩次代碼審都改成不帶 `--spec` 繞過,`loop next` 因此只能停在 gate-pending,收斂與否改由人自己跑 `loop status --disposal`。

## 根因

`cmd_loop_next` 帶了 `--spec` 時會「靜默代問一次閘」來判 converged。那段寫死問 panel 閘(`panel=panel_fmt`)。2026-08-25 panel 閘退役後,新編號問它只會拿到拒判 rc2,`loop next` 原樣把 rc2 吐出來。

## 修法(2026-10-04)

新編號(用 `_panel_retired_for` 判,跟 panel 閘自己拒判的是同一支,兩邊對「新舊」不會有不同意見)改問處置閘;處置閘不收 panel 閘的 need/min-seats 參數,分開呼叫。過關時 `gate_basis` 寫處置閘的依據。舊編號照舊走 panel 閘回放。代問時帶 `readonly`:loop next 是唯讀指針,處置閘平常會順手追加的席位異常紀錄(roster-alerts.log)這裡不寫,重跑才不會灌水(代碼審 r1 正確性席)。

## 為什麼一個多月沒被抓到

`scripts/test_lumos.py` 開頭把 `LUMOS_PANEL_RETIRE_CUTOFF` 凍在 9999-12-31,讓既有的 panel 行為測試維持退役前語意。副作用是整套測試裡所有編號都算「舊迴圈」,`loop next --spec` 在新迴圈下的路徑從來沒被跑過。新測試自己把退役日拉到 2000-01-01 驗新迴圈,另用總檔預設驗舊迴圈照舊。

REVISIT:2026-11-01 盤點其他會依 _panel_retired_for 分流的指令路徑(loop status、loop replay、疑似還有 roster 對帳),在「新迴圈」語意下有沒有測試;沒有的各補一條自己把退役日拉到過去的測試,再評估能不能把總檔開頭的 9999 覆寫拿掉。
