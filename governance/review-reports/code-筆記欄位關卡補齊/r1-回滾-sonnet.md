severity: clean

## 已驗過、沒問題

在 `/tmp/lumos-rollback-review`(從 `/Users/enzo/harness/lumos-toolchain` clone 的複本)裡把 `.lumos/config.json` 的 `note_lint.gate` 分別改成 `on` / `warn` / `off`,對五個行為逐一實跑驗證:

1. **`lumos lint <節點>`(單篇快檢)**:建一篇缺 `status` 的測試節點。`on` 時「沒填 status」判 error(exit=1,擋提交);`warn` 時同一條降成 warning 且訊息帶「專案開關 note_lint.gate 是 warn,先提醒不擋」(exit 仍為 1,但那是因為同一篇還踩到「原有規則」的 `沒寫 aliases`——這條不受開關影響,見下);`off` 時「沒填 status」完全不出現,連 warning 都不印。行內引句:
   引句:「if mode != "off":」
   引句:「errs.extend(new)」
   對應:`scripts/lumos:4844`、`:4846`(clone 內同一份,patch 對應 hunk `@@ -4791,20 +4817,47 @@`)。

2. **`lumos doctor` 的 L 段擴充**:同一篇測試節點在 `on` 時被列進「有 N 篇筆記沒通過 lint 的錯誤等級規則」且 `doctor --ci` exit=1;`warn` 時同一段改印「note_lint.gate 是 warn,先提醒不擋」且 `doctor --ci` exit=0;`off` 時整段印「筆記欄位規則被關了…這一步不跑」。且驗證這個擴充段落**同時把「原有規則」的 error 也一併照開關**(例如「沒寫 aliases」這條在單篇 `lint` 永遠擋,但在 L 段擴充裡照樣受 `note_lint.gate` 控制)——這點程式碼有清楚寫在注解與筆記摘要裡:
   引句:「★原有規則也照開關★(r3 外家席)」
   引句:「不讀碰到清單(預告合約那段的 --touched-from 擋法不受影響)。」
   查了 doctor 整段輸出,確認沒有出現 `--touched-from` 字樣,跟注解一致。

3. **`lumos lint` 對「原有規則」不受開關影響**:同一篇缺 aliases 的節點在 `note_lint.gate=off` 時,`lumos lint` 仍把「沒寫 aliases」判成 error、exit=1——證實「新規則擋不擋看開關,原有規則不受影響」這句設計說法對單篇 `lint` 成立。
   引句:「# ★這次新增的欄位規則擋不擋看專案開關★(筆記欄位關卡補齊_計劃;原有規則不受開關影響,S13)」

4. **設定檔壞掉的降級**:把 `.lumos/config.json` 換成非法 JSON 後跑 `lumos lint`,印出「.lumos/config.json 讀不了(JSONDecodeError),筆記欄位新規則用預設(只提醒)」,行為等同 `warn`,跟設計一致。
   引句:「except Exception as e:」
   引句:「return mode, [f".lumos/config.json 讀不了({e.__class__.__name__}),筆記欄位新規則用預設(只提醒)"]」

5. **`set responsibility`、`append about_code`、`new --code` 三個寫入口刻意不看開關**——這是這個鏡頭(回滾)最該盯的地方:把 `note_lint.gate` 依序改成 `on`/`warn`/`off` 後,對同一批操作各跑一次:
   - `lumos set <節點> responsibility "短"`(僅 1 字):三種開關值下都回「擋下:負責範圍至少 10 個字…檔案沒動」、exit=2,一致。
   - `lumos append <節點> about_code "docs/lumos-toolchain-knowledge/Systems/回滾測試節點.md"`(筆記路徑):三種開關值下都回「在圖譜資料夾裡,是筆記不是程式檔」、exit=2,一致。
   - `lumos new system <名> --code "docs/lumos-toolchain-knowledge/Systems/回滾測試節點.md" --responsibility "…"`:`gate=off` 時仍擋下、exit=2、沒建檔。
   代表如果上線後想「撤」,把 `note_lint.gate` 設回 `off` **只能讓 lint / doctor 兩處降級,救不回 `set responsibility` 與 `append/new --code` 這三個寫入口**——想讓這三處也放寬,必須改程式碼(revert 或改條件),不是改設定檔。但這件事在程式碼注解與知識圖譜摘要裡都寫得很清楚,不是隱藏行為:
   引句:「不看開關(筆記欄位關卡補齊_計劃 S11;不看開關——r3 架構席:」
   引句:「有一篇 Issue 就是用 append 把筆記路徑寫進 about_code;要連結別篇請寫 related。」
   （知識節點出處,非引自 patch,僅供對照)：`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:1`(summary 第一行 KEY 明寫「不過就擋、檔案不動,不看開關」)。
   → 結論:這是設計刻意如此且已寫清楚,不是作者沒看到的漏洞;回滾當天如果要連這三個檢查也一起撤,操作者得知道「改設定檔不夠、要改程式碼」,而這一點文件已經講了,不算 gap。

6. **相關單元測試**:在複本裡跑 `python3 scripts/test_lumos.py -k t_note_lint`,12 個相關案例(gate 預設、on 擋、off 不跑新規則、原有規則不因開關放寬、壞設定檔各分支)全數通過,跟上面手動驗證的結論一致。

沒有發現需要擋下的問題;`note_lint.gate` 對 `lint`/`doctor` 兩處的降級行為與文件宣稱完全一致,而 `set`/`append`/`new --code` 刻意不受這顆開關控制的事實也在程式碼注解與圖譜筆記裡寫清楚,不是漏寫。
