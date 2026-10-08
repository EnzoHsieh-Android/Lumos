severity: minor

# 架構對齊席(sonnet)第 1 輪

## 三問

1 分層與順序:對齊。drift check 放在同一個 ref 迴圈內、code-loop check 之後,全套測試(迴圈外)之前,符合「便宜的先跑」(掛鉤自己的順序註解:code-loop 約 0.6 秒,全套 8 分鐘);rc 處理(0 放行、1 擋、其他放行)與 home check、note-shape 同型;刪除 ref 在迴圈頂端已 continue,不會走到。CI 端與 code-loop gate、note-shape 兩步同型(push 事件才跑、BEFORE 補 40 個 0、rc1 才 exit 1、其餘原樣回傳)。輕微不齊:範圍算法(F1)、CI 步驟借用前一步環境(F2)、順序註解表沒補這道最壞 60 秒(F3)。
file: `scripts/hooks/pre-push:261-265`(閘順序與耗時註解)、`scripts/hooks/pre-push:341-351`(note-shape 的 rc 處理)、`.github/workflows/ci.yml:110-124`(code-loop gate 步驟形狀)

2 命名、錯誤處理、訊息:對齊。變數 dr_rc 與 nh_rc / ns_rc / cl_rc 同一命名族;先 rc=0 再 `|| x_rc=$?`;擋下訊息用「逃生:…」開頭、寫明略過環境變數與 config 的 gate 設 warn,與 home、note-shape 兩段同一句式;CI 的 `::error::` 訊息同 note-shape 步驟寫法。測試用 `t_prepush_...` 命名、`check("①…")` 編號式、真的跑那支掛鉤,與 t_prepush_runs_home_check 同一路線(drift 那支改成轉給真 lumos,是為了驗真實 rc,不算第二種做法)。
file: `scripts/hooks/pre-push:331-351`、`scripts/test_lumos.py:43957-44012`

3 第二種做法:沒有引入第二種機制(沒有另起暫存檔、沒有自己算 rc 映射、沒有跨層直呼內部函式)。唯一接近的是掛鉤內第三種範圍算法(F1),但註解有講理由,標 minor。

## F1 掛鉤內出現第三種範圍算法,且跟同一支掛鉤裡 home/note-shape 的 _hrange 不同
severity: minor
blocking: 否
引句:「"$PY" "$GRAPHCTL" drift check --diff "$_rsha..$_lsha" --repo "$REPO_ROOT" || dr_rc=$?」
file: `scripts/hooks/pre-push:308-352`(同迴圈裡 _range 與 _hrange 兩套已存在,並有註解「別把兩套合併成一套」)
1. 同一個迴圈裡已有 `_range`(空樹兜底)與 `_hrange`(不在遠端的最早提交的上一個)兩套;drift 直接吃原樣 `_rsha.._lsha`,新分支時就是 `000…0..sha`。
2. 作者的理由(把明寫的空樹當「從空樹比、截到上線點」會誤擋)成立,且 CI 端 note-shape 也是原樣交出去;但同一支掛鉤裡 note-shape 是吃 `_hrange`,drift 卻吃原樣——同一類「lumos 會截上線點的擋」在掛鉤與 CI 兩處的傳法不一致,而掛鉤的 note-shape 是用 `_hrange`、CI 的 note-shape 是原樣,drift 兩邊都原樣。
3. 結構上對(沒有自己重寫推導,是交給 lumos 的共用判法);⚠ 判不準是否該共用 `_hrange`:若 lumos 對 `000…0..sha` 的分岔點判法與 `_hrange` 結果不同,同一次推送兩道閘看的範圍會不同。未能重現。

## F2 CI 這步靠前一步 note-shape 做的 fetch 與本地 main,不自足
severity: minor
blocking: 否
引句:「放在 note-shape 這步後面是借它 fetch 好的遠端分支與本地 main」
file: `.github/workflows/ci.yml:128-141`(note-shape 步驟才做 git fetch 與建本地 main;code-loop gate 步驟不依賴別步)
1. 既有 lumos 步驟(code-loop gate、note-shape)各自帶齊自己要的環境;這步把 fetch 責任外包給相鄰步驟。
2. 場景:哪天有人把 note-shape 步驟搬走、拿掉或改條件(例如 if 條件不同),drift 步驟不會紅只會在 lumos 判不出主線時退化(或放行),沒有機械守衛。測試 ⑦ 只驗順序在 code-loop 之後,沒驗跟在 note-shape 之後。
3. 影響小(作者已在註解講明),標 minor;⚠ lumos 對「找不到主線」的退化是放行還是全掃,沒逐行驗。

## F3 順序註解的耗時清單沒補這道最壞 60 秒
severity: minor
blocking: 否
引句:「這道最壞 60 秒、全套 8 分鐘,便宜的先跑」
file: `scripts/hooks/pre-push:261-265`(「所有閘加起來約 13 秒」的清單;新閘的最壞 60 秒與它矛盾,但清單沒更新)
1. 掛鉤自己的閘順序註解寫「除全套外所有閘加起來約 13 秒」,新閘註解自承最壞 60 秒,而且它排在同迴圈後面的 bound_tests_advisory 與迴圈外的自主迴圈那支(約 10 秒)之前。
2. 內部不一致:一處說全部 13 秒,一處說這道最壞 60 秒;「便宜的先跑」若嚴格照耗時,10 秒那支應排在它前面。作者依據是計劃書指定位置,順序本身可接受;只是註解表沒同步。

## 圖譜鏡頭
本席職責為架構對齊;圖譜鏡頭逐條判定不在本席範圍,未做。

不對齊共 3 條,其中 major 0 條

最高等級:minor
