# r1 收貨紀錄(rN-intake.md 慣例首用;2026-08-25)

## 引句機械收貨
- s1/s2/s3:quote-check 對 r1-snapshot.md **全數錨定**(工具輸出留於 session;帳面 sha 見 canary-log r1 五筆)。
- arch #1(截為「…」)與 ext #3(截於「,各加開一輪 」):快照自身內文帶「」致截斷。機械重現:
  ```
  python3 归一化比對(去 *`空白「」,NFKC)r1-snapshot.md ∋
    「審查員輸出格式段加卷證規則兩句」→ HIT
    「首輪前掃固定清單加第四類」→ HIT
    「兩迴圈的 r1 carrier 皆因引句錨在審材外現碼觸發 disposal 閘 quote 關 FAIL,各加開一輪 delta 才過」→ HIT
  ```
  三句全中,兩席引句收貨成立。

## 佐證通道抽驗(編排者親驗的關鍵主張)
- s2「refcheck 只抽反引號 inline-code」:scripts/lumos:68 INLINE_CODE_RE 實讀屬實;s2 自帶雙格式實測(無反引號 0 抽取)。
- s2/s1「cascade 計劃首 commit 即 v2(折入前無 git 前版)」:`git log --diff-filter=A -- docs/lumos-toolchain-knowledge/Projects/連鎖佇列軟提醒_計劃.md` → 7a026ef,屬實。
- s3/s1 波及數字(16/59 vs 19/59 兩算法):收進 measurements.md,採「同案跨線」結論,未裁孰對——正是撤回理由本身。
- arch「[S6] 校準已跑、結論=2 條/300 字待下案」:2026-08-25_設計審收斂重定義落地.md:12 實讀屬實。
- s1「[S3] 目標句不在 Systems/design-loop」:grep「建議上修」該檔 0 命中、連鎖佇列軟提醒_計劃.md:67 命中,屬實。
