severity: minor

severity: minor

F1 lands_in 指錯既有邊界，漏掉實際機制的家
severity: minor
blocking: 否
引句:「lands_in:
  - Systems/lumos-cli-write
  - Systems/codex-harness
  - Systems/測試假綠形態」
file: `governance/review-reports/design-背景啟動失敗即時回報/r1-snapshot.md:14`
file: `docs/lumos-toolchain-knowledge/Systems/hook逾時預算.md:74`
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:91`
重現/因果: `Systems/hook逾時預算` 明定 `lumos dispatch-lens --deadline` 的背景程序、等待與錯誤轉述屬於該節點；`lumos-cli-write` 自述只管圖譜 frontmatter 寫入原語。照目前 lands_in 寫回會漏記這次新增的 Popen 失敗分流，卻污染圖譜寫入節點。應把 `Systems/lumos-cli-write` 換成 `Systems/hook逾時預算`。

已讀,無 finding：模組邊界、錯誤分類、第二套鎖／監督機制、測試現場前提。設計沿用 `_lens_spawn_warmer`、`_lens_wait_or_warm`、既有 JSON 分類與薄殼 hook，沒有新增 lease、flock、監督程序或握手。

總結：最嚴重 low；blocking 0 條。
