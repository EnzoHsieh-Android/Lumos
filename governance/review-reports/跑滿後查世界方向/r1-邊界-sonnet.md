severity: major

邊界席報告:跑滿後查世界方向 r1(`world_check` 欄的極端輸入)。對照的程式碼在 `/Users/enzo/harness/lumos-cap-world-check`。我匯入 `scripts/lumos` 實測過 `_loop_ts_key`、`_real_chars` 和 `_cap_retro_check`。實驗暫存已用字面絕對路徑刪除。

## 逐條 finding

1. queries 的規則在「做法」與「驗收條款」兩處寫得不一樣。做法第 2 點(spec 第 55 行)說「每條」都要至少 4 個字。S2(第 73 行)卻說「沒有一條夠 4 個字」才判不過。
   - 重現:`queries: ["正常的查詢詞組", ""]`(或加一條 `"。。。"`)。照做法會判不過,照 S2 的字面(沒有一條夠)會放行。
   - 綁測試的是 S2 這句,所以測試不會釘住「每條」。實作者照哪邊寫,測試都綠。
   - 模板預設是 `[""]`,作者多加一行忘了刪空字串,就剛好落在兩種讀法之間。
   - 引句:「queries 沒有一條夠 4 個字」
severity: major
   - blocking: 是,條款與做法互相矛盾,而這條條款正是拿來綁測試的。

2. 人裁 `ts` 不是字串時,spec 說「當成生效日之後」,但函式會丟例外。
   - 重現:治理帳一列 cap-decision 寫成 `"ts": 1730000000`(數字、清單、`true` 都一樣),回顧是 version 1、人裁是 extra-round。
   - 實測 `_loop_ts_key(1730000000)` 丟 `AttributeError: 'int' object has no attribute 'replace'`。該函式只攔 `ValueError`。
   - 沒帶時區、空字串、`None`、只有日期、前面有空白,這幾種都回 `None`,spec 的說法成立。
   - `_cap_retro_check` 被 `_cap_retro_status` 呼叫,`canary record`、處置閘、doctor 都走這條路。帳上一列怪值就會讓整條閘丟堆疊,違反該函式說明寫的「壞檔一律判不合格並講原因,不丟堆疊」。
   - 正常寫入端一定寫字串;實際帳上 99 筆 cap-decision 全都解得開。所以只有手改過帳才會踩到。
   - 引句:「`ts` 解不開當成生效日之後」
   - file: `scripts/lumos:19357`(`_loop_ts_key`);呼叫路徑 `scripts/lumos:22399`(`_cap_retro_check`)。
severity: minor
   - blocking: 否,要手改過帳才踩得到,但 spec 要註明先判型別再呼叫。

3. 網址的判法是字面比對,「至少兩個來源」可以被不同寫法的同一個網址湊出來。
   - 開頭只收小寫 `http://`、`https://`,沒說要不要去頭尾空白、要不要忽略大小寫。
   - `HTTPS://example.com` 與 `" https://x"`(前面有空白)會被擋,雖然網址本身合法。
   - `javascript:` 會被擋,這是對的。
   - 只有 `https://` 或 `http://` 的會放行。
   - `https://a.com/x`、`https://a.com/x/`、`https://A.com/x` 三項互不相同,所以同一頁寫兩次(有無結尾斜線)就算兩個來源。
   - `verdict` 同理:`Direction-OK` 或尾巴帶換行會被擋,但 spec 沒說這是故意嚴格。
   - 引句:「兩項的 `url` 不能相同」
severity: minor
   - blocking: 否,不是有意偽造,是「正常人兩次貼同一頁」就會誤算。spec 的「不做」節只免了偽造防護,沒免這個。

4. 驗收條款沒說接受風險時,`world_check` 為 `null`、`{}`、`[]`、字串,或 source 缺 `point` 鍵時算空骨架還是型別錯。
   - 空骨架的定義是「全是空字串」,但缺鍵或 `null` 不是 `""`。
   - 能產生 `null` 的工具(Python 與 JS 序列化)很常見。`data.get("world_check")` 也分不出 `null` 與缺鍵。
   - 第 54 行「先驗型別」是寫在 extra-round 底下,accept-risk 要不要先驗型別沒交代。
   - 引句:「最新一筆人裁是 accept-risk 時:`world_check` 可以是空骨架或省略;有填就照上面驗(填一半算錯)」
severity: minor
   - blocking: 否,邊界未定義;實作時各猜一邊,S3 的測試只釘兩個典型輸入。

5. `--record` 的提醒不分人裁種類,accept-risk 會印出不對的話。
   - 重現:最新人裁是 accept-risk,`world_check` 有填且 `verdict: change-direction`,`--record` 成功後印出「加開前先跟人確認新方向,別照原方向直接派下一輪」。但這時已經選了不加開,沒有下一輪可派。
   - S5 也沒限定人裁種類,測試不會抓到。
   - 引句:「世界查證認為要換方向:加開前先跟人確認新方向,別照原方向直接派下一輪」
severity: minor
   - blocking: 否,只多印一行,不擋;但文字對 accept-risk 是錯的。

