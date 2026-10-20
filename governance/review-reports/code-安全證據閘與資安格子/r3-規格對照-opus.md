severity: major

## 1. S42 改寫後,故障證據的判定碼內部錯誤仍被收成單項 report_malformed,不會整道判 evaluation_error
severity: major
blocking: 是

S42 這一輪改寫成:判定碼自己的 KeyError、IndexError 要整道判 evaluation_error,只有讀進來那一層判出的外來資料型別錯才只讓那一項判 report_malformed。外層的分派這一輪已改成只接 `_SecevDataError`,但 `_secev_judge_tq` 裡面還有一層寬的 except。

- file: `scripts/lumos:8879-8884`(47434676 版)——`ctx.tq.fault_check(phases, targets)` 外面包著 `except (KeyError, TypeError, AttributeError, ValueError, IndexError): return ["report_malformed"]`。`fault_check` 是三階段核對,屬判定碼,不是讀法。它吃的資料已經由 `load_receipt_data` 驗過形狀,讀檔的錯另在 `_secev_tq_phase` 那一層(8858)接,所以這一層接到的實際上就是程式內部錯誤。
- 後果:程式內部錯誤被收成單項 invalid。依 `scripts/lumos:10291-10293` 程式註解的說法,單項不合格可以被例外蓋掉放行。這正是條款要擋的情形。
- 綁定的測試抓不到:這一輪新增的注入是把整支 `_secev_judge_tq` 換掉,例外直接丟到外層,所以裡面那層寬 except 從沒被走到。

