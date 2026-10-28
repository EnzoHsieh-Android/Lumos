-- SPDX-FileCopyrightText: 2026 Enzo Hsieh
-- SPDX-License-Identifier: MIT
--
-- 記憶體與穩定性收集:原生配置排行(heapprofd 那一段錄檔),給收集腳本(android-stability-collect.sh)寫進 stability.json 的 native_retained
-- 每列第一欄 kind 分三種:
--   site  排行的一列:a 函式、b 所在 .so、c 呼叫者(三格都是 hex 過的 UTF-8)、d 有沒有符號、e 是不是系統函式庫、f 結束時還留著的位元組
--   rows  heap_profile_allocation 的總列數(f)
--   stat  stats 裡等級是 error 或 data_loss、值不是 0 的一項:a 名字(hex)、f 值
-- 文字欄用 hex 輸出:trace_processor 的 csv 輸出不跳脫字串裡的引號與換行,hex 之後照逗號切就切得對
-- 呼叫位置:從 malloc 那一框往上走,跳過配置器那幾層(libc、libc++、libstdc++ 裡的全部框架,malloc 家族的函式名,
--   operator new 與標準庫容器的 mangle 名前綴),第一個不是的框架;回溯失敗的 ERROR 偽框架與整條都是配置器時記成 ?
-- 呼叫者:呼叫位置往上第一個不在 libart.so 的框架(是 ERROR 偽框架時記成 ?);同一呼叫位置有幾個呼叫者時取結束累計加總最大的那個,
--   一樣大時有名字的排在 ? 前面、再照名字升冪
-- 只留結束累計至少 1 MiB 的呼叫位置,照累計降冪、函式名、.so、系統旗標升冪取前 200 個
-- 規則單源 Projects/原生記憶體增長提示_計劃〈排行怎麼算〉
with recursive
leaf(cs, retained) as (
  select callsite_id, sum(size) from heap_profile_allocation where heap_name = 'libc.malloc' group by callsite_id
  having sum(size) != 0   -- 淨留量是 0 的呼叫點不影響任何加總,不往上走呼叫鏈(大錄檔省工)
),
walk(leaf, cs, step) as (
  select cs, cs, 0 from leaf
  union all
  select w.leaf, c.parent_id, w.step + 1 from walk w join stack_profile_callsite c on c.id = w.cs where c.parent_id is not null
),
fr as (
  select w.leaf, w.step, f.name as fname, f.rel_pc, coalesce(m.name, '') as path
  from walk w join stack_profile_callsite c on c.id = w.cs
  join stack_profile_frame f on f.id = c.frame_id
  left join stack_profile_mapping m on m.id = f.mapping
),
fr1 as (
  select leaf, step, fname, rel_pc, path,
    case when path = '' then '?'
         when instr(path, '!') > 0 then substr(path, length(rtrim(path, replace(path, '!', ''))) + 1)
         else substr(path, length(rtrim(path, replace(path, '/', ''))) + 1) end as so
  from fr
),
fr2 as (
  select leaf, step, fname, so,
    coalesce(so in ('libc.so', 'libc++.so', 'libc++_shared.so', 'libstdc++.so')
      or fname in ('malloc', 'calloc', 'realloc', 'posix_memalign', 'memalign', 'aligned_alloc',
                   '__libc_malloc', 'je_malloc', 'tc_malloc', '__wrap_malloc')
      or fname glob '_Znw*' or fname glob '_Zna*' or fname glob '_ZNSt*' or fname glob '_ZNKSt*', 0) as alloc,
    coalesce(fname, '') != '' as sym,
    case when coalesce(fname, '') != '' then fname
         else so || '+0x' || case when rel_pc is null then '?' else printf('%x', rel_pc) end end as func,
    (path glob '/system/*' or path glob '/apex/*' or path glob '/vendor/*' or path glob '/product/*'
      or path glob '/system_ext/*' or path glob '/odm/*') as sys
  from fr1
),
site_step(leaf, step) as (
  select leaf, min(step) from fr2 where not alloc group by leaf
),
site as (
  select l.cs as leaf, l.retained, s.step,
    (s.step is null or coalesce(f.fname glob 'ERROR *', 0)) as unknown, f.func, f.so, f.sys, f.sym
  from leaf l left join site_step s on s.leaf = l.cs
  left join fr2 f on f.leaf = l.cs and f.step = s.step
),
caller_step(leaf, step) as (
  select s.leaf, min(f.step) from site s join fr2 f on f.leaf = s.leaf and f.step > s.step
  where not s.unknown and f.so != 'libart.so' group by s.leaf
),
leafrow as (
  select s.retained,
    case when s.unknown then '?' else s.func end as func,
    case when s.unknown then '?' else s.so end as so,
    case when s.unknown then 0 else s.sys end as sys,
    case when s.unknown then 0 else s.sym end as sym,
    case when s.unknown or cf.func is null or coalesce(cf.fname glob 'ERROR *', 0) then '?' else cf.func end as caller
  from site s left join caller_step c on c.leaf = s.leaf
  left join fr2 cf on cf.leaf = s.leaf and cf.step = c.step
),
per_caller as (
  select func, so, sys, caller, sum(retained) as r from leafrow group by func, so, sys, caller
),
pick as (
  select func, so, sys, caller, row_number() over (partition by func, so, sys order by r desc, caller = '?', caller) as rn from per_caller
),
agg as (
  select func, so, sys, max(sym) as sym, sum(retained) as retained from leafrow group by func, so, sys having sum(retained) >= 1048576
),
top as (
  select a.func, a.so, a.sys, a.sym, a.retained, p.caller from agg a
  join pick p on p.func = a.func and p.so = a.so and p.sys = a.sys and p.rn = 1
  order by a.retained desc, a.func, a.so, a.sys limit 200
)
select 'site' as kind, hex(substr(func, 1, 500)) as a, hex(so) as b, hex(substr(caller, 1, 500)) as c, sym as d, sys as e, retained as f from top
union all
select 'rows', '', '', '', 0, 0, count(*) from heap_profile_allocation
union all
select 'stat', hex(name), '', '', 0, 0, sum(value) from stats where severity in ('error', 'data_loss') and value != 0 group by name;
