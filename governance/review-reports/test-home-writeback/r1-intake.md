preflight-4: ran

# 收貨與處置

原八項宣告、七項blocking，以同段同因合併為四個不同問題；最高major，不降級原報告。

|ID|重現|結果|採信及處置|
|---|---|---|---|
|logic-F1|r1-intermediate-baseline-counter.json 的 middle-delete/rename：CLI home check --diff，三版 cat-file存在性false/true/false|HIT rc1|採信，逐group提交/父版合法測試分類補路由|
|boundary-F1|同一counter與_nodehome_required只掃side.files語意|HIT|與logic-F1同段同因，折入同一修訂|
|integration-F1|同一counter、content_notes own逐提交但reqB/N只有端點|HIT|與logic-F1合併，已折|
|resources-F1|同一counter；中間新增後刪除不在端點|HIT|與logic-F1合併，已折|
|rollback-F1|同一端點缺口及新增diff-double-rename兩次改名control|HIT|與logic-F1合併，已折|
|logic-F2|counter pure-test-other-home只改測試/寫Production正文rc0；原test-only寫TestHome無法殺誤啟動|HIT|採信，新增普通/-O pure-test-other-home反控制|
|resources-F2|新36方法shebang-index正/反把索引與工作樹首行設反向；舊碼20pass16fail具名日志|HIT|採信，新增两方向普通/-O控制，不宣稱候選已綠|
|resources-F3|_nodehome_required測試跳過在side.shebang讀取之前，_nodehome_reader不相同版本呼叫git show|HIT|採信，撤除無新程序宣稱並補1/10提交成本收據入口|

PF-1前掃：修改前_nodehome_required/side/route_groups → 修改後_nodehome_required/_nodehome_side/_nodehome_commit_groups與_nodehome_mark_note_content，AST名稱驗證HIT，非核心裁定。

收貨raw的missing均synthetic fixture路径，轉交canonical僅移除這些inline-code標記；原文/引句/等級未改，raw及格式收據保存；canonical三道全部通過，clean架構無引句按工具rc2格式保留。

鏡像raw clean確認四組問題已折；fold-check仍rc1 Project沒有summary，advisory非無提醒，未手改header。新紅36=20通過16失敗；原24=16/8不覆寫。正式CLI52仍未改。以上合成案例不代表真實審查輪數下降。
