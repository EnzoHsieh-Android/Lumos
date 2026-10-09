severity: clean
blocking: 否
引句:「明示可信本機命令，非沙盒；外部服務隔離由呼叫者負責。」
file: `scripts/test_quality.py:148`

已讀,無 finding。

裁定: disagree；major 秘密外洩不成立。

HIT：可重現 `capture` 原樣保存呼叫者傳入的假值。實驗中 `receipt.json` 保存 `DEMO_API_KEY=sk-demo-not-real`，stdout 與 report 也保存 `sk-demo-not-real`。file: `/tmp/lumos-seat-work/code-test-quality-native-push/defender/repro/capture/receipt.json:8`、file: `/tmp/lumos-seat-work/code-test-quality-native-push/defender/repro/capture/stdout.txt:1`

判準：此 HIT 證明原始收證沒有遮罩，不證明未授權秘密外洩。CLI 契約要求「可信本機命令」及保存原始 runner 報告、來源快照；程式只建立本機新目錄並寫入快照、stdout、stderr、report、receipt，沒有 git add、push 或上傳路徑。file: `scripts/test_quality.py:102`、file: `scripts/test_quality.py:144`、file: `scripts/test_quality.py:151`、file: `scripts/test_quality.py:166`、file: `scripts/test_quality.py:183`。圖譜同樣明訂「保存真正runner原始報告」及「只使用隔離資料庫和可信小型來源」。file: `docs/lumos-toolchain-knowledge/Projects/測試品質工具接線_計劃.md:28`、file: `docs/lumos-toolchain-knowledge/Projects/測試品質工具接線_計劃.md:30`

攻擊者入口：在該重現中，攻擊者只能控制交給 CLI 的 argv／stdout，且假 token 本來就是攻擊者已知資料。要讓公開讀者取得真正秘密，還需維護者：

1. 執行含真正秘密或會讀取秘密的命令；若命令由攻擊者控制，已違反 trusted-command 契約，而且該命令在無沙盒下本來就有任意本機及網路能力。
2. 明示把秘密放入命令、runner 輸出或 `--context` 檔。
3. 另行 stage、commit、push 收證目錄。

Python R16「秘密不進 log、不進錯誤訊息、不進 repo」仍適用，但責任點是秘密注入與發布邊界；假值命中關鍵詞不能證成可直接利用漏洞。file: `/Users/enzo/.agents/skills/python-idioms/SKILL.md:194`

concern：若要加強操作提醒，可明說公開前須確認卷證不含秘密；這是防誤用建議，不支持 major。單一 finite 遮罩無法完整解決：秘密可為任意格式、編碼或分段，規則也會誤擋 `DEMO_API_KEY` 這類假 fixture；遮罩來源快照或原始 JUnit 還會破壞本次「原始報告＋hash＋不可覆寫快照」的證據契約。若要保證處理不可信命令，需要另設沙盒、環境清洗及發布閘，已超出本次可信本機收證 scope。

本次既有 generated 卷證的高信心金鑰形狀掃描為 0 命中；未發現現存真 secret。

總結最嚴重 severity: clean；blocking: 0
