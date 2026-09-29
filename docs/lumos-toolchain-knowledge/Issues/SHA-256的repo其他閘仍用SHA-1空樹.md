---
type: issue
status: open
created: 2026-09-29
updated: 2026-09-29
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-09-29 乙代碼審 r5 外家席、正確性席]主程式裡寫死的空樹編號是 SHA-1 的(4b825dc…);SHA-256 物件格式的 repo 空樹是 6ef19b4…,拿 SHA-1 那個去 git diff 會回「unknown revision」。新分支首推、找不到主線時,推送起點判法回的就是這個寫死的值,之後拿它當 diff 起點的閘全部算不出改動。重現:`git init -q --object-format=sha256 R && git -C R commit -q --allow-empty -m x && git -C R diff --name-status 4b825dc642cb6eb9a060e54bf8d69288fbee4904 HEAD`,回傳碼 128
  WHY:[2026-09-29 乙代碼審 r5,Enzo 裁「修完直接推」]乙只修了存量漂移自己那兩條路(改用這個 repo 算出的空樹,見 [[Systems/存量漂移守衛]]);其他閘(每支檔有家、筆記形狀擋、筆記內容審、推送起點判法本身)同一個常數沒動——改的是全工具共用的推送起點,範圍比乙大,要另外審
  REVISIT:2026-12-29 決定要不要把空樹改成每個 repo 算一次、所有閘共用;先查這段期間有沒有人用 SHA-256 的 repo(GitHub 目前不收這種 repo)
---
# SHA-256的repo其他閘仍用SHA-1空樹

白話:git 有兩種物件格式,舊的 SHA-1 和新的 SHA-256,兩種的「空樹」編號不一樣。工具裡寫死的是 SHA-1 那個,所以在 SHA-256 格式的 repo 第一次推送、又找不到主線時,好幾道推送前的檢查會算不出這次改了哪些檔。

## 現況

- 存量漂移檢查已修:改用這個 repo 自己算出的空樹([[Systems/存量漂移守衛]],[[Projects/存量漂移防線_計劃]] 的乙代碼審 r5)。
- 其他閘沒修:它們共用同一個寫死的常數與推送起點判法。
- 影響面:GitHub 目前不收 SHA-256 的 repo,實際碰到的機會低;碰到時的症狀是檢查判不了,不是靜默放行。

## 要做什麼

- 把空樹改成每個 repo 算一次(`git hash-object -t tree --stdin`,標準輸入要明確給空的,不然在推送掛鉤裡會讀到掛鉤自己的 ref 清單),推送起點判法與各閘共用。
- 改的是全工具共用的推送起點,要走代碼審。
