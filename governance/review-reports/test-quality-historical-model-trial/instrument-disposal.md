# 原始與修訂評分器分開

四場生成都在原始 runner 下完成；只讀 implementation.txt，無 verifier 或執行工具，全部模型輸出於修訂前凍結。原始分數全 invalid，不作模型品質失敗：normal fixture 未建立完整可信快取，兩場模型正常前置斷言因此在修復版也紅；其餘兩場含標準 if __name__ == "__main__": unittest.main() 尾段，超出考卷語法，不能說測試品質差。

修訂只補 normal fixture 的 .cache/lumos/vault-lock 私有目錄，及接受單一精確、在 generated_tests 名稱下不執行的標準尾段；不接受任意 if 或其他新API，生成 code 未改。八項控制全過，額外 normal 控制原 invalid 的結果保留在 controls-final。對四場全部一致重算，不重抽模型，不提供回饋。原分數保存在 results.json；修訂結果在 rescored-results.json；生成 runner 快照 runner-before-normal-fixture.py.txt，其 SHA 對應 manifest。首次控制的 runner-before-read-scope.py.txt 只少模型Read路徑核對，不能混成正式生成版本。

受限fixture主動把兩秒內不能完成的取鎖轉為 AssertionError，並記錄巢狀深度與退路狀態；這提供了部分失敗判準，所以不能把結果等同於完全自由、沒有fixture幫助的測試開發。整體程序15秒逾時仍invalid；語法、環境錯和零測試都不是檢出。
