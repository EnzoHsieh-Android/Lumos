severity: minor

## Finding CTR8-01
severity: minor
blocking: 否
引句:「改由測試核對兩邊寫法一致(t_probe_boundary_fourth_round_report_and_provenance)。」
file: `governance/eval/ablation_lumos_first.py:385`
- 具體輸入:主程式 `_PATH_SPECIAL_CATS` 改了類別,例如拿掉 `Zl/Zp/Cs`,或加上 `Co`。
- 走到哪一段:`t_probe_boundary_fourth_round_report_and_provenance` 裡的 `expect = lm._kill_esc(sample).replace("\\","\\\\")`。`sample` 只含 `\u202e \ufeff \U000e0001 \u3000 \u00a0 x`,也就是只含 Cf 和 Zs 的字元。
- 壞在哪:程式註解說「由測試核對兩邊寫法一致」,但測試只比對這幾個字元,沒有比對類別集合。`Cc/Zl/Zp/Cs` 不在樣本裡,任一類被主程式改掉,測試都不會紅。
- 重現:在副本把 `scripts/lumos` 的 `_PATH_SPECIAL_CATS` 改成 `("Cc","Cf")`,再跑 `-k probe_boundary_fourth_round_report_and_provenance`,得到 `15 passed, 0 failed`。改成加上 `"Co"` 也是 `15 passed, 0 failed`。對照:報表端拿掉 `Cf` 時同一支測試會紅。
- 回答問題「獨立 oracle 還是重抄實作」:`_kill_esc` 是動態基準,不是重抄。主程式改動樣本內的類別時,測試會翻紅。但它只涵蓋樣本字元,註解宣稱的同步保證不成立。
- 歸因:有證據的修復回歸。
  - 修前 `67b1dea2` 沒有這句同步宣稱,修後 `e5ce8675` 才有。
  - 命令:`git show <sha>:governance/eval/ablation_lumos_first.py | grep -c '改由測試核對兩邊寫法一致'`,修前輸出 0,修後輸出 1。

## Finding CTR8-02
severity: minor
blocking: 否
引句:「報表裡的外部文字只把控制、格式（雙向覆寫、零寬）、行段分隔、代理這幾類字元寫成看得見的 `\uXXXX`」
file: `docs/lumos-toolchain-knowledge/Verification/持久用量帳第六輪審查修補驗證.md:24`
- 問題:這條驗證紀錄 `status: pass`,`revalidate_when` 列了 visible,內文仍寫「報表的不可列印字元改寫成 `⟦U+XXXX⟧`」。第七輪把這個寫法推翻,第六輪紀錄沒有加更正或指向新節點。
- 同一份第六輪紀錄第 20 行「追加模式只收普通檔與字元裝置」,也被第七輪的「只有一個名字」規則取代。
- 三個月後接手的人讀到這份 pass 紀錄,會以為 `⟦U+XXXX⟧` 是現行寫法。
- 重現:`git grep -n '⟦' e5ce8675 -- docs/lumos-toolchain-knowledge`,結果出現在 `Verification/持久用量帳第六輪審查修補驗證.md:24`。
- 歸因:有證據的修復回歸。修前該行是現況,修後變成過期說法。

## Finding CTR8-03
severity: minor
blocking: 否
引句:「不像主程式清理注入內容的 `_esc_clean` 那樣換成空白」
file: `scripts/lumos:11245`
- 問題:`_esc_clean` 的 docstring 寫的是「逃逸帳顯示消毒」,用在 doctor 輸出的顯示消毒,不是「清理注入內容」的函式。WHY 用錯了名字或描述。
- 結果:接手的人照這句去找「注入內容清理」,會找到錯的函式。
- 重現:`sed -n 11245,11250p scripts/lumos`;`grep -n '_esc_clean(' scripts/lumos` 的呼叫點全是顯示行。
- 歸因:有證據的修復回歸。這句是第七輪新增的 WHY。

## 固定席逐條判定
- `Systems/codex-harness`(家):新 PITFALL 的鍵齊全(`出處`、`根因`、`test`)。
  - 宣稱逐項對上 `scripts/scenario_probe.py`:`_open_char_device` 有 NOCTTY、fstat、set_blocking;`_output_target_problem` 試開;`_open_history` 收單名普通檔與字元裝置;暫存檔用 keep_mode 建立。
  - 新 WHY 的鍵也齊。
  - `lint` 兩條 warning 是原有的 FACT 行,與本次無關。
