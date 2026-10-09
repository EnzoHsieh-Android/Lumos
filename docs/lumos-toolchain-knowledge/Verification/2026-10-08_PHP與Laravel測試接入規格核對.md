---
type: verification
status: pass
date: 2026-10-08
valid_under: 官方Laravel12.x、Pest及Infection文件的接入規格核對，未執行消費專案或原生PHP測試
revalidate_when: 消費專案PHP/Laravel/Pest/PHPUnit與抓錯工具版本確定時，核對相應版本文件並跑原生資格考卷
tags:
  - type/verification
  - status/pass
  - scope/evals
system_refs:
  - "[[Systems/test-quality-evidence]]"
---
# 2026-10-08_PHP與Laravel測試接入規格核對

## 文件核對範圍

只核對接入規格與官方來源，不是PHP/Laravel原生測試、mutation工具或靜態掃描實跑。Node.js已在共用標準；此前56次固定實驗仍只有Python/Node，不擴大分母。

Laravel12.x testing文件確認Pest/PHPUnit/Artisan入口與Unit不啟動應用；database testing說明RefreshDatabase交易；mocking說明測試與listener分工，events的testing節明示全域Event fake可影響依事件生成資料的factory。Pest官方有mutation testing；Infection相容性依當前supported frameworks與消費專案版本核對，不沿用過去Pest支援新聞。這次來源是版本例子，不假定消費專案版本。

新增PHP/Laravel表格與專節：獨立expected、Feature業務結果、factory和fake前置情境、測試DB設定、相關故障與負例資格。狀態planned，靜態掃描器PHP能力不宣稱已接入。

來源：
- https://laravel.com/docs/12.x/testing
- https://laravel.com/docs/12.x/database-testing
- https://laravel.com/docs/12.x/mocking
- https://laravel.com/docs/12.x/events#testing
- https://pestphp.com/docs/mutation-testing
- https://infection.github.io/guide/supported-test-frameworks.html

REVISIT:2026-10-21 補PHP/Laravel原生資格與真專案證據後才更新平台能力；本紀錄只證明文件來源核對。

乾淨審查指出composer.lock不能固定實際PHP runtime；標準已改為套件lock與實際php --version、extensions/coverage driver分開留證，另用composer check-platform-reqs核對，config.platform模擬不能當實機版本。來源：https://getcomposer.org/doc/06-config.md#platform 與 https://getcomposer.org/doc/03-cli.md#check-platform-reqs 。
