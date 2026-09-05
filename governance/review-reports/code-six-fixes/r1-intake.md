# code-six-fixes r1 intake(2026-09-05,standard:通才-sonnet / 架構對齊-sonnet / 外家finder-codex)
收貨:通才 12 行 severity 全錨;架構 6 條全錨;外家 9 行 1 句錨不到(#6 引自探針檔非 diff,同題架構 F 已有)。manifest 0 條。carrier=通才(全錨、涵蓋最廣)。
## 外家 6(3 major 3 minor):M1 單次 impact 不受 30 秒預算 HIT → 子行程帶剩餘秒數 timeout;M2 delguard 部分結果記 ok HIT → 掃後判 deadline,部分=degraded(reason=timeout-partial);M3 spec 路徑/程式檔不限 repo 內 HIT → resolve 後 relative_to(root);m1 docs/methodology 正規式死碼 HIT 刪;m2 連結節點若也被命中會掉到後面 HIT → 連結永遠最前(kind 合併);m3 codex runner 忽略 max_turns HIT → docstring/--help 寫明。
## 架構 6(2 major 4 minor):A 回放 log 在 shell 端組(違本檔慣例)HIT → replay_weekly 印 LOG: 行、shell 只抽前綴,+單元測試;D 渲染迴圈複製一份且漏截斷提示 HIT → 抽 _lens_render_listed 共用;B --spec 不在互斥清單 HIT → 加入;C Codex 分支超時仍靜默 HIT → 同語意附 additionalContext;E ok 記帳沒走具名 helper HIT → _delguard_log_result;F ⚠ max_turns 只 Claude 側 → 文件化(同外家 m3)。
## 通才 9(6 major 3 minor):#1 spec 超時句給錯指令 HIT → cmd 依模式;#2/#3 路徑越界 HIT(同外家 M3);#4 有檔但 0 席 text 空 HIT → 一行說明;#5 partial 記 ok HIT(同外家 M2);#6 ok 每 commit 一筆淹掉 gov 視圖 HIT → 呈現層折疊納入 kind=ok;minor docs/methodology 死碼(同)、set -- 切割(架構 A 已改掉整段)、max_turns 文件(同)。
辯方:全部有翻紅重現或多席同題,未開庭。輪內有 major → accepted 空。intake 到此為止。