- `Systems/測試假綠形態` ★INVARIANT★:新測試都有前置現場斷言,例如 `tmp_modes` 長度、decoy 被看成字元裝置、SCENE leader/ctty、現場 FIFO/硬連結。不破壞合約,還原結果見下表。
- `Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject):不受影響。
  - 第 140 行新說明成立。我拿掉 `scripts/lumos` 的 `O_NOCTTY` 後,`t_confirm_tty_unit` 仍是 6 passed,`t_confirm_tty_no_ctty_session_survives` 翻紅。
  - 新說明沒有再把 `t_confirm_tty_unit` 當防回歸。
- `autonomous-iteration-loop`、`lumos-cli-read`、`design-loop`、`bound-tests-gate`、`canary-audit`、`guard-kill`、`slim-*`、授權與其餘只列名的節點:本次沒改它們的程式檔,宣稱與合約不變。
  - `design-loop` 牽連的 `ablation_lumos_first.py` 只改了 `visible`。
  - 新綁定測試名都存在。
- 殘留舊說法:`⟦U+XXXX⟧` 只剩 CTR8-02 那一處,另外兩處是明寫「不選」的歷史說明。`t_confirm_tty_unit` 當防回歸的舊寫法已清掉。

## 還原翻紅結果表
測試目錄是 `e5ce8675` 副本,逐項改壞後各自跑對應測試。

| 項 | 改壞方式 | 結果 |
|---|---|---|
| ① | 拿掉 `O_NOCTTY` | 紅:`char_device_session` 的「寫進終端不會把它收成控制終端」,輸出 `AFTER_WRITE ctty=True` |
| ② | 拿掉 fstat 字元裝置確認 | 紅:「開到的不是字元裝置就不寫」,結果 `NEWp` |
| ③ | 拿掉 `set_blocking` | 紅:「終端讀得慢時大量輸出照樣寫完」,`BlockingIOError` |
| ④ | `_output_target_problem` 不試開 | 紅:`char_device_session` 的 `--out` 與 `--history` 兩條 |
| ⑤ | `_open_history` 拿掉型別與名字數確認 | 紅:換成有人讀的 FIFO 與換成硬連結兩條 |
| ⑥ | `_open_history` 拿掉 `O_NONBLOCK` | 紅:「換成沒人讀的 FIFO:報錯不卡住」 |
| ⑦ | 暫存檔改回 `0o666` 建立 | 紅:`['0o644']` |
| ⑧ | `visible` 的類別組拿掉 `Cf` | 紅:`_kill_esc` 一致性那條 |
| ⑨ | `_guard_hang` 不還鬧鐘 | 紅:「測試執行器原本的逾時還在」,值 179.9 |
| ⑩ | 在輔助函式裡呼叫 `umask` | 紅:「寫入期間呼叫了 umask」 |

- ⑨ 的那條斷言在執行器本身沒有鬧鐘時是空轉(`runner_left == 0`)。在 `test_lumos.py` 執行器下鬧鐘存在,所以有效。
- 十項全部翻紅,沒有假綠。

## 驗證紀錄數字重現
在 `-k` 副本上跑,只跑子集:
- 第五輪輸出 39 passed、第四輪報表 26、終端確認 8、等待 2,都和紀錄一致。
- 消融子集 4 與「消融單元測試 OK」未另跑。
- 紀錄寫「探針大子集 424 passed / 0 failed」,我跑 `-k probe` 得到 423 passed、1 failed。
  - 失敗的是 `t_probe_discipline_targets_are_fresh`。
  - 這很可能是副本沒有完整 docs 與目標題而造成的環境差異,不能歸到審材。
  - 所以 424/0 在這個副本無法重現,但也不構成反證。
- 「兩支產品檔的規則告警與修前相同」未驗。

## 修補三問
- 原問題的修復效果:每個 repair 案例都有可翻紅的行為證據(見上表)。G-ESC 的報表測試由 `15 passed` 來,Verification 紀錄寫的是 26 passed(全 `fourth_round` 子集)。
- 修補處的正常、錯誤與相鄰路徑:
  - preserve 項全過:`/dev/null` 照寫、FIFO 換成普通檔、新檔照 umask、0640 保留、自擁單名檔沿用。
  - `-k fifth_round_output` 39 passed、`-k probe_boundary` 192 passed,0 failed。
  - 新增 `for…else` 的 100 次撞名上限,控制流正確。
- 新發現案例的修前與修後:CTR8-01 修前沒有同步宣稱、修後宣稱不成立;CTR8-02 修前正確、修後過期;CTR8-03 修前沒有這句、修後才有。

## 未驗範圍
- Linux 與 root 的行為。
- 全套測試和推送閘。
- `r7-mutation-checks.log` 裡十一種改壞版本的原始紀錄。
- 規則告警(複雜度)與修前是否相同。
- 非 POSIX 平台。
- 在有真正控制終端的互動式 shell 裡跑 ①,我是在沒有控制終端的 session leader 子程序裡驗到它翻紅。
- 實驗目錄已 `rm -rf`。

總結:最高嚴重度 minor
