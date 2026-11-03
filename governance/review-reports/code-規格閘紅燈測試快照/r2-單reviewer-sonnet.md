severity: major

我是第 2 輪單 reviewer。修補後共 6 條 finding,其中 2 條 blocking(F1、F2),其餘為 minor。下面每條都附修前、修後的同案例結果。

我的臨時目錄在 `/tmp/lumos-seat-work/code-規格閘紅燈測試快照/單reviewer-sonnet/`。`after/` 是 c627b3874 的複本,`lumos_before` 是 30ae09fb6 的 `scripts/lumos`,`t1.py` 到 `t8.py` 是我的重現腳本,`h.py` 是共用載入器,`W=before` 或 `W=after` 切版本。各腳本用 `python3.14 tN.py` 跑。

## 修補歸因界線

先讀了 `r2-repair-binding.json`。修前到修後除了修補,還混有改名(`_RB_*` 改 `_TG_RB_*`、`t_tg_redbase_*` 改 `t_tq_guard_redbase_*`)和拆小函式,沒有分開的中間版本。所以下面每條的歸因都附兩版實跑結果,不只看修後。

## Finding

### F1 新測試檔改名或搬家後,「預期值被改」從 weakened 降成 unmatched,原因文字還是錯的
severity: major
blocking: 是 — 計劃 S5 要求搬家照比,這條路徑上守衛的判定結果錯了,而且測試抓不住
引句:「if "TOOLARGE" in (b, h) or "UNREADABLE" in (b, h):」
file: `scripts/lumos:49843`(`_tg_rb_fill`);`_tg_read` 把缺檔也標成 UNREADABLE,見 `scripts/lumos:49399`;早退先於「分岔點已有就跳過」,見 `scripts/lumos:49820`(`_tg_rb_compare`)。

失敗場景:
1. 規格閘判紅時,紅燈版記的測試在分支內才新增的 `OldTest.kt`。
2. 推送前這支檔改名成 `NewTest.kt`,同時把 `assertEquals(900, …)` 改成 `800`。
3. `OldTest.kt` 在起點和終點都不存在,`_tg_read` 兩邊都回 "UNREADABLE"(缺檔和讀不出共用這個值)。
4. 修後的 `_tg_rb_fill` 把它當成「太大或讀不出」,`by_path["OldTest.kt"]` 變成字串,`_tg_rb_compare` 直接列 `tq/redbase-unmatched`,不再去 `NewTest.kt` 找同函式鍵。
5. 結果:真正的改弱(預期值被改)沒被指出,使用者看到的是「太大或讀不出」。這是 AI 最容易走的路徑(改檔名同時改 expected)。
6. 現有 S5 的「搬到別的檔」測試抓不到,因為它的紅燈版路徑是 `CalcTest.kt`,在主線就存在,兩端都讀得到。

次要症狀:S5 的「整支新測試檔先加後刪」仍列 unmatched,但原因文字也變成「太大或讀不出」,修前是「推送版找不到這支測試(被刪或改名)」。

重現(`t2.py` 是搬家,`t1.py` 是先加後刪):

```
cd /tmp/lumos-seat-work/code-規格閘紅燈測試快照/單reviewer-sonnet && W=before python3.14 t2.py; W=after python3.14 t2.py
```

歸因:**有證據的修復回歸**。

證據:
- claim:新測試檔先改名再改 expected,應照 S5 搬家路徑比,列 `tq/redbase-weakened`。
- input:紅燈版路徑 `OldTest.kt`(分支內新增),推送版只有 `NewTest.kt`(搬過去,expected 900 改 800)。
- expected:`tq/redbase-weakened`。
- case_source:我自建,依據計劃 S5 和 `_tg_rb_locate` 的搬家設計。
- before(30ae09fb6):`tq/redbase-weakened …同一支測試的預期值被改了`。
- after(c627b3874):`tq/redbase-unmatched … 推送版這支測試檔太大或讀不出,沒比`。
- comparison:同一輸入,修前對、修後錯。

### F2 `_tg_rb_pending` 只在推送頂端等於工作目錄頂端時才看工作目錄,這個守衛沒有測試釘住
severity: major
blocking: 是 — 這是本輪新增、鏡頭 4 與 S4 明寫的條件,拿掉它 106 條 redbase 測試全綠(守衛的唯一驗證落空)
引句:「if head != _lens_full_sha(root, "HEAD"):」
file: `scripts/lumos:49684`;測試端 `scripts/test_lumos.py` 的 `t_tq_guard_redbase_unreadable`、`t_tq_guard_redbase_reads_tip` 的 `h` 全是剛提交的 HEAD。

