severity: major

PF-1  
severity: major  
blocking: 是  
引句:「只捕捉特定解碼例外，不吞Exception、不另讀快照或新增背景工作。」  
佐證file: docs/lumos-toolchain-knowledge/Projects/載體快照非法編碼受控拒收_計劃.md:47  
佐證file: scripts/test_lumos.py:25819  

觀察：新測試只注入三種 `UnicodeDecodeError`，驗證 rc2、診斷、無 traceback 與帳不變；沒有注入其他例外，也沒有控制能辨別「只接 `UnicodeDecodeError`」與「以 `except Exception` 統一回 rc2」。因此實作者若廣泛捕捉 `Exception`，目前 S1/S2/S3 與 34 條控制仍可能全綠。這是依測試內容得出的靜態推論；本次未做變異實跑。

判準：原始契約明定不得吞 `Exception`，且計劃也重申此限制。實作前應補一個能殺死廣泛捕捉的控制，例如在同一解碼階段注入非編碼例外，證明它不會被改報成 `--snapshot` 編碼 rc2；否則「特定例外」只有散文約束，尚不是真控制。

其餘核對結果：回退範圍、OSError 分流、載體／非載體邊界、有效 UTF-8 與 raw-bytes 指紋、換檔及負數守衛均有對應控制；初版 34＝20 pass／14 fail 與兩份入口探針已分來源、分階段陳述，沒有把 S2 整支紅誤稱為合法路徑退化；`dispatch-lens --spec` 收據確為 linked/shown 2，計劃沒有宣稱其他節點自動附上。

已讀材料：使用者 AGENTS v1.0、repo CLAUDE、完整計劃、新測試、`cmd_canary` 載體 snapshot 分支、red-source-bind/red.json/red.log、main/candidate counter、preflight-four-checks、spec-gate-red、existing-reader、前案零引句計劃、UnicodeDecodeError Issue、Systems/design-loop 合約。最高級：major。