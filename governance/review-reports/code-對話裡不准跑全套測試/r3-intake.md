# r3 收貨紀錄(code-對話裡不准跑全套測試)

兩席新席(審查三、架構對齊三)全數交回後才寫進卷證。架構對齊三初版檔首寫 clean、內文卻有一條 minor,退回該席改成 minor 並把那條獨立編號,存重交版。兩份 quote-check 全數錨定。

編號:審查三 U1(minor)、架構對齊三 C1(minor)。

## 重現

| id | 驗法 | 結果 |
|---|---|---|
| U1 | 新增 t_home_cache_append_line_rejects_loose_dir:事先建好同群組可寫(0770)的最後一層,斷言拒寫、不留檔;反面 0700 寫得進去。只拿掉 `_trusted_private_dir` → 照綠;再拿掉 `_mkdir_trusted_under_home` 的群組可寫判斷 → ①紅 | 現象 HIT(守衛測試只看字面);席位說的「這個案例會漏」MISS:`_mkdir_trusted_under_home` 逐層本身就拒同群組可寫的層,兩道檢查重疊。補了真跑行為的測試,兩道同時拿掉才紅 |
| C1 | 讀碼 | HIT:`_chat_guard_log` 用 `except Exception` 包住載入 scripts/lumos;計劃寫明計數盡力而為,載入可能丟任何例外,放行 |

修後:`-k home_cache_append_line` 3 passed;改壞驗證如上。
