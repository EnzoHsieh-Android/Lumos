---
type: system
status: doing
created: 2026-08-09
updated: 2026-08-09
aliases: []
pitfall_ask: 多分頁/多請求並發 refresh:token 一次性輪換?前端 single-flight(僅一個 refresh 在飛、其餘等待共用結果)?refresh 中的 API 請求排隊或放行+失敗回滾至登入?
pitfall_source: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
tags:
  - type/system
  - status/doing
summary: |-
  FLOW:
  KEY:
  DEP:
  TEST:
pitfall_when:
  - content:refresh.?token|refreshToken|token.?rotat
verified_by:
  - "[[Verification/2026-08-09_已知坑策展庫v2落地]]"
---
# known-pitfall-refresh-token

**類型=known-pitfall(世界已知坑,非本專案事故)**。pitfall_ask 由 pitfalls spec 模式在 spec 文本命中 content-trigger 時 advisory 攤出(design-time);答或寫「已排除:理由」,panel 審(裁定留痕)。

## 坑
refresh token 並發:多分頁/多請求同時發現 access token 過期→同時拿同一 refresh token 換新。若 refresh token 一次性輪換(rotation,安全最佳實務),第一個換成功作廢舊 token,後發請求拿已作廢 token→被拒→誤登出。

## 解
- 前端 single-flight:偵測到需 refresh 時僅發一個 refresh 請求,其餘等待共用其結果。
- refresh 進行中的 API 請求排隊等新 token;refresh 失敗→整批失敗+導向登入(明文回滾)。
- 後端容忍舊 token 短窗重複兌換(grace period)或前端保證不重複兌換,二選一。
