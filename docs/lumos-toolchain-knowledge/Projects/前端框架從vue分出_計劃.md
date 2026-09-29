---
type: project
status: todo
created: 2026-09-29
updated: 2026-09-29
aliases:
  - React 分出 vue
  - 前端框架分題
related:
  - "[[Projects/代碼審前後端角色鏡頭_計劃]]"
  - "[[Systems/補新語言SOP]]"
  - "[[Systems/效能檢核目錄]]"
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
summary: |-
  WHY:[2026-09-29 Enzo 裁 [[Projects/代碼審前後端角色鏡頭_計劃]] d3「另外開」]前端依賴裡有 react/next/svelte/@angular/core/solid-js/preact 的檔,現在一律拿 vue 的棧別檢核題與 vue-idioms;要不要各自分出題組與慣例,走補新語言的標準流程另案處理
  REVISIT:2026-12-29 有 React/Svelte/Angular 專案真的要接進來時才開工;到期還沒有就把這篇改 superseded 並寫明沒人用
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/效能檢核目錄
---
# 前端框架從 vue 分出_計劃

> 白話:現在工具把所有前端框架都當成 vue 來審。這篇記著「要不要把 React、Svelte、Angular 分出來、各給自己的題目和慣例」這件事,等真的有這類專案要接進來再做。

## 現況

- 判前後端時,前端依賴清單命中任何一個框架都歸成 vue(判定在 [[Systems/pitfalls-code-loop]] 那一帶),連帶拿 vue 的五題效能題和 vue-idioms。
- 對 React 等框架,vue 專屬的題(響應式成本、watch 競態)可能問錯方向;這點還沒有實例佐證。

## 開工條件

- 有 React、Svelte 或 Angular 的專案真的要接 lumos。照 [[Systems/補新語言SOP]] 的八格盤點走,不要只補題組。
