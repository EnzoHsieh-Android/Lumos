severity: minor

我照 skill 實際走了一遍,沒有找到會讓人做錯的洞,只有 3 條知識同步上的措辭問題。

- **貼進收據再重跑**:我把範本換掉佔位字,整份貼在 `-- [Q1] … expect=f100:compose_ns=20,xml_ns=10` 標頭底下,再用 `android-receipt-rerun.sh` 跑。用的是自己寫的 sqlite 假 `trace_processor`,不是真的 Perfetto。同一份 queries.sql 貼兩條 Q 回 0,把換行改成 CRLF 也回 0。
- **修補前**:修前的範本(`f96ffe70`)因為註解行以分號結尾,查詢被截斷,結果是 `BAD Q1`、rc=1。
- **既有測試**:`-k android_ui_attribution` 47 個全過,`-k license_headers` 8 個過。我另外跑了 `-k vendored`(92 個)、`t_slim_uninstall_manifest_parent_cleanup_is_best_effort`(5 個)、`guard_kill_rc_precedence`(4 個),全過。
- **指令是否存在**:skill 叫人跑的 `lumos compose-metrics --audit`、`lumos macrobench --repo … --update-baseline --json` 都存在,參數對得上。
- **消費專案路徑**:範本已登記在 `_VENDORED_TREE_FILES`(`scripts/lumos:31929`),消費專案在 `scripts/templates/` 下拿得到。
- **效能**:3000 幀、每幀 42 個區段、300 種不重複名稱,修前修後都是 0.45 秒。`IS` 與 `MAX` 沒有拖慢。
- **三處說法一致**:expect 寫法、第一欄是 `f` 接幀起點、標頭格式,skill、`reference.md` 和範本檔頭三處講的一致。

## 1. 計劃的 WHY 行還是舊的管線名單,skill 的名單又比範本短
severity: minor
blocking: 否
引句:「兩種寫法共用的畫面管線(input、animation、traversal、measure、layout、draw、Record View#draw()、postAndWait)單獨一類」
file: `docs/lumos-toolchain-knowledge/Projects/Android介面寫法分流_計劃.md:22`
歸因:有證據的修復回歸。修補只改了同檔的規則表(第 44 行)和 S8,沒改這行決策 WHY。
- **場景**:接手者讀決策 WHY,會以為任何 `draw` 開頭的區段都算管線。範本修後已經只認 `draw` 與 `draw-VRI*`,表和 S8 也寫了「App 自己打的 draw 開頭區段不算」。
- **skill 的名單**:`SKILL.md` L1 第 2 步只列「input、animation、traversal、measure、layout、框架的 draw」,少了範本認的 `Record View#draw()`、`postAndWait`、`draw-VRI`。
- **兩版查證**:`git show f96ffe70:scripts/templates/android-ui-attribution.sql` 是 `GLOB 'draw*'`,`46773fe6` 改成 `name = 'draw' OR name GLOB 'draw-VRI*'`。計劃第 22 行兩版相同,仍寫 draw。

## 2. 修補補上的幾條行為,筆記沒指出對應的測試,也沒有條款編號
severity: minor
blocking: 否
引句:「這三條與 draw 只認框架名稱,都是 2026-10-24 代碼審 r1 抓到、各有測試釘住。」
file: `docs/lumos-toolchain-knowledge/Projects/Android介面寫法分流_計劃.md:70`
歸因:有證據的修復回歸。這行是修補新增的。
- **場景**:三個月後的接手者想找「各有」的那幾支測試。
- **找不到的原因**:這行沒有 `[test:]`,條款也沒有 S13 之類的新編號。
- **查證**:`grep -rn receipt_rerun docs skills scripts/lumos` 沒有任何命中,「範本註解不能以分號結尾」這條規則的測試 `t_android_ui_attribution_receipt_rerun` 沒有任何筆記提到。
- **後果**:這條規則改了範本註解就會踩到,而筆記指不出該跑哪支測試。

## 3. 驗收紀錄的有效範圍寫「本次版本」,但分類規則在驗收後已經改了
severity: minor
blocking: 否
引句:「revalidate_when: 歸因查詢的分類規則改動、Compose 或 RecyclerView 升版改了區段名」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-23_Android介面寫法分流實驗室驗收.md:6`
歸因:有證據的修復回歸。修補改了 draw 的認法,沒更新這份紀錄。
- **場景**:這份紀錄的 `valid_under` 寫「歸因查詢範本本次版本」,但 `draw*` 縮成 `draw` 與 `draw-VRI*`,命中它自己的重驗條件。
- **兩版查證**:`git diff f96ffe70 46773fe6 -- docs/lumos-toolchain-knowledge/Verification` 沒有輸出,紀錄兩版相同,仍是 `status: pass`。
- **後果**:讀者會以為實驗室的 Compose +6793ms、XML +2298ms 等數字是用現行範本跑的。⚠ 我沒有真實 Trace,無法證明數字會變,只能說紀錄沒標明驗的是改前版本。

## 三問
**① 原問題的修復有行為證據嗎?**
- **有**:收據重跑那題,修前回 `BAD Q1`、rc=1,修後回 `OK` 與 0,詳見上面的實跑結果。
- **有**:`.sql` 用 `--` 認 SPDX 的守衛,`t_license_headers_travel_with_vendored_files` 8 個全過。案例檔說 `#` 寫法與拿掉行都會紅,我沒有重做這兩個破壞實驗。
- **有**:名稱 NULL 與子區段比父區段長取 0,對應的新測試都過。

**② 修補處的正常、錯誤與相鄰路徑還成立嗎?**
- 正常路徑、CRLF、一次貼兩條都成立。
- 相鄰的 `rerun.sh` 沒被改,`-k vendored` 全過。
- 唯一沒測到的相鄰路徑,是案例檔自己列的:沒有對 `.sh` 或 `.py` 拿掉 SPDX 再驗一次會紅。
- 一個小提醒:範本檔頭第 10 行「把 __PROCESS__ 換成…」也含佔位字。只換 SQL 本體那一處會留下 `__PROCESS__`,違反 `reference.md` 的「不要留在收據裡」。全部取代就沒事,所以我沒列成發現。
- 另一個 ⚠:skill 說 expect 的幀起點「取 triage 挑的那一幀」,但沒說要用查詢輸出的 `frame_ts`。如果 triage 給的是別的時間軸,鍵會對不上而回 BAD。

**③ 新發現的案例,修前修後各是什麼?**
- **發現 1**:修前修後同一狀態(WHY 行寫 draw);修後規則表已經改成框架 draw,所以兩處互相矛盾。
- **發現 2**:修前沒有這行,修後新增但缺測試指向。
- **發現 3**:修前紀錄與範本一致;修後範本改了、紀錄沒動。

總結:最高嚴重度 minor
