# Unfamiliar-stack Invariant Brief pilot

This directory contains five synthetic, executable code-review cases. They test
whether a short, change-specific invariant brief helps a reviewer working in an
unfamiliar language. They are not evidence about production review quality.

Each case has a buggy and fixed source, a normal-path control, a hidden answer
key, and a brief assembled from existing Lumos idiom rule IDs. Qualification
must show this matrix before any model session:

| version | target scenario | normal scenario |
|---|---|---|
| buggy | non-zero for the intended defect | zero |
| fixed | zero | zero |

The answer keys and fixed sources are grader-only material. They must never be
listed in a model session's `materials` field.

## Qualification versions and dispatch boundary

qualification-v1 and its result receipt are immutable historical evidence.
Its U4 oracle checked concurrency but missed lost worker results; it is not a
complete S2 qualification. qualification-v2 replaces only U4 sources with
buggy-v2.js/fixed-v2.js, checking returned values, input order, empty input and
the concurrency bound. Other case hashes are unchanged, not newly rerun.

Before a formal run, each case must declare dispatch_common (a nonempty list
of frozen reviewer-safe paths) and dispatch_brief (one distinct frozen path).
Each session must exactly match common, plus the Brief only for the brief arm.
The allowlist needs independent S3 review: declaring a path does not prove its
content is answer-free. Qualification manifests intentionally lack dispatch
allowlists and sessions and cannot start a formal run.

## 選材與壓縮候選版

`candidates/v2/U1.json` 至 `U5.json` 是重新核對 idiom 原文後的候選
Brief，每案 1–2 條；最多 12 條是上限，不是需要湊滿的配額。
原本的 `cases/*/brief.json` 與 qualification-v1 凍結材料保持原樣。

選材理由（本節只供編輯者閱讀，不放入 reviewer 材料）：

- U1 保留 R7 的資源有效期間及 R6 的釋放責任；兩者分別檢查過早釋放與清理路徑。
- U2 把 R5 的重複提醒合併，另選實際存在的 controller 關閉責任 R6；移除未由 R5 原文充分支持的「所有 teardown 都必須 await」概括。
- U3 保留 R5；刪除 R2 的 UI／Task 擁有者延伸，案例未提供該生命週期。
- U4 保留 R2；刪除針對長活快取的 R10，避免把短期輸入集合當成長活集合。
- U5 保留 R22 的交易入口概念；刪除過寬的角色卡引用，原子性要求由兩組共用的任務契約提供。

每條只提供規則、適用結構與待查問題；不給缺陷位置或修法。容量、
結果先後與原子性等成功條件，必須放在兩組共用材料，不能藏在 Brief。
這些候選是本次 assistant 編輯結果，未另派 Astra 執行。

採用前須另做 S3 獨立洩題審查並升版凍結 manifest。編輯者已知五案
主題，不能自行宣告通過盲審；格式與來源 ID 核對不證明沒有語意洩題。
