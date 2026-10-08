severity: major

ID:i1  
severity: major  
blocking: 是  
引句:「五消費專案最終vendor收證模組均與本機來源hash一致」  
file: `docs/lumos-toolchain-knowledge/Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證.md:45`  
合約佐證 file: `docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:17`  
目前五個新建實驗 consumer 的三支 sidecar 均與 HEAD 不同，且都缺少 HEAD 新增的 SPDX 標頭；這些不是決策 d2 豁免追補的舊 11 份副本。因此逐字 hash 聲明不成立，也違反「被複製的每支檔至少帶 SPDX」合約。功能內容的差異僅是 SPDX 兩行，故原生行為證據仍可由目前 CLI 重播，但推送前須同步這五份 consumer 或修正驗證聲明與授權處置。

最小重現：

```sh
repo=/tmp/lumos-readme-oct-audit
lab=/Users/enzo/lumos-test-quality-lab-20261008
for s in node laravel csharp android ios; do
  for f in test_quality.py test_quality_scan.py test_quality_semgrep.py; do
    cmp -s "$lab/$s/scripts/$f" "$repo/scripts/$f" || echo "$s/$f mismatch"
  done
done
diff -u "$lab/node/scripts/test_quality.py" "$repo/scripts/test_quality.py"
```

結果：15 個組合全部印出 `mismatch`；diff 顯示 consumer 缺少 `SPDX-FileCopyrightText` 與 `SPDX-License-Identifier`。

ID:i2  
severity: minor  
blocking: 否  
引句:「把主程式、四支輔助腳本、整個 hooks 目錄複製進消費專案」  
file: `docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:45`  
程式碼 file: `scripts/lumos:22124`  
`_VENDORED_TOOLKIT` 現為主程式加七支輔助腳本；正文的「四支」已被本次新增三支 test-quality sidecar 推翻。摘要合約未寫死數量，實際複製與授權測試正常，因此屬圖譜正文漂移。

掃描零候選、`detected` 與 partial 資格邊界：已讀,無 finding。README、標準、03 手冊、Systems 與 Verification 均明示零候選不代表測試有用、`detected` 不證明業務答案正確、三棧只取得固定案例的部分原生資格。

CLI 與卷證：已讀,無 finding。兩份 manifest 的 142／729 個項目皆存在且 hash 相符；目前 CLI 重播五棧均為 `detected/not_assessed`，零選中與編譯錯控制保持 invalid。相關子集為 22 passed、21 passed；授權與 deinit 合約子集分別 7 passed、4 passed。未跑全套。

總結最嚴重 severity: major；blocking: 1 條。