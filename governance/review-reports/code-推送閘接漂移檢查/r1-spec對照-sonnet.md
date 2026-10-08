severity: minor

# spec對照-sonnet 第 1 輪

## F1 CI 那一步排在全套測試之後,字面沒照 [S18]
severity: minor
blocking: 否
引句:「全套測試在這步前面(既有安排,沒搬):推送前掛鉤排序是為了便宜的先擋、人不用白等全套;CI 是推上去之後的後盾」
佐證:file: `.github/workflows/ci.yml:55`(Full test suite 在第 55 行,drift check 在第 149 行,兩者都在同一 job 裡)
1. spec [S18] 原文:「推送前掛鉤與工具鏈 CI 應呼叫 drift check 並排在 code-loop check 之後、全套測試之前」。CI 這步在 code-loop gate、note-shape 之後(合規),但在 Full test suite 之後(不合)。
2. 綁定測試 t_prepush_and_ci_wire_drift_check 的 ⑦ 只驗「CI 排在 code-loop gate 之後」,沒驗「在全套測試之前」,所以偏離沒被測試抓到。
3. 作者已在 ci.yml 註解與計劃裡承認偏離,不是漏做;但 spec 條款本身沒被改寫成「掛鉤在全套前、CI 只要在 code-loop 後」。

## 逐條對照

### 〈做法〉第 4 節第 4 點
- 接線位置:掛鉤「排在 code-loop check 之後、全套測試之前」:已實作。pre-push 插在 bound_tests_advisory 之後、合約測試閘與全套(約第 540 行起)之前;測試 ①④⑤ 用假 lumos 記錄驗了 code-loop < drift < SUITE 的先後。
- 接線位置:CI:縮水(見 F1,只滿足「code-loop 之後」)。
- 預設模式「三條全過才 block,任一沒過先 warn、攤給 Enzo 裁」:已實作。diff 沒動預設值,掛鉤與 CI 都寫「沒寫=warn」,測試 ⑥ 驗沒寫設定不擋;計劃補一行「2026-09-30 已接線(warn),門檻量測另行」。〈考試結果〉門檻②在工具鏈上還沒量(計劃自己寫「要等那時再量」),所以維持 warn 與 spec「任一沒過先 warn」一致。⚠ 「攤給 Enzo 裁」這個動作 diff 裡看不出已發生,只有「另行」二字,不算違反。
- 三條門檻本身(①②③):不在這次 diff 的範圍(屬量測),diff 沒有多做也沒有替它們下結論。

### [S1]
- gate 模式 block/warn/off:已實作(掛鉤只看 rc==1 才擋,模式由工具讀設定;測試 ①⑤⑥ 三種都驗)。
- 範圍:已實作(見下「刻意偏離」)。
- 略過開關 LUMOS_SKIP_DRIFT_CHECK=1:已實作(掛鉤不攔截、交給工具記 skipped-env;測試 ④ 驗放行且照跑全套)。設成別的值不算,是工具端 `== "1"`,掛鉤沒改。
- 淺層 clone 跳過記帳:已實作,由工具端負責,掛鉤未干預。
- 上線標記:已實作。掛鉤新增獨立一行 `# lumos drift check`,測試 ⑥ 驗該行存在。

### [S18]
- 接線那一條:掛鉤已實作、CI 縮水(F1)。

## 刻意偏離兩處的判斷
1. 範圍改成遠端舊值..本地新值原樣交工具,不用掛鉤的 _range:不違反 spec 字面。〈共用〉指令段寫的是 `--diff <起點>..<終點>`,起點「照 `_lens_push_base`」再截到上線點,也就是起點該由工具算;掛鉤原樣交出 remote_sha..local_sha 正好讓工具做這件事。若照 _range 做,新分支或找不到起點時 _range 變空樹,diff 註解說會把主線上線後別人的轉正算進來而誤擋,這對 spec「只評估這次推送可能改變結果的行」反而是違反。結論:照現況比照 spec 字面更好。⚠ 工具端對 40 個 0 的處理沒在 diff 內(屬既有的 `_lens_push_base`),本席未逐行驗。
2. CI 排在全套之後:違反 spec 字面,見 F1。照字面做要把 drift check 與 code-loop gate 都搬到全套測試前(因為 spec 同時要求排在 code-loop 之後),等於動兩個既有步驟。CI 是推上去後的後盾,任一步紅整個 job 就紅,順序不影響擋不擋,只影響全套先紅時這步有沒有跑到。照字面做的好處很小,建議改 spec 措辭(掛鉤與 CI 分開寫),不必搬步驟。

## 多做(diff 中無 spec 對應的行為)
- 掛鉤 rc 非 0 非 1(參數錯)一律放行,不擋(spec 只定義工具回 2,沒定義掛鉤怎麼處理)。
- 掛鉤對 tag 也跑(註解:「分支與 tag 都查」),spec 未限定。
- CI 那步只在 push 事件跑、before 空補 40 個 0、rc 2 照實回報:spec 未寫細節,屬實作補洞。
- 掛鉤擋下時多印一段逃生說明;CI 印 ::error:: 說明。
- 動了 governance/anchor-baseline.json 與 Systems/bound-tests-gate、Systems/存量漂移守衛的筆記(治理與落點,非行為變更)。

## 四類清單
- 已實作:掛鉤位置(code-loop 後、全套前)、預設 warn、gate 三模式、範圍(改為工具算起點)、略過開關、淺層 clone(工具端)、上線標記、CI 呼叫 drift check 且在 code-loop 之後。
- 縮水:CI 排在全套測試之後(F1)。
- 多做:見上節。
- 未實作:無。

縮水+未實作共 1 條

最高等級:minor
