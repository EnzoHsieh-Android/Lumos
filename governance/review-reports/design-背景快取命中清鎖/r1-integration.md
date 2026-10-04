severity: major

severity: major
blocking: yes
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:13`
引句:「lands_in:  - Systems/lumos-cli-write」
finding: 圖譜落點指錯且不完整。`lumos-cli-write` 的責任是圖譜 frontmatter 寫入原語；本案改的是派工鏡頭背景暖機、快取與清鎖。現有同機制分別記在 `hook逾時預算` 與 `codex-harness`，照凍結設計實作會讓行為與驗證只回寫到不負責該行為的節點，漏掉真正的系統合約。
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:90`
file: `docs/lumos-toolchain-knowledge/Systems/hook逾時預算.md:50`
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:56`
最小重現: `grep -qx '  - Systems/codex-harness' docs/lumos-toolchain-knowledge/Projects/背景快取命中清鎖_計劃.md; echo $?` 輸出 `1`；`grep -qx '  - Systems/hook逾時預算' ...; echo $?` 亦輸出 `1`。把實際承接節點加入 `lands_in`，並讓後續 Verification 雙向連回它們即可翻綠。

severity: minor
blocking: no
file: `governance/review-reports/design-背景快取命中清鎖/r1-snapshot.md:26`
引句:「測試先在舊碼驗 rc 0 且鎖仍在，再驗修後鎖消失」
finding: 原 Issue 的修好條件另要求驗「快取 TTL 後可重新暖機」，S1–S4 只驗清鎖、保留他鎖、正常算完及 impact 錯誤，沒有把 TTL 過期後再次派暖機列成斷言；目前可由 S1 與 S3 推論，但沒有端到端驗收釘住。
file: `docs/lumos-toolchain-knowledge/Issues/背景快取命中留下暖機鎖.md:37`

父案未通過狀態：已讀,無 finding

本次清鎖與 F2 另案銜接：已讀,無 finding

現有 CLI／安裝流程契合：已讀,無 finding

總結：最嚴重 severity major，blocking 1 條。
