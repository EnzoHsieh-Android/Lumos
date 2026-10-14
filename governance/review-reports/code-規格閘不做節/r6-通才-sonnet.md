severity: minor

審查範圍是修補差異,另跑了 `-k nogo`(253 條)、`-k prepush_spec_gate`(12 條)、`-k disposal`(183 條),全綠。

一開始跑 `-k prepush` 時有 36 條報 `No such file` 的暫存目錄例外。我清掉殘留目錄後重跑相關子集全綠,判斷是同機其他會談清暫存造成的干擾,不是這次修補的問題。

我留在 `/var/folders/.../T/` 底下的暫存都清掉了。該目錄現在剩 5 份 `gctl-run-*`,不是我的,沒碰。

## Finding

severity: minor
blocking: 否 — 只有審查帳讀不到這種少見情境才會觸發,而且工具壞了放行本來就是這道閘寫明的政策;但現在放行時一個字都不印
引句:「except OSError as e:
        return {"by_loop": {}, "err": e, "snap": {}}」
問題:讀帳改成開頭讀一次(`_nogo_ctx`)後,`OSError` 被吞成空表。原本 `_spec_gate_latest_records` 讀帳失敗會直接丟例外,推送前檢查因此失敗而擋下。現在 `latest` 變成空的,所有風險低計劃都不算「有風險低留痕」,留痕裡的測試不跑,小改動閘和留痕過期檢查也不做。`err` 只有不做清單略過了危險詞的計劃才會講出來。
具體失敗情境:我造了一份有風險低留痕、條款測試是紅的計劃。審查帳可讀時推送前檢查是 rc1,印「留痕裡的測試沒全綠」。對審查帳做 `chmod 000` 後,同一個推送是 rc0,stdout 和 stderr 都沒有任何提示。
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos`(`_nogo_ctx` 與 `_spec_gate_push_scan` 開頭)。
修法建議:讀不到帳時,`_spec_gate_push_scan` 要像「平台設定讀不動」那樣印一句再放行,或改成擋下。

## 你點名的幾個面向

- **門規則版本升 4,對既有留痕與風險低計劃:已讀,無 finding。**
  - 帳上每個編號的最後一筆留痕,`door_rule` 全是 1,版本不符本來就普遍存在,不是新問題。
  - 18 份最後一筆是風險低的計劃,我用新規則重判:只有 `派工鏡頭跨repo不再靜默_計劃` 因第 60 行圍欄裡的「錨點」變成風險高,其餘 17 份仍是低。
  - 那一份狀態是 `done`:不是推送前的 doing 候選,碰到它時 `_spec_gate_push_nogo_only` 判高後直接回 None,不擋。
  - 另有幾份 `doing` 的計劃重判後仍是低,不受影響。
  - 提醒:圍欄內的詞也算的副作用是範例、指令樣板寫在圍欄裡會多判高,方向是保守,屬設計取捨。
- **`_prov_check` 接 `ValueError` 對處置閘:已讀,無 finding。**
  - 三個既有呼叫點(26610、26899、26922 行)都是「讀不到」就走既有的失敗分支,含 NUL 的路徑從崩潰變成報失敗,沒有誤放行。
  - `-k disposal` 183 條全綠。
- **`t_prepush_nogo_plan_not_skipped` 期望改動:已讀,無 finding。**
  - 擋下仍然成立,只是出口從「先跑規格閘」改成「補一筆綁好的輕量審」。這是 r5 G2 的刻意改動:做完且全綠的計劃跑規格閘過不了、也不留痕,等於沒有出口。
  - 副作用:原本留痕是風險高、現在判成風險低的計劃,不再被強迫重跑規格閘,只要一筆輕量審就放行。留痕裡的測試不會跑,風險低的完整檢查也不做。這是這次改動的取捨,屬設計層面,不算 bug。
- **入口清 git 環境對所有子命令:已讀,無 finding。**
  - 我在 git 2.39.2 實測 `GIT_GRAFT_FILE=/dev/null/lumos-no-grafts` 加 `GIT_NO_REPLACE_OBJECTS=1`,`git log` 和 `git fsck` 都正常、不報警告。
  - 新增的 `t_prepush_nogo_git_replace_still_blocks` 和 `t_prepush_nogo_git_grafts_still_blocks` 也在 `-k nogo` 裡通過。
- **讀帳一次的快取,同一次推送多個 ref:已讀,無 finding。**
  - 每個 ref 各跑一次 `_spec_gate_push_check`、各自建 `ctx`,不會跨 ref 共用過期資料。
  - 單次掃描中途 `_auto_escape` 追加的帳,只影響各計劃自己的編號,不影響其他計劃的查表。
  - `_nogo_snapshot_rows` 的快取以(路徑, 帳上雜湊)為鍵,結果與計劃無關,沒有串錯的風險。
- **補充觀察(不算 finding):**
  - `_nogo_major_carried` 讓任何一筆輕量審的 major,在被略過的那幾行沒改之前永遠照擋,即使 major 說的是計劃別處,逃生口是 `plan_risk: high`。
  - `_nogo_is_arch_seat` 用 `arch` 子字串判斷,`research` 之類席名會被當架構席。兩者都是 r5 刻意的「寬判多擋」,方向保守。

最高等級 minor,blocking 0 條。
