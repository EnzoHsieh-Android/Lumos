severity: clean

審查摘要:我在 `git clone --shared` 的複本(HEAD 2359ed5f2)裡跑了約 30 道改壞實驗,每道都跑 `-k psrc`,有的另加綁定測試子集。複本已刪,沒動 repo。
- 開頭那把鎖檔 `.warming` 不存在,沒有鎖要處理。
- 未改壞前 `-k psrc` 是 250 過 0 敗。

**第四輪合約席 F1 到 F4 逐條重做**
- F1(`Systems/規格閘.md` 的 WHY 寫「同一段」、與程式相反):已修好。該行現在寫「行內註解只在同一行判,沒閉合照一般文字留著」,樹清單也改寫成走 `_drift_list` / `_drift_oids`。剩下兩處「同一段」都是歷史脈絡,不是現況描述。`lumos lint` 對規格閘和計劃兩篇都是 0 問題。
- F2(`scope="note"` 沒有綁定測試):已修好。首次加入日那條 WHY 補綁了 `t_psrc_first_days_note_scope` 和 `t_psrc_first_days_systems_node`。拿掉 `scope="note"`,這兩支測試翻紅(3 敗);只跑 PITFALL 綁的 `t_high_risk_evidence_since` 仍是 7 過 0 敗。但那條 PITFALL 守的是 `-M`/`-C` 改名偵測,不是範圍,所以不算漏。
- F3(CRLF 行數沒測試):已修好。`_repo_ref_source_line_count` 的改壞全翻紅:
  - CRLF 不扣一個換行:12 敗。
  - 結尾換行不扣:21 敗。
  - 空檔不回 0:2 敗。
  - 結尾只認 LF:6 敗。
- F4(`_plan_path_is_note` 只被 `Projects/` 底下的檔測過):已修好。改成只認 `/Projects/`,`t_psrc_first_days_systems_node` 翻紅。

**這輪新測試的改壞實驗(都有紅)**
- 讀 blob 走批次讀取(`t_psrc_blob_capped_reader`):
  - 上限換成別的常數:紅。
  - 超過上限回行數 0 而不是 None:紅。
  - 拿掉 blob 快取:三支計 git 次數的測試紅。
- 擋下原因(`t_psrc_reason_bad_chars`、`t_psrc_reason_case_links`):
  - 不先擋 NUL:紅。
  - 不先擋編不成檔名的字元:紅。
  - os 呼叫不接 OSError:紅。
  - `.git` 判斷分大小寫:紅。
  - 大小寫比對的連結、檔、經過連結判斷各拿掉一道:紅。
  - 兩種訊息分支對調:紅。
  - 解析結果不回版控裡的寫法:紅。
- 樹快取三態(`t_psrc_tree_timeout_notice`):失敗後重試、失敗不印、失敗不記,三種改壞都紅。
- 三支計 git 次數的測試:實測次數剛好是 6、5、5,和上限一樣大,沒有留空隙。
- 行號與大小上限用本 repo 實檔實跑:`scripts/test_lumos.py:128104` 和 `scripts/lumos:14595-14600` 算,超界的擋。

**S1 五種應擋**:條款、預期值表、`t_spec_gate_sources_section` 三方對得上。五種是 example.com、未來日期、行號超界、符號連結指到 repo 外、整節在 HTML 註解裡。

**放行三條**:四邊3、四通3、四架2 的理由我看過,成立。

**沒標成 finding 的觀察**
- 連結目標轉 NFC 那步(`nfc(raw.decode(...))`)拿掉後測試全綠,但後果只是多擋,不會放錯。
- 大小寫比對遇到只差大小寫的同名項,取哪一個的規則(取字典序最小、取先列到的)沒有測試。只影響訊息裡寫的是哪一個,不影響擋不擋。
- `.GIT/config` 那條在 Linux 上改壞測試不會紅(docstring 已自承),Linux 上這個路徑本來就不存在。
- `_plan_blob` 在 git 失敗時「不快取、下次再試」那句註解沒有測試守。拿掉後變成快取失敗,在單次執行的命令裡反而更省。
- 計劃偏離列新寫的「清單項與引用區塊照頂層規則判」沒有專屬測試。既有的 `t_psrc_inline_same_line` 涵蓋清單項,不涵蓋引用區塊。
- 計劃 S5 綁的 `t_kt_catalog_unverified_rows` 全 repo 找不到定義,但那是已有 `REVISIT:2026-11-20` 的延後項目,不在這次 diff 裡。

總結:最嚴重是無,會擋 0 條。
