不對齊共 5 條,其中 major 1 條。這份審查只讀了檔案,沒有改任何東西。

被審材料(`/tmp/修補大小上限試行-r1.md`)我讀的是 S6 那一節;其餘各節只當上下文。repo 證據取自 `Word-wild-search-rst`。

**問 1:試行條款落點與既有試行結構一不一致**

大致一致,有兩處落點不齊。

- 一致的部分:S6 沿用「每個加碼段自帶 PRIOR-ART、RETIRE-IF、REVISIT」的做法,收尾日期也與既有 REVISIT 同為 2026-11-03。
  - file: `docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:42-44`(收斂性診斷那節的先例)
  - file: `docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:100-102`(改道那節的先例)
  - 依據是 `/tmp/修補大小上限試行-r1.md:58-62`。
- 沿用既有 intake、逐案紀錄和三輪上限,沒有新增命令或閘。
- 不齊處 A:S1–S5 都放在「範圍與條款」節(`/tmp/修補大小上限試行-r1.md:30-34`)。S6 卻編號接續,實際放在另一個日期標題節(`:46-50`)。要找「S1–S6 全部條款」得跨節找。
- 不齊處 B:`skills/lumos-code-loop/reference.md` 把新增的第 6 點插在第 5 點與那張 intake 表之間,前面多空一行。
  - 第 5 點原文被改成「本節末的表」,所以表還能對上。
  - 第 6 點與表無關,讀起來卻像歸它管。
  - file: `skills/lumos-code-loop/reference.md:131-133`
- 與既有規則重疊:同檔第 1 點已有「修復若擴成新格式、新狀態或另一套機制,先重估是否拆案……另列建議」。S6 又定了一套觸發條件(超過 100 行)和去處(另案或 Issue)。兩條沒有互相指到。
  - file: `skills/lumos-code-loop/reference.md:127`

**問 2:計數方法是不是另起一套**

是,而且這是本次唯一的 major。

- 現成的數法有三套:
  - 小改動閘的 `_sc_changed_files`,用 `git diff --numstat -z`、處理改名與二進位,並用 `_BOOKKEEPING_FILES` / `_BOOKKEEPING_DIRS` 排除簿記檔。
    - file: `scripts/lumos:8903-8941`
    - file: `scripts/lumos:29395-29418`
  - §3.1 第 2 步產生 `rN-repair.patch` 的固定命令。
    - file: `skills/lumos-design-loop/templates.md:208`
  - canary 的 `--scope-lines`,它數的是被審材料的行數,不是修補行數,不能直接拿來比。
    - file: `scripts/lumos:10668-10686`
- S6 沒沿用其中任何一套,另用手寫的 `git diff --numstat <上一輪凍結提交>`(工作樹對提交)。它宣稱「跟回放同一單位」,又說提交後 `rN-repair.patch` 的 `+` 行「是同一個數」。
- 驗證筆記的回放腳本是第四種數法:對兩輪的整分支快照 patch 做 `difflib.SequenceMatcher` 逐行比對,同內容的行扣掉。
  - file: `docs/lumos-toolchain-knowledge/Verification/2026-10-14_修補大小與下一輪major回放.md:86-100,140-143`
  - 它與 S6 的數法至少有三處不同:
    - 回放扣掉同內容行,numstat 不扣,搬動或重複的行會多算。
    - numstat 對工作樹只看已追蹤檔,新增的測試檔若還沒 `git add -N` 就漏數;回放與 repair.patch 都看得到。
    - repair.patch 帶 `-U10` 與 `+++` 檔頭,還含兩版之間全部已提交變動,如合併進來的主線改動;§3.1 第 2 步自己也寫「不是自動判出的只有修復」。
  - 這些差異讓「100 行門檻是用回放的單位校出來的」這個前提不成立。照字面做,門檻會用另一個單位去量。
  - 嚴重度:major,因為引入第二種數法,而且計劃對外宣稱兩者相同。
  - file: `/tmp/修補大小上限試行-r1.md:50`
- 次要:S6 的排除清單手寫成三項(`governance/review-reports/`、`governance/replay/`、`docs/.*-log.jsonl`),是 `_BOOKKEEPING_DIRS`(`governance/code-loop/` 等五個目錄)加 `_BOOKKEEPING_FILES`(如 `docs/.governance-log.jsonl`)的子集。
  - 例如 `governance/code-loop/` 下的檔照 S6 會被算進修補行數,照既有簿記慣例卻不算。
  - 嚴重度:minor,因為結構(用 numstat 加排除)是對的,只是排除清單另寫一份。
  - 應改為指向既有簿記排除集,或明寫「與小改動閘同一排除集」。

**問 3:回放腳本放在驗證筆記正文裡、不放進 repo 工具目錄,有沒有違反既有慣例**

有偏離,屬於 minor。

- 既有先例是把回放與分析腳本放進 `governance/eval/`(`k1_stop_replay.py`、`ledger_analysis.py`、`cd_fix.py`),圖譜節點只引用路徑。
  - file: `docs/lumos-toolchain-knowledge/Projects/panel收斂判準改革_計劃.md:21,29`
  - file: `docs/lumos-toolchain-knowledge/Projects/收斂機制優化調研2026-08-14.md:23,58`
- 驗證筆記內嵌程式碼的先例都只有 3 到 7 行的小片段(`2026-07-31_公開精簡版交付.md`、`2026-09-13_社群規則庫可行性實測.md`)。這份筆記內嵌約 110 行完整腳本,是第一例。
  - file: `docs/lumos-toolchain-knowledge/Verification/2026-10-14_修補大小與下一輪major回放.md:61-150`
- 後果:S6 的 REVISIT 要「用驗證筆記裡的回放腳本重算」,執行者得先從 markdown 把腳本抄出來。腳本沒有測試,也沒有 Systems 節點管它(專案鐵則 5 管的是程式檔,放進 `.md` 正文剛好繞開)。
  - 腳本的 `ROOT` 靠命令列參數、`SKIP` 又手寫一份,會跟前述簿記排除集再漂移。

**附帶一條不計入上面的條數**

`Systems/pitfalls-code-loop.md` 新增的 WHY 行寫「187 個有 major 的續輪只有 7 輪因此變乾淨」,驗證筆記寫的是「169 個、16 輪」。兩處數字對不上,是內容漂移,不是架構對齊問題,但會讓下一個讀者無從判斷哪個才對。
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:37`(新增的 WHY 行)
- file: `docs/lumos-toolchain-knowledge/Verification/2026-10-14_修補大小與下一輪major回放.md:17`

**不對齊清單**

1. major:S6 另起第四種數法,又聲稱與回放及 `rN-repair.patch` 是同一單位,實際不是(問 2)。
2. minor:S6 手寫排除清單,是既有 `_BOOKKEEPING_*` 的子集(問 2)。
3. minor:回放腳本內嵌在驗證筆記,偏離 `governance/eval/` 的先例(問 3)。
4. minor:S6 編號接續 S1–S5 卻放在另一節;`reference.md` 第 6 點插在第 5 點與其表之間(問 1)。
5. minor:`reference.md` 第 6 點與第 1 點對「修補擴大就拆」並存兩套觸發與去處,沒有互指(問 1)。

不對齊共 5 條,其中 major 1 條。
