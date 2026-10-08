# code-ci-wait短sha r2 收貨

席報告 2 份(正確性r2 1 條 minor、架構對齊r2 1 條 minor)。

彙整 id:正確性r2 d1、架構對齊r2 b1。

## 處置

- 放行 d1(完整 40 碼尾端帶換行也被當成完整):`$` 錨定讓尾端換行照放行,結果跟修正前一樣查不到、判 no-run,不會誤判綠;--sha 是人打的參數,命令列不會自帶換行。
- 放行 b1(取 HEAD 走 ci-wait 原本的 git_out、換短碼走 _lens_full_sha):取 HEAD 那段是原本的程式整段搬進來,保留「取不到 HEAD 判 unavailable」的既有行為,不在這次改。
