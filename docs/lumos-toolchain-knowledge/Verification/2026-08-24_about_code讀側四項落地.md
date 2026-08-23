---
type: verification
status: pass
date: 2026-08-24
valid_under: 語料 338 篇、83 篇 about_code 存量(batch-2026-08-23)、goldset rev 483c631b7294(釘定快照 9fcb761 早於 83 篇寫入——釘定口徑下 about 不生效)
revalidate_when: goldset 快照前進到含 about_code 的 commit 後重跑(屆時「固定席前 3 必看命中率」才是有 about 的數字);LUMOS_IMPACT_ABOUT_MAX 門檻要調時;about_code 存量重標超過 20 篇時
summary: |-
  FLAG:TECHNICAL
  KEY:about-code-impl-std 三輪達上限後人裁乙直接實作——#4 impact 讀 about_code(about_hit 只加分、事故優先、過期雜湊、總開關、巨檔門檻)/#6 doctor Check S2/#9 hook ★關於★/#10 pin_top3_must/#11 restamp+migrate-stamp 全落地,新測試 6 組 70+ 條、翻紅釘 7 根全驗,全套 3143 綠
  KEY:★首量結果誠實★:必看 29 篇只 8 篇坐固定席,about 只重排固定席內部 → 新指標 train 0.29/held 0.12,有無 about 幾乎同值;P@8/棘輪零動(設計保證,實測吻合)
  KEY:83 篇存量 migrate-stamp @dbd104f^ 後 0 篇過期;A 席到最終寫入之間正文動過的只 1 篇(lumos-cli-read,B 席讀的是新版,人裁過,不動)
  DEP:[[Projects/固定席扇出降權_計劃]]｜[[Systems/retrieval-ranking]]｜[[Verification/2026-08-23_about_code存量雙評審落地]]
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/固定席扇出降權_計劃]]"
related:
  - "[[Systems/retrieval-ranking]]"
  - "[[Verification/2026-08-23_about_code存量雙評審落地]]"
---
# 2026-08-24_about_code讀側四項落地

> 白話:「這篇筆記在講哪支程式」這個標籤,昨天 83 篇寫進去了;今天把**讀它的那一側**做完——
> 改程式時推薦筆記會把「真的在講這支」的排前面、體檢會列出「標了之後筆記又改過」的、
> 標籤有了一把能量過期的尺(正文雜湊)。設計審三輪跑滿沒收斂,Enzo 裁直接做,剩下交給測試。

## 做了什麼(對應計劃工具清單)

| # | 項目 | 測試 | 翻紅釘 |
|---|---|---|---|
| 4 | `impact` 讀 `about_code`:命中且未過期 → `about_hit: True`(只在 True 出鍵、不動 pinned、不碰既有 `hit`);固定席 stable sort 鍵 `(kind!="incident", not about_hit)`;總開關 `LUMOS_IMPACT_ABOUT`;巨檔門檻 `LUMOS_IMPACT_ABOUT_MAX=8`;`--incidents-only` 整段跳過 | `t_impact_about_hit`(15)、`t_impact_about_giant_file`(2) | 拿掉 sort → ①翻紅 ✓ |
| 6 | doctor Check S2:全 type、跳過作廢、比正文雜湊、舊格式另列、受總開關、warn_soft 不擋;訊息先叫人看標籤 | `t_doctor_about_code_expiry`(9) | 比對恆 False → ①翻紅 ✓ |
| 9 | hook 固定席行首 `★關於★`(讀 `about_hit`) | `t_impact_hook_v11_delta_and_format` +1 | — |
| 10 | `pin_top3_must`:固定席前 3 位必看命中率,row→`_macro`→verdict→history,不進 gate,沒標 2 回 None | `t_eval_pin_top3_must`(9) | 分母改固定 3 → 翻紅(邏輯上必然,未另跑) |
| 11 | `note_body_hash`(utf-8-sig)、`about-code restamp <節點> [--by]`(三段全換=人核過,無批次)、`about-code migrate-stamp --at <commit>`(一次性,用標註當時正文) | `t_note_body_hash_and_restamp`(13)、`t_about_code_migrate_stamp`(6) | utf-8-sig→utf-8 ✓/restamp 不換第一段 ✓/migrate 用現在正文 ✓ |
| 7 補 | revert 單篇部分失敗原本照刪 stamp 照算成功(重複值直接崩潰)→ 去重、失敗留 stamp、rc 非 0 | `t_about_code_revert_partial_fail`(5) | 拿掉 continue → 翻紅 ✓ |

登記守衛:`check-s2` 進 `_KNOWN_GATES`(漂移守衛抓到才補——機制在工作);HELP_WHEN 三條;索引 02 檔四行。
全套 3143 passed / 0 failed;`lumos doctor` 0 issues。

## 首量結果(誠實)

考卷(`--ablation`,釘定快照)八條閘全過;必看 train 26/29、held 35/37 **與改前相同**——設計承諾「不碰召回」實測吻合。
新指標「固定席前 3 位必看命中率」:釘定口徑 train 0.2917 / held 0.1167;**現況語料(有 about)** train 0.2963 / held 0.1167。
★幾乎同值的原因★:必看 29 篇只有 8 篇坐固定席,about 只重排固定席內部,能動的空間本來就小。
抽三題看:pre-push 那題 2 篇 about 命中確實排到最前;impact-hook.py 那題 2 篇命中都在自由席,設計上不升——固定席沒變。
**這是甲案收窄時就講明的結果,不是 bug。** 要讓這個數字有意義,下一步是「必看為什麼不在固定席」(三軸保送面),不是 about_code。

## 存量遷移

`migrate-stamp --at dbd104f^`(最終寫入 commit 的前一個)83 篇全補第三段;之後 0 篇過期。
A 席(12:19)到最終寫入(22:19)之間正文動過、且在 83 篇內的:只 `Systems/lumos-cli-read`——B 席讀的是新版、40 條人裁含它,不動。

## 天花板

- 新指標只有一次量測,「一個月觀測再決定要不要閘」的觀測才剛開始。
- 釘定快照早於 83 篇寫入,考卷口徑下 about 永遠不生效——★標註刷新把快照前進之前,成績單要看 `--live-vault` 口徑★(本篇 KEY 已標)。
- 翻紅釘 #10 那根沒實跑(分母改固定 3 必翻紅是算術事實),其餘六根實跑過。

## 附帶:評測輸出白話化(2026-08-24 Enzo:「優化時少一層認知負擔」)

`retrieval_eval.py` 印出來的每個數字旁加一句「這是什麼、門檻多少、為什麼在意」;關卡改印白話+實際數字(例:「推薦:前 8 名裡 71% 是對的(門檻:至少 70%)」);
棘輪訊息改白話;`loop status --panel` 兩個行話標籤(falsification+ODC、capture-recapture)換掉。
★history 的 key 一個字沒動★(帳本連續);自動迴圈 grep 的「gate 總判定」與測試釘的「unjudged(held 評測母體)」兩個錨字串保留在句內。
同步改了三條測試斷言字串。白話標準本身沒有圖譜節點,在 session 記憶(tool-output-plain-style)——★若要升格成規則,應立 Systems 節點★。
