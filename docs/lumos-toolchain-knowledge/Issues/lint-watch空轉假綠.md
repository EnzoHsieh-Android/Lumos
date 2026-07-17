---
type: issue
status: done
created: 2026-07-17
updated: 2026-07-17
tags:
  - type/issue
  - status/done
related:
  - "[[Systems/lint-version-watch]]"
summary: |-
  FLAG:TECHNICAL
  KEY:lint-watch 網 2026-07-05 部署後空轉 12 天無人知——兩層病因疊加:①撒網位置錯(runner 只掃源 repo,零依賴 python 無 .lumos/lint-watch.json 宣告檔=恆空;真宣告在消費專案 LandmarkMember 卻無排程掃)②本機 python urllib 憑證鏈壞(CERTIFICATE_VERIFY_FAILED→全 fetch None;curl 走 macOS 鑰匙圈所以人工測通=假象)
  KEY:遮蔽鏈=fail-open 設計(網路失敗永不升 rc)+log 恆 0 bytes+wrapper 只記 rc——三層都「正常」,無一層能暴露「網破了」;同族先例=test runner -k 選中 0 案例假綠(跑了個寂寞必須紅)
  KEY:修法(2026-07-17 收網三修,governance/lint-watch-check.sh):①SSL_CERT_FILE 指 macOS 內建 /etc/ssl/cert.pem(未設定才 export)②多 repo 撒網迴圈(宣告檔存在才掃,seen/pending 按 repo 分檔)③心跳行(candidates/checked/failed 計數逐 repo 落 log,全失敗可見)
  KEY:教訓=監測器自身需要心跳——fail-open 的「永不升 rc」必須配一條可見性通道(計數行/週報),否則「不阻斷」默默變成「不工作」;凡 cron 掛的偵測網,驗收必含「斷網跑一次,確認失敗看得見」
  KEY:首次真收網(2026-07-17)=LandmarkMember 5 條落後:ClosedXML 0.105.0/Dapper 2.1.79/xunit 2.9.3(小)+Swashbuckle 6→10.2.3/SqlClient 6→7.0.2(大版,須審 changelog);pending 暫存等人放行
  DEP:[[Systems/lint-version-watch]]
---
# lint-watch 空轉假綠——網撒錯池塘＋憑證鏈壞,雙層病因疊加 12 天無聲

## 時間線
- 2026-07-05 部署 lint-watch-check.sh 進 daily-governance wrapper(launchd 09:30)。
- 2026-07-05〜07-17:每日 wrapper log 記「lint-watch 段結束 rc=0」;lint-watch.log 恆 0 bytes;`governance/lint-upgrades/` 目錄不存在(暗示腳本體從未產出任何東西)。
- 2026-07-17 使用者說「收網」→ 排查發現雙層病因。

## 病因(兩層,單修任一層都仍空轉)
1. **撒網位置錯**:runner 寫死 `--repo $TOOLCHAIN`,源 repo 無 `.lumos/lint-watch.json`(零依賴 python,本來就沒 linter 好盯)→ lumos lint-watch 回空、dedup 無輸入、LINE 無訊息。真正掛宣告檔的 LandmarkMember 沒有任何排程掃它。
2. **python 憑證鏈壞**:`urllib` 全數 `CERTIFICATE_VERIFY_FAILED`(OpenSSL 找不到本機 CA bundle)→ 就算指對 repo,fetch 也全回 None。curl 走 macOS 鑰匙圈正常,人工 curl 測通=假象。07-04 驗證時真機可跑,期間 python 環境變動所致。

## 遮蔽鏈(為什麼 12 天沒人發現)
fail-open(網路失敗永不升 rc,設計正確)→ rc 恆 0;輸出恆空 → log 恆 0 bytes;wrapper 只記 rc → 每天「成功」。**三層各自正常,疊起來=沒有任何通道能暴露「網破了」。**

## 修法(已落地,lint-watch-check.sh 收網三修)
① `SSL_CERT_FILE=/etc/ssl/cert.pem`(macOS 內建,未設定才 export)② 多 repo 撒網迴圈(宣告檔存在才掃;seen/pending 按 repo basename 分檔防去重互撞)③ 心跳行:每 repo 每日一行 `candidates=N checked=M failed=K` 落 log——全失敗時 failed=6 可見,不再無聲。

## 教訓(可攜)
- **監測器自身需要心跳**:fail-open「永不升 rc」必須配可見性通道,否則「不阻斷」默默退化成「不工作」。
- **cron 偵測網的驗收必含負向測試**:斷網/壞憑證跑一次,確認失敗「看得見」——同 test runner `-k` 選中 0 案例必須紅的假綠家規。
- 部署驗收只驗了「機制會動」(07-04 真機),沒驗「排程環境下持續會動」——排程環境(cron PATH/SSL env)是另一個世界。

## 首次真收網(2026-07-17)
LandmarkMember 5 條落後進 `governance/lint-upgrades/pending-LandmarkMember-2026-07-17.json`,等人放行:小版 ClosedXML 0.105.0/Dapper 2.1.79/xunit 2.9.3;大版 Swashbuckle 6.9.0→10.2.3、SqlClient 6.1.3→7.0.2(須審 changelog 再升)。

## 殘餘待辦
- [ ] Citrus_KDS 掛 `.lumos/lint-watch.json`(有 lint.json/detekt 卻沒掛 watch)並加進 REPOS 清單
- [ ] 其他 python 網路功能(cross-family qwen 調用等)同受憑證鏈影響,cron 路徑需同款 SSL_CERT_FILE 保護——盤點 governance/*.sh