6. 時間常數與測試夾具會讓 S4 的測試隨日期翻紅或翻綠。
   - 夾具 `_cr_decide`(`scripts/test_lumos.py:103441`)呼叫真的 `cap-decision` 指令,事件的 `ts` 是 `datetime.now()`(`scripts/lumos:1598`)。
   - 合併當天 now 小於生效日(隔天零點)。想測「version 1 加 extra-round 要擋」,用預設夾具會在當天紅、隔天才綠。想測「舊格式照舊過」,用預設夾具則是當天綠、隔天紅。
   - spec 第 6 點寫的是「時間用現在」,沒說 S4 兩支測試要直接寫帳上的 `ts`(例如剛好等於常數、早一秒)。
   - 剛好等於生效日:`_loop_ts_key` 實測相等,「不早於就擋」的比較要用 `>=`。spec 沒有把這個邊界列進 S4。
   - 引句:「`_cr_decide` 預設 extra-round 而且時間用現在」
severity: minor
   - blocking: 否,推送前閘本機就會看到紅,不會漏進主線;但測試設計要明講。

7. 手冊同步點的清單比被引用的〈五〉少兩處,而且「同一句」搜不到全部。
   - 審查跑滿回顧計劃〈五〉(該計劃第 144 行)列的是六處:
     - design-loop SKILL.md;
     - design-loop reference.md 兩處;
     - code-loop SKILL.md;
     - code-loop reference.md;
     - `skills/lumos-project-notes/commands/05-設計審查迴圈.md:33`。
   - 本 spec 第 59 行只點了前五處,漏掉指令速查 `05-設計審查迴圈.md:33` 的「跑滿上限還沒過 → 停,攤給人裁」。
   - 實作時另找到的 code-loop reference.md 的另一句(第 245 行「到頂還沒收斂就停」)也沒點。
   - design-loop reference.md 的兩處措辭也不同:第 332 行是「到頂仍未收斂」,只有第 542 行是「到頂沒過」。用「同一句」去搜會漏第 332 行。
   - 後果:AI 平常查的是指令速查,漏掉它,「查 → 攤人裁」那步在速查裡不存在。
   - 引句:「還在 lumos-design-loop 的 reference.md 兩處與 lumos-code-loop 的 reference.md 一處」
severity: minor
   - blocking: 否,保底的 `world_check` 仍由工具擋;但清單要補齊並用實際行號列出。

8. 回顧檔很大時,問題清單沒有上限。⚠ 去重演算法沒寫。
   - 回顧檔上限是 256KB(`_RETRO_MAX_BYTES`,`scripts/lumos:22123`)。
   - 我用現有欄位(60000 個壞項的 `families` 加 1000 個壞的 `changes`,183KB)實測,`_cap_retro_check` 回 61002 條問題,共 3.2MB,耗時 0.02 秒。`cmd_loop_retro` 全部逐條印出(`scripts/lumos:22963` 一帶)。
   - `sources` 一項最小約 22 位元組,256KB 約可放 11000 項,每項最多 2 到 3 條訊息,同樣不封頂。
   - 「兩項網址不能相同」若用清單掃描比對,約 11000 項會是約 6000 萬次比較。spec 沒說用集合,所以我判不準 ⚠。
   - 引句:「不合的逐欄列出,跟既有欄位同一種列法」
severity: minor
   - blocking: 否,速度本身不是問題,只是終端洗版;沿用既有欄位的同一習慣。

## 實測確認沒問題的項目

- queries 是一條全標點:`_real_chars("。。。。")` 為 0,會被擋。
- 字數剛好卡線:`point` 10 字、`note` 20 字、queries 4 字,spec 都寫「至少」,卡線算過,沒有歧義。
- 表情符號不算字,數字與全形字母都算一字。
- 現有 `version` 檢查(`scripts/lumos:22418` 一帶)已排除 `bool` 並要求 `int`。`"2"` 字串、`2.0`、`true` 都會被擋。前提是實作時保留這段型別判斷,spec 沒重述,但寫的是「照舊擋」。
- 人裁 `ts` 的邊界(`_loop_ts_key` 實測):
  - 剛好等於 `2026-11-05T00:00:00+08:00` 與 `2026-11-04T16:00:00Z` 數值相同。
  - 沒時區與只有日期回 `None`。
  - 未來時間正常比較。
- 舊格式不追溯:實際帳上 99 筆 cap-decision 全部解得開,沒有因為「解不開當成之後」而讓已記回顧被誤判過期。

## 實務隱患逐類

- 併發:無新風險。`--record` 用同一份位元組驗證並算指紋(`scripts/lumos:22288`)。人裁在 `--check` 與 `--record` 之間被改,`_cap_retro_status` 會用最新人裁重驗,不過就標「過期」(`scripts/lumos:22570`),寧擋不放。
- 效能:見第 8 條。256KB 上限已擋住讀檔成本,風險只在輸出量與去重寫法。
- 資源:無,工具不上網也不新增檔案。
- 回滾:spec 第 80 行的回退寫法夠用。只有一個缺口,spec 沒提:別台機器若還跑舊版 `lumos`,會把 version 2 回顧判成「version 要是 1」而擋住 `canary record`。推廣版本時要同步,否則回顧檔本身沒問題也會被擋。這項我沒實測 ⚠。
- 金流、對外送出、不可逆:同意 spec 的「已排除」。
- 圖譜附帶節點 `Systems/loop-retro` 帶 0 條合約行,只有 PITFALL 與 WHY。沒有合約可破壞。節點裡「讀回顧檔不要求是自己的檔」「提示只由 `_cap_retro_fix_cmd` 決定」兩條,不受這份 spec 影響:它只在 `_cap_retro_check` 多驗一欄,沒碰讀檔或提示的決定函式。

最嚴重 severity: major,blocking 1 條(第 1 條),其餘 7 條 minor、blocking 否。