失敗場景:
1. 守衛被改壞或誤刪,例如重構時以為多餘。
2. 檢查別的提交時(`lumos test-guard --diff main..<舊提交>`,或 `git push origin <別的分支>`),工作目錄剛好留著另一條工作的未提交紅燈版。
3. 這時會對與工作目錄無關的提交列 `tq/redbase-unreadable`,擋推送,而且叫人去 `git add` 不相干的檔。

我拿掉那兩行做了突變:`python3.14 scripts/test_lumos.py -k redbase` 仍是 `106 passed, 0 failed`。

最小重現 `t5.py`:`h_old` 是舊提交、HEAD 已前進、工作目錄有未追蹤的紅燈版。

```
cd /tmp/lumos-seat-work/code-規格閘紅燈測試快照/單reviewer-sonnet && python3.14 t5.py; MUT=1 python3.14 t5.py
```

- 真版輸出 `[]`。
- 拿掉守衛的突變版輸出 `tq/redbase-unreadable 規格閘紅燈版讀不到、沒提交或被改過…`。
- 應補的測試就是 `t5.py` 這一支。

歸因:**有證據的修復回歸**,指新增的 `_tg_rb_pending` 沒帶測試。修前沒有這個函式,真版行為本身是對的。證據是修後守衛存在但移除後測試仍全綠。

### F3 判綠事件 `items` 的「平台感知」讀回端沒有測試
severity: minor
blocking: 否 — 只是覆蓋面缺口;突變會讓某平台的紅燈版少存(守衛變弱,不是錯擋)
引句:「if (c.get("plat"), c["name"]) in greened or (None, c["name"]) in greened:」
file: `scripts/lumos:14463`

失敗場景:android 判綠、backend 同名測試判紅時,若 `_redbase_cap_reason` 退回「只比測試名」,backend 的紅燈版會被誤判「曾判綠」而不存。
- r1 修補只測了 `_redbase_collect` 回傳的 `greens`,沒測讀回端。
- `t6.py`:真版 `_redbase_cap_reason` 對 `(backend, shouldCalc)` 在 `greened={("android","shouldCalc")}` 回 `None`。
- 把比對換成只看名字的突變版,同一輸入回「曾判綠(實作後補跑)…」,而 redbase 測試仍是 `106 passed`。

歸因:**有證據的修復回歸**。這是 r1 F1 修補的一半沒釘測試。

### F4 補讀測試檔的總量上限沒扣掉紅燈版已讀的位元組,也沒有測試
severity: minor
blocking: 否 — 超量最多約兩倍,且是資源上限的精度問題
引句:「deadline, max_total=max(0, _TG_MAX_TOTAL - consumed))」
file: `scripts/lumos:49838`、`scripts/lumos:49814`(`_tg_rb_compare` 把同一個 `consumed` 傳給 load 與 fill)

失敗場景:`_tg_rb_load` 和 `_tg_rb_fill` 各自拿到「200 MB 減已讀」的完整額度,紅燈版本身讀的位元組沒有累加進 `consumed`。
- `t4.py` 實測 `_nodehome_cat_blobs_capped` 的三次呼叫,`max_total_bytes` 分別是 200000000、199999705(讀紅燈版)、199999705(補讀,但紅燈版已用掉 21808)。
- 第三次應該是 199977897。
- 計劃與程式註解說「紅燈版與補讀的測試檔都算進 `_TG_MAX_TOTAL`」,只對了一半。
- 把補讀的 `max_total` 參數整個拿掉,redbase 測試仍 `106 passed`(r1-behavior-cases G3 自己也寫了沒有專門案例)。

歸因:**有證據的原有漏查**。修前 `_tg_rb_fill` 完全不算總量,修後只算了 `consumed`,沒算紅燈版自身。

### F5 寫入端讀「上一份紅燈版」時同檔仍每支測試重切一次(平方級),r1 的 F4 只修了讀取端
severity: minor
blocking: 否 — 慢但不錯;要同一個迴圈同一支檔有數百支紅測試才明顯
引句:「got = _tg_rb_entry(t, doc["files"])」
file: `scripts/lumos:14438`(`_redbase_branch_state`)

