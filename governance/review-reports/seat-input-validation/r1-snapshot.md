---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
  - risk/守衛面
lands_in:
  - Systems/lumos-cli-read
---
# 異常派工單回報輸入錯誤_計劃

白話：先確認拿到的是一張可讀的派工單，再對照審查報告。格式錯誤應明講哪個欄位錯，避免工具崩潰被誤判成審查內容有問題。

WHY:最小修正在 cmd_seat_check 的既有讀取邊界，只補資料形態檢查，不另建 schema 引擎或收貨閘 [出處:2026-10-06 seat-shape-probe 原版 CLI 最小重現] [因:先排除壞材料引起的錯誤診斷]

PRIOR-ART:Python 官方 JSON 文件說明解析成功可能得到 list、None、布林或數值，JSONDecodeError 只代表語法壞；JSON Schema 的 object／array 與 items 分工提供同等型別判準。借其設計，沿用 isinstance 與 ValueError，零依賴實作。https://docs.python.org/3/library/json.html https://json-schema.org/understanding-json-schema/reference/object https://json-schema.org/understanding-json-schema/reference/array

RETIRE-IF:CLI 共用讀取入口提供同等物件與 materials 路徑清單驗證、且本案反例全由該入口守住時，撤掉局部檢查，避免兩套並存。

## 現場與重現

固定來源為引用行號修復分支的功能加帳本版本 f05c473cd5237395ea9691fbf4b3424a060d0f3a；本案位於另一個隔離分支。原始重現保存在 governance/review-reports/seat-input-validation/repro.json。

合法 JSON 的 []／null 派工單，原 CLI 在 .get 拋 AttributeError；materials 含物件時，原 CLI 在 Path 拋 TypeError，回 1 並輸出 traceback，而不是既有壞輸入的 rc2 診斷。非空物件 materials 被 assert 擋，-O 會移除 assert，需用實際 CLI 對照。

涉及 `scripts/lumos` 的 cmd_seat_check 與 `scripts/test_lumos.py` 的席位對帳測試。既有規格 [[Projects/驗證層自證三件_計劃]] 的 S1 對合法材料只觀測，空材料可豁免；不把 unreported 當未閱讀證明。

## 核心裁定

1. 在 .get 與 Path 前驗 JSON 頂層必須是 dict；只接受缺省／null／清單型 materials，每項必須是非空且不含 NUL 的字串。以具體欄位的 ValueError 進既有 rc2 分支，不捕獲所有例外。
2. 缺省、null 與 [] 保留 vacuous rc0；未知欄位以及 round、seat、lens 的既有輸出不收窄。合法材料漏報／越界仍 rc0，JSON 與帳本欄位不變。
3. 全部資料形態驗完才讀材料或寫越界帳；不改報告、派工單、主線來源或使用者配置。
4. 不做多席派工包自動選席，不驗材料業務語意，不把文字提及當實際閱讀證明，不讓觀測結果變成推送閘。

## 驗收條款

- [S1] 當派工單解析成非物件或 materials 不是缺省、null、清單時，席位對帳應回 rc2、輸出輸入診斷且不輸出 traceback 或觀測 JSON。[test:t_s1_seat_check_bad_dispatch]
- [S2] 當 materials 含非字串、空字串、NUL 字串或有效路徑後跟錯項時，席位對帳應在寫越界帳前回 rc2；普通與 -O CLI 保持一致。[test:t_s1_seat_check_bad_dispatch,t_s1_seat_check_preflight_order]
- [S3] 當 materials 缺省、null 或空清單時，席位對帳應保持 rc0 與 vacuous；中文含空白的有效路徑仍能錨定引句。[test:t_s1_seat_check_valid_dispatch]
- [S4] 當合法材料清單的報告漏提材料或引句出界時，席位對帳應保持 rc0，並依既有格式記錄越界帳，不新增阻擋語意。[test:t_s1_seat_check_valid_dispatch]

## 實務隱患

- 守衛面：錯形態不能當有效空清單豁免。普通與 -O 都真跑，不用 assert 當正式輸入驗證。Python 官方 -O 說明：https://docs.python.org/3/using/cmdline.html#cmdoption-O
- 相容性：明確保留缺省／null 空材料；不限制未知欄位、元資料與有效路徑內容，不增相對路徑基底推斷或多席包拆解。
- 已排除:金流:只讀審查材料，不操作帳務。
- 已排除:對外送出:不發送外部訊息。
- 已排除:不可逆:錯輸入在既有越界帳 append 前回錯，不涉及資料遷移。
- 資源與效能：局部資料形態掃描一次，無新依賴、無網路、無常駐工作；測試沿用私有臨時 vault，子程序設有限逾時。
- 射程：只證明錯輸入能清楚回報，不證明多席材料範圍正確或實務審查輪數下降。
REVISIT:2026-10-20 抽查十次實際收貨，統計 malformed 派工單與格式錯誤被誤作內容問題的事件；依實際事件決定是否另外改善派工包使用方式。

## 回退

回退本功能提交即恢復原讀取，保留原始重現與紅綠卷證。沒有資料遷移、全域設定或新背景工作。

## 審計修正紀錄

前掃提出 PF1、PF2 的語意背書問題，核心裁定原文保留，交正式席覆核。原始報告保存在 preflight-raw.md，不改等級或引句。

- PF1：原測試只查「擋下:」，不足以證明欄位診斷；補 dispatch／materials／materials[項次] 明確預期。泛稱 bad dispatch 不算通過。
- PF2：原測試只查帳本未寫，不足以證明首份材料尚未讀；補直接執行真 cmd_seat_check AST、用標準函式庫觀測 read_text 的普通與最佳化對照。以有效首項跟錯形態尾項證明讀到派工單、未讀材料；不用會阻塞的命名管道。
- 這些是既有裁定的測試背書修正，生產函式仍待正式設計審放行才修改。正式席可推翻前掃判準。
