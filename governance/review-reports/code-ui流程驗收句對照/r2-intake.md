# r2 收貨與待驗案例(2026-11-01)

修正關卡:`lumos loop fix-check code-ui流程驗收句對照 --round r1` ✓ 全部通過(130.6s),修正前 74d6c9df → 修正後 595b910d;第一次跑因 G1、G3 的 other 類缺 note 被擋,補 note 後重跑通過。殺傷力配方 `guard kill Systems/canary-audit --id 259cf76bb8ae` 照樣 killed。

## 待驗案例(repair=原問題、preserve=要維持的既有行為)

| 組 | 角色 | 行為 | 來源 | 測試 |
|---|---|---|---|---|
| G1(s1) | repair | 預覽列出零檢查流程與沒對到的句子;本機總表那筆有 checks 數 | 計劃做法 4 | t_android_e2e_checks_preview_and_history |
| G1(s1) | preserve | judge 的過與不過不因檢查數改判 | 計劃做法 4 | t_android_e2e_checks_recorded |
| G2(s2) | repair | 情境寫了 accept 卻沒有 flows,--check-config 回 2 | r1 單審 s2 | t_android_e2e_accept_config_strict |
| G2(s2) | preserve | 三個新鍵都不寫的舊設定照舊回 0;只列 visual 的情境不寫 accept 照舊合格 | 計劃 S13 | t_android_e2e_accept_config_strict |
| G3(a1) | repair | e2e 名單改用 _secinv_names,長路徑整段印出 | r1 架構對齊 a1 | t_android_e2e_checks_preview_and_history |
| G3(a1) | preserve | _secinv_names 其他 7 處呼叫照舊每項截 40 字 | 安全證據閘既有行為 | t_android_e2e_checks_preview_and_history、-k security |

修補與重構(_e2e_cap 改用 _secinv_names)在同一提交,沒有拆開驗(見 binding 的 attribution_limits)。

## 收貨(兩席到齊後)

- 單審席 severity clean,沒有 finding(也就沒有引句);報告附了三問與已驗主張的兩版證據表。它在 /tmp/lumos-seat-work 底下另開的兩個臨時工作樹已自行刪除,`git worktree list` 與 `git reflog` 核對 repo 沒被動到。
- 架構對齊席 1 條 minor(a1:e2e 直呼以安全證據閘命名的 `_secinv_names`,讀的人會以為是安全登記專用)。放行:跨子系統共用小工具有先例(e2e 本來就呼叫規格閘的 `_door_keyword_hits`),拿掉重複的 `_e2e_cap` 正是 r1 架構對齊席要的;改名會動到安全證據閘 7 處呼叫者,範圍大於這次修補。
- 歸因:a1 是本輪修補(改用 `_secinv_names`)直接帶出的命名問題,屬「有證據的修復回歸」(minor);`--regression-set` 只收 code- 開頭的編號,本輪 finding 編號不是那種形式,記在這裡不填該欄。
