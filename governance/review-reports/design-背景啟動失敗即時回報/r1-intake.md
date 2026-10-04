# design-背景啟動失敗即時回報 r1 前掃

preflight-4: ran

唯讀前掃逐查未定義詞、壞引用、範圍一致性與程式宣稱語意；`refcheck --json` 缺檔與越界均 0，`prose-lint` 無命中，`pitfalls --check` 有實務隱患節，計劃 lint 0 問題。`spec-gate` 初跑找出 S3/S4 句式缺「應」與回退標題混寫，已按工具要求修正；再跑為高風險、5 條全標，S3 舊測試真綠、相依回歸 2 支全綠，其餘新測試尚待紅燈與實作。

| 類別 | 原句、現碼與測試核對 | 前掃處置 |
|---|---|---|
| 核心語意 | 原 S4 稱啟動失敗應立即 rc 2，卻綁 `t_lens_stale_lock_reports_uncertainty`；該測試在 `_lens_cache_read` 回呼中建立替代鎖與可用快取，要求 rc 0 且新鎖仍在。若失敗後無條件返回，既有受測行為會倒退。 | 修為失敗清鎖後只讀一次可用快取：命中沿舊 rc 0，未命中立即 rc 2；S4 同時保留原測試與新增「替代鎖已取得但快取未命中」測試。核心裁定交正式席位再審。 |
| 前置條件 | 原 S1 寫「沒有替代快取或持有者」，但現碼只有等待輪詢讀快取；無法判定這句話是在何時檢查。 | 改成「本次取鎖、Popen 同步 OSError、失敗清鎖後單次讀取未命中」，替代持有者可有可無，不能以其存在否定本次未啟動。 |
| hook 分流 | 現行 `scripts/hooks/claude/dispatch-lens-hook.py` 只處理 `lock_error` 為 error，rc 5 為 timeout，其他 rc 2 多半靜默；`_role_text` 可從 rc 2 JSON 取角色段。 | S2/S5 明寫新增固定提示與 error 記帳、保留角色卡、不得把原始 reason 注入派工詞。 |
| 外部先例 | Python 官方 `subprocess` 文件說建構子常以 `OSError` 表示啟動前失敗，但 WSL/QEMU 某些路徑會先成功建立再由子程序非零退出。 | PRIOR-ART 與 RETIRE-IF 限定本案只辨識同步 `OSError`，後續退出須另設握手才可辨識。 |

前掃沒有把「已啟動但未算完」改成啟動失敗；S3 舊整合測試仍用來守住此邊界。正式審查需特別找一次快取重讀與替代鎖交錯的新洞。

## 正式席位逐項判讀與重現

重現環境：Python 3.14.6，隔離 clone，臨時目錄；故障注入命令在席報告 r1-boundary、r1-correctness 與本輪終端紀錄。換鎖注入得到 acquired=True、after=False，故 HIT；人工模式注入得到 rc5 與「鎖狀態未知」，故 HIT；Popen 加 unlink 雙故障連續兩次均 rc5 且鎖仍在，故 HIT。這三組皆有真實前置斷言，不把未進被測路徑的綠燈算證據。

| ID | 席位/判讀 | 重現與處置 |
|---|---|---|
| c1 | correctness major | HIT: Popen 失敗且 unlink 被拒、快取命中時現碼回 rc0 且原鎖仍在。folded: S1 明定清鎖失敗優先 rc2 與 lock_cleanup_error，即使快取有結果。 |
| c2 | correctness minor | HIT: 人工 CLI 目前依舊等到 rc5，S1 原句只綁 JSON。folded: S1 補固定人工診斷與不輸出原始例外。 |
| b1 | boundary major | HIT: Popen side effect 先換鎖再拋例外，替代持有者鎖遭按路徑刪除。folded: S4 要求建鎖當下保存裝置與 inode，失敗清理核身份，測 Popen 內與清理後兩種交錯。 |
| b2 | boundary minor | HIT: 同名鎖可由別的程序持有而尚未有快取；原「背景未啟動」會泛指所有程序。folded: S2 限為本次未啟動並提示同名鎖可能另有持有者。 |
| i1 | integration minor | HIT: 與 c2 同一人工模式缺口。folded: 同一 S1 與同一測試，不另開第二套提示。 |
| r1 | resources major | HIT: Popen 與 unlink 雙故障後下一次可能 rc5，且無法安全區分仍活著的持有者。accepted: 權限拒絕時不能保證能刪鎖或寫安全標記，自動依 PID/mtime 接手會違反既有不偷鎖決策；本次以 lock_cleanup_error 即時回 error，清鎖錯誤事件入口要求查權限、實際持有者與下一次狀態，實際安裝前案 S6 仍未放行。 |
| k1 | rollback major | HIT: 與 b1 同一換鎖交錯。folded: 同一 S4 身份清理與故障注入測試。 |
| k2 | rollback major | HIT: 舊 hook 對新 CLI 的 spawn_error rc2 只附角色卡，不記事件。accepted: 本分支不單獨部署；舊 hook 無能準確表達本次 spawn failure 的既有欄位，冒充 lock_error/timeout 會製造假訊息；前案實際安裝 S6 是成對安裝及重驗入口，未過前不得宣稱部署收斂。 |
| k3 | rollback minor | HIT: 舊測試只驗最終有注入文字，未驗停用開關零 Popen/零新鎖。folded: 新 S6 與 t_lens_no_cache_bypasses_warmer 釘住。 |
| a1 | architecture minor | HIT: 背景等待與轉述的既有家是 Systems/hook逾時預算。folded: lands_in 改指該節點，保留 Systems/codex-harness 與 Systems/測試假綠形態。 |

全輪報告 10 條，實際存活 10 條，折入 8 條、附理由接受 2 條、重現不到 0 條。高風險建議沒有直接照單全收：雙故障後自動偷鎖的處置會讓正在工作的替代持有者受害，因此只承認可觀測的殘餘限制，接上清鎖錯誤事件入口。