引句:「for fn, exc in (("_secev_judge_junit", KeyError("注入的程式內部錯誤")), ("_secev_judge_tq", IndexError("注入")),」

重現:`/tmp/lumos-seat-work/code-安全證據閘與資安格子/規格對照-opus/probe/p1.py`。它用 `_SgRepo` 建 repo,再把 `_secev_tq().fault_check` 換成直接丟 KeyError:
```
python3.14 -I p1.py <修後工作樹>
baseline fault: [] None
fault_check KeyError -> None ['invalid:report_malformed'] blocked True
```
gate_code 是 None,不是條款要的 evaluation_error。在修後版上 `t_secev_s42_deep_and_errors` 照綠,所以測試翻不紅。

歸因:有證據的原有漏查。同一支 p1.py 對修前 7655a12d 跑,結果相同(`None ['invalid:report_malformed']`)。這一輪改寫了 S42、也收窄了外層,但沒有把同族的內層 except 一起掃掉。

## 2. S64「那支檔不在樹上」這一半沒有測試釘住
severity: minor
blocking: 否

S64 寫的是「指紋不同、或那支檔不在樹上」都判 stale:receipt_source_changed。綁定的測試只造「檔改了」的情況。我把 `scripts/lumos:8918` 改成只比「樹上有、而且內容不同」的檔(不在樹上的直接放過),`-k t_secev_r2_fault` 的 8 條斷言照綠。

在現有夾具裡,刪掉實作、測試或 context 都還會被 binding_incomplete 擋下(p2.py:修後版是 `binding_incomplete + receipt_source_changed`,改壞版只剩 `binding_incomplete`)。所以只有「收據快照了、但沒列進綁定」的 context 檔被刪掉時,才會完全沒人擋。

引句:「"stale:receipt_source_changed" in _sg_codes(rep, "fault_sensitivity") and path in (it.get("receipt_source_changed_paths") or [])」

歸因:未判定。這兩條規則都是本輪新增,修前沒有可比的行為。

## 3. S65 的前提「這條護欄有 behavior 證據時」沒有測試釘住
severity: minor
blocking: 否

我把 `scripts/lumos:8943` 的 `if beh and not (red & counter):` 改成 `if not (red & counter):`,S65 的測試照綠。改壞之後,沒有 behavior 證據的護欄也會被判 fault_unrelated,屬於誤擋。三支測試的故障情境都帶 behavior 證據,所以分不出這個差別。

引句:「fault 收據改壞的實作檔不在這一項的綁定或家節點程式檔裡 → invalid:fault_unrelated;紅掉的測試跟這條護欄 behavior 證據的反例目標」

(這句取自 r3-repair-tests.patch 裡 `t_secev_r2_fault_evidence_unrelated` 的 docstring,不是計劃文字;已用 `grep -cF` 確認在那份 patch 逐字出現 1 次。)

歸因:未判定(本輪新增)。

## 4. d19 承諾寫進 limitations 的天花板(直接寫核可檔)沒有測試守著
severity: minor
blocking: 否

d19 寫的是「天花板照實寫進…security evidence 的 limitations」。修後的 `scripts/lumos:10600-10601` 確實加了「繞過這支指令直接寫 .lumos/security-approvals.jsonl…(計劃 d19)」。但守 limitations 的測試只檢查「偽造終端」四個字,而修前的舊句「核可寫入要互動終端加手打確認碼;刻意用 script 之類工具偽造終端…」也含這四個字。限制文字退回 d19 之前的版本,測試照綠。我在混合目錄(修前程式配修後測試)跑出的 `security evidence` 輸出裡看得到那句舊文字。

引句:「check("天花板 偽造終端寫進 limitations", any("偽造終端" in x for x in lim), str(lim))」

歸因:未判定(d19 是本輪新決策;這條是 decision,沒有綁 [test:])。

---

### 三問

**① 修復效果的行為證據**

我拿修前 7655a12d 的 scripts 配修後的 test_lumos.py 跑 `-k t_secev_r2_`,結果 22 條斷言過、29 條紅、1 條略過。紅的涵蓋以下幾組,這些修補在修前確實會紅:
- 符號連結:三處都紅。
- 印出外來字串前的清理:V2 那幾支全紅,修前輸出裡看得到原樣的 ESC 和自成一行的注入句。
- 擋下訊息跟著原因代碼走。
- S64、S65(各 4 條、2 條)。
- 追加用位元組模式寫入。
- 主線設定檔讀不到。
- payload 遇到壞的 covers_kinds(修前印 traceback)。
- 預檢回 no_registration 蓋掉 mainline_unknown。
- 3000 個符號連結的預算(修前 110.5 秒)。
- 漏洞庫極端日期(修前 OverflowError 變成 evaluation_error)。

S42 在修前紅了 4 條。

修前就綠的是補覆蓋、不是修行為,包括:mixed_tty(修前已經要求兩端都是終端)、S9 校準綁定、S13 入口過濾、S52 的「推送版自己設的主線不採用」那條新斷言。

**② 正常、錯誤與相鄰路徑**

我在修後版抽查三條本輪沒改的條款,都還成立:S6(`t_secev_s06` 4 條過)、S7(5 條過,而且跟 S65 不衝突:非目標測試紅掉照樣在 fault_check 那層判 invalid)、S44(2 條過)。

計劃這一輪改寫的地方我逐條比對了程式,以下都對得上:
- 核可鏈筆數上限 2000,超過判 read_incomplete(`_SECAPR_MAX_ENTRIES`、`_SecaprTooLong`)。
- payload 的 `--outcome`、`--reason`、`--content-file`、`--commit`,以及 consideration 照 30 天或 180 天的上限(`_secapr_entry_dates`、`_secev_consideration_counted`)。
- S38 的符號連結逐層檢查(用共用的 `_repo_path_unsafe`)。
- S50 要兩端都是終端。
- d17 改寫後與 d19 不矛盾;確認碼函式的註解也已改成「只管這支指令」。

**③ 同一案例修前、修後的結果**

只有發現 1 有兩版對照:兩版都是 report_malformed(原有漏查)。發現 2 到 4 都是本輪新增的規則,修前沒有那段行為可比,記為未判定。

### 未驗範圍

- 全套測試沒跑。
- `t_secev_r2_golden_capture_reproduces` 在混合目錄被略過(找不到 golden 檔)。
- `--outcome` 等 payload 新旗標只讀了程式,沒有跑測試翻紅。
- 只翻紅了 S64、S65 這兩處變異,其他新條款沒有逐條做變異測試。

我自己產生的 gctl-run 暫存現場、兩個 detached worktree、mix 與 mut 目錄都已刪除。重現腳本與 log 留在 `/tmp/lumos-seat-work/code-安全證據閘與資安格子/規格對照-opus/`(probe/、mix-r2.log、mix-s42.log、mix-s52.log、mut1.log),收貨後請編排者刪。

最嚴重 severity:major;blocking 共 1 條。
