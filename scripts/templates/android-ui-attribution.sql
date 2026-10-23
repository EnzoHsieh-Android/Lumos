-- SPDX-FileCopyrightText: 2026 Enzo Hsieh
-- SPDX-License-Identifier: MIT
--
-- 每一幀 App 主執行緒的時間拆成四類,給 lumos-android-evidence 的 L1 用:
--   compose  Compose 自己打的區段(重組、Compose 的排版、清單預先組合,開了 composition tracing 時還有函式區段)
--   xml      只有 XML 寫法才有的元件區段(inflate、清單綁定列,RecyclerView 與 ListView)
--   pipeline 兩種寫法共用的畫面管線(input、animation、traversal、measure、layout、框架的 draw 與 draw-VRI…):Compose 畫面也掛在 View 系統上跑,
--            Compose 的繪製沒有自己的區段,所以這類不能算成 XML
--   other    以上都不是、祖先也都不是(doFrame 本身、排 vsync 等)
-- 用法:把 __PROCESS__ 換成 App 的行程名(套件名),交給 trace_processor 跑;複製進收據的 queries.sql 時,上面加一行
--   -- [Qn] session=<名> trace=<artifact id> requires=- expect=f<幀起點>:compose_ns=<值>
--   第一欄 frame 是「f 接幀起點」的字串:重跑腳本拿第一欄當鍵,純數字的鍵會誤判(見 skill 的 reference.md)。
-- 規則(單源 Projects/Android介面寫法分流_計劃):
--   每個區段扣掉子區段後的自身時間,依它自己的名稱分類;分不出類的跟著最近一個分得出類的祖先;一路上都分不出的算其他。
--   所以 XML 的 measure 裡包著 Compose 的排版時,Compose 那段算 Compose,外層只算剩下的。
-- 只用標準 SQLite 語法與 slice/thread_track/thread/process 四張表(測試用 Python 內建的 sqlite3 跑同一支檔)。
-- 效能:往下走子區段時直接查 slice 表(trace_processor 對自己的表過濾快,查中間結果會變成平方級),
--   分類先對「不重複的區段名」算一次,通常只有幾百個。
-- 註解一律不以分號結尾:收據的重跑腳本拿第一個以分號結尾的行當查詢結尾,註解以分號結尾會把查詢截斷。
WITH RECURSIVE
main_track AS (
  SELECT tt.id AS track_id
  FROM thread_track tt
  JOIN thread t ON t.utid = tt.utid
  JOIN process p ON p.upid = t.upid
  WHERE p.name = '__PROCESS__' AND t.tid = p.pid
),
main AS (
  SELECT s.id, s.ts, s.dur, s.name, s.parent_id
  FROM slice s
  WHERE s.track_id IN (SELECT track_id FROM main_track) AND s.dur >= 0
),
names AS (
  -- is_fn:composition tracing 的函式區段,形狀固定是「套件.函式 (檔.kt:行號)」,整個名稱只有一個空白。
  --   ART 的鎖競爭區段也帶「(檔.kt:行號)」但是一整句話(2026-10-23 實驗室真實 Trace),只比括號會被誤算成 Compose。
  SELECT name,
    CASE
      -- compose: 小寫開頭是 LazyColumn 的預先組合(compose:lazy:prefetch:*,2026-10-23 實驗室 Compose 1.9 真實 Trace)
      WHEN name GLOB 'Compose:*' OR name GLOB 'compose:*' OR name GLOB 'Recomposer:*' OR is_fn THEN 'compose'
      WHEN name IN ('inflate', 'obtainView', 'setupListItem') OR name GLOB 'RV *' THEN 'xml'
      WHEN name IN ('traversal', 'measure', 'layout', 'animation', 'input', 'Record View#draw()', 'postAndWait')
        OR name = 'draw' OR name GLOB 'draw-VRI*' THEN 'pipeline'
    END AS own,
    is_fn
  FROM (
    SELECT name, (name GLOB '* (*.kt:[0-9]*)' AND length(name) - length(replace(name, ' ', '')) = 1) AS is_fn
    FROM (SELECT DISTINCT name FROM main)
  )
),
frame AS (
  -- 不要求在最上層:App 開了訊息迴圈追蹤時,doFrame 會掛在 Looper 訊息的區段底下;doFrame 本身不會巢狀
  SELECT id AS frame_id, ts, dur FROM main WHERE name GLOB 'Choreographer#doFrame*'
),
tree AS (
  SELECT f.frame_id AS id, f.frame_id, 'other' AS fam
  FROM frame f
  UNION ALL
  SELECT s.id, t.frame_id, COALESCE(n.own, t.fam)
  FROM tree t
  JOIN slice s ON s.parent_id = t.id
  -- IS 而不是 =:名稱是 NULL 的區段(track_event 沒給名稱)也要接得上,照「分不出類、跟祖先」,不然它連子樹整段消失
  JOIN names n ON n.name IS s.name
  -- 沒收尾(dur -1)的區段連同底下整棵子樹都不走:它的時間沒從祖先扣掉(kids 只算已收尾的),留給最近一個已收尾的祖先,
  -- 不擋的話,名稱在別處出現過時子樹會被算進去、祖先又沒扣,四類加總超過幀長
  WHERE s.dur >= 0
),
kids AS (
  SELECT parent_id, SUM(dur) AS kid_ns FROM main WHERE parent_id IS NOT NULL GROUP BY parent_id
),
self AS (
  -- 子區段總長比自己長(資料錯或時間重疊)時取 0,不輸出負數
  SELECT t.frame_id, t.fam, m.name, MAX(m.dur - COALESCE(k.kid_ns, 0), 0) AS self_ns
  FROM tree t JOIN main m ON m.id = t.id LEFT JOIN kids k ON k.parent_id = t.id
),
fn AS (
  SELECT frame_id, name, ROW_NUMBER() OVER (PARTITION BY frame_id ORDER BY SUM(self_ns) DESC, name) AS rk
  FROM self
  WHERE name IN (SELECT name FROM names WHERE is_fn)
  GROUP BY frame_id, name
),
per_frame AS (
  SELECT frame_id,
    SUM(CASE WHEN fam = 'xml' THEN self_ns ELSE 0 END) AS xml_ns,
    SUM(CASE WHEN fam = 'compose' THEN self_ns ELSE 0 END) AS compose_ns,
    SUM(CASE WHEN fam = 'pipeline' THEN self_ns ELSE 0 END) AS pipeline_ns,
    SUM(CASE WHEN fam = 'other' THEN self_ns ELSE 0 END) AS other_ns
  FROM self GROUP BY frame_id
)
SELECT 'f' || f.ts AS frame, f.ts AS frame_ts, f.dur AS frame_dur, p.xml_ns, p.compose_ns, p.pipeline_ns, p.other_ns,
  fn.name AS top_compose_fn
FROM frame f
JOIN per_frame p ON p.frame_id = f.frame_id
LEFT JOIN fn ON fn.frame_id = f.frame_id AND fn.rk = 1
ORDER BY f.ts;