失敗場景:`_tg_rb_entry` 的 `cache` 參數只有 `_tg_rb_load` 有傳,這裡沒傳,每次呼叫都用空 cache,所以每支測試都重跑 `_tg_functions` 切一次整檔。
- `t3.py` 量到上一份紅燈版有 800 支測試時,`_redbase_branch_state` 要 12.17 秒(修前 11.90 秒)。
- 200 支約 0.76 秒,是平方級成長。
- 每次重跑規格閘都要再讀同迴圈所有舊紅燈版。
- 作者新增的 800 支效能測試只涵蓋讀取端和收集端。

重現:`N=800 python3.14 t3.py`,再用 `W=before N=800 python3.14 t3.py` 對照。

歸因:**有證據的原有漏查**。同族缺陷(同檔每支重切)只修了一個呼叫點,另一個呼叫點跟修前一樣。

### F6 計劃正文兩處沒跟著改,跟程式和 S4、S7 矛盾
severity: minor
blocking: 否 — 措辭與精度;但讀者照做會以為「兩者都沒動就完全不讀」,而程式現在會看 `git status`
引句:「用比對工具的 `_tg_start` 算分岔點;算不出來時兩處都看整本工作目錄治理帳。」
file: `docs/lumos-toolchain-knowledge/Projects/規格閘紅燈測試快照_計劃.md:61`(寫入端分岔點仍寫 `_tg_start`,程式已改成 `_lens_default_base` 加分支名判斷);同檔 `:69`(「兩者都沒動就完全不讀……漏 `git add` 紅燈版檔那種情況走不到偵測……起點是空樹……只印一句」)。

失敗場景:
- `:69` 與本輪 S4 新增的「治理帳與紅燈版都忘了提交也偵測」直接矛盾。
- 它仍說空樹起點「只印一句」,但程式已刪掉這句 print,S7 改寫成「新增告警閘本來就對空樹起點印一句」。
- 獨立跑 `lumos test-guard --diff <空樹>..HEAD` 現在完全不印,見 `scripts/lumos:49931` 一帶,`cmd_test_guard` 沒有對應輸出。

歸因:**有證據的修復回歸**,屬文件沒跟程式。

## 三問

**① 原問題的修復效果有何行為證據?**
- 跨平台同名:修前 `t8.py` 兩支都紅時只存 android,修後存 android 與 backend 兩份。
- JSON 跳脫後 5 MB、符號連結資料夾、上一份是符號連結不跟、上一份版本不認得、判綠擠掉原因、讀不出帳要出聲:這幾項我只確認修後 `t_spec_gate_redbase_written_on_red` 全綠,沒有逐項自跑修前對照,所以這幾項我沒有自己的修前證據。
- 紅燈版與治理帳都沒提交:S4 新測試通過,真版和 F2 的反例都已實跑。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常路徑:`-k redbase` 106 條通過。
- F1(搬家)是相鄰路徑,在修補的 `_tg_rb_fill` 上壞了。
- F2、F4、F5 是錯誤與邊界路徑的守衛沒測試或不夠。
- 其他我另外檢查過的相鄰路徑,看起來都沒壞:
  - S10 照終點判:`_tg_rb_load` 仍只讀 head 的 blob。
  - `_tg_rb_locate` 對字串型 `by_path` 的防護完整。
  - `_redbase_attach` 的「判綠」排序是穩定排序。
  - `_tg_rb_entry` 的 cache 共享 `fn` 物件,但 `_tg_rb_chain` 不修改它。

**③ 新發現的同一案例,修前與修後各是什麼?**
- F1 的兩個案例修前、修後結果分別見 F1 證據和下面的表。
- F5 修前、修後都約 12 秒,是原有漏查,不是修補造成。
- F2、F3、F4 在修前沒有對應程式,屬修補新增面。

| 案例 | 修前 | 修後 |
|---|---|---|
| F1 新測試檔搬家 + 改 expected(`t2.py`) | `tq/redbase-weakened` | `tq/redbase-unmatched … 太大或讀不出` |
| F1 先加後刪(`t1.py`) | `…推送版找不到這支測試(被刪或改名)` | `…太大或讀不出,沒比` |
| F5 800 支重切(`t3.py`) | 11.90 秒 | 12.17 秒 |

## 圖譜鏡頭

固定席牽連的節點,逐條判斷結果如下:

- **`Systems/guard-kill`、`Systems/lumos-cli-read`、`Systems/測試假綠形態`、`Systems/design-loop`、`Systems/lumos-cli-lifecycle`**:`git diff` 沒動到這幾個節點宣稱的函式,只動了 `_redbase_*`、`_tg_rb_*`、`_tg_read`。
  - 我跑了它們綁定的 `t_guard_kill_rc_precedence`(4 條)、`t_guard_kill_json_purity`(6 條)、`t_reinject_preserves_outside`(3 條)、`tq_guard_cli_contract`(99 條),全綠。
  - 其餘的 `search` 排除 superseded 與 slim_uninstall 那兩條,我的 `-k` 子串沒有選中任何測試,所以這兩條我沒驗。
- **`Systems/pitfalls-code-loop`、`Systems/loop-convergence-recording`、`Systems/reversibility-governance-ledger`**:僅標 `★RISK★`,沒有可驗證的合約行。簿記資料夾那一項的新測試(`S11 .kt 不算簿記`)通過。
- **舊測試名殘留**:grep 全 repo(排除卷證與帳本),沒有 `t_tg_redbase_*`、`t_spec_redbase_*`、`_RB_DIR` 殘留。
- **計劃與 `Systems/規格閘`、`Systems/test-guard` 兩篇**:見 F6,計劃正文兩處未跟上。

## S1 到 S11 核對(含計劃做法一、二)

- **S1**:收集端身分改成 `ident = (plat, method)`,`t8.py` 與測試都過。引句:「ident = (plat, method)」。
- **S2**:紅燈版比對沒被改壞,引句:「S2 終點沒有斷言:只列 tq/no-assertion 一條」。
- **S3**:引句:「S3 兩份 ts 寫反照行序判:只有第一份→第二份那一步命中」。
- **S4**:
  - 引句:「S4 治理帳與紅燈版都還沒提交(推的就是工作目錄的頂端):列 unreadable 講還沒提交」,測試過。
  - 但 `head == HEAD` 這個條件沒有反向測試(F2)。
- **S5**:
  - 引句:「S5 紅燈版記的測試檔在推送版括號配不平:列 unmatched、講沒比」。
  - 搬家路徑對「新檔改名」壞了(F1),先加後刪的原因文字錯。
- **S6**:引句:「S6 主線上早就有的判綠不算:這條分支跑紅照存」,過。`_redbase_branch_rows` 的 `fork == head` 且分支名為 `main`/`master`/空時才看整本,`feat` 分支剛開時照減分岔點,我走過這條路,行為對。
- **S7**:
  - 引句:「S7 單檔 800 支紅燈測試:比對 5 秒內」,過。
  - 但「兩者都沒動就完全不讀」,現在每次比對在推 HEAD 時都會多跑一次 `git status`。結果相同、成本小。計劃 `:69` 沒改(F6)。
- **S8**:引句:「S8 紅燈版與終點都沒斷言:照舊列 tq/no-assertion」,過(`t_tq_guard_redbase_still_checks_new_rules` 通過)。
- **S9**:引句:「S9 放行一條紅燈版候選、另一條照擋」,過。指紋改為帶子候選的 key,與計劃一致。
- **S10**:
  - 引句:「S10 工作目錄多一行沒提交的留痕:不拿它來比(不列改弱),只提醒紅燈版還沒提交」。
  - 「照終點判」仍成立:比對仍從 head 的 blob 批次讀(`_tg_rb_load`),沒有讀工作目錄。
  - 新加的工作目錄偵測只在推 HEAD 時啟用,守衛沒有測試(F2)。
- **S11**:引句:「S11 紅燈版資料夾裡出現 .kt:不算簿記」,過。

## 未驗範圍

- 沒有逐項自跑修前對照的修復項,已在問 ① 說明。
- 沒測 `git status` 在大型 repo 逾時時的退化路徑,程式碼上是回空集合(靜默略過)。
- 沒驗 Windows 路徑。
- 沒驗 CI 乾淨 clone 的真實流程,只讀程式與單元測試。
- 沒驗 `_tg_rb_load` 的 deadline 逾時分支(沒有測試覆蓋)。

總結:最嚴重等級為 major,blocking 共 2 條(F1、F2),minor 4 條(F3 到 F6)。
