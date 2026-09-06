severity: major

- [major] 新節點 Systems/授權與歸屬.md 的 summary(FLOW/KEY/DEP/TEST)完全空白,跟 lumos new system 剛建檔的骨架逐字相同。
  位置:`docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:11`
  引句：「summary: |-」
  why: 對照 scripts/lumos 的 TEMPLATES["system"] 骨架一字不差,而 cmd_new 印的提示明講「摘要那幾行還是空的,要自己填」。抽查既有五篇 Systems 節點(anchor-integrity、cochange-guard、check-r-guard、bound-tests-gate、canary-audit)全部把四行填成能查的摘要——那是檢索入口,search 與 context --brief 都讀這裡,空白等於這篇對兩者隱形。

- [major] 同一篇節點 about_code 留空,但內容整篇在講 scripts/lumos 的檔頭與白名單行為。
  位置:`docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:7`
  引句：「about_code: []」
  why: 官方判準是「改那支檔的人不看這篇會不會做錯事?會就列」;對照 Systems/cochange-guard.md 的 about_code 列了兩支。空著等於以後有人動 scripts/lumos 時,lumos impact 不會把這篇排進固定席。

- [major] 節點裡唯一的 [test:] 綁定寫在正文散文條列裡,不是慣例要求的 KEY 摘要行,合約鏈機械掃不到。
  位置:`docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:46`
  引句：「[test:t_license_headers_travel_with_vendored_files]」
  why: 對照 Systems/check-r-guard.md,既有合約一律寫進 summary 的 KEY 行才會被 INVARIANT_RE 解析、被 guard bind / contracts / bound-tests-gate 認得。寫在正文只是普通文字,對整條合約鏈是隱形的。

- [major] 新守衛測試用正則掃原始碼確認常數內容,而同一支測試檔裡已有更好、且針對同一常數的既有寫法。
  位置:`scripts/test_lumos.py:25923`
  引句：「m = _re.search(r"_VENDORED_TOOLKIT = \((.*?)\)", src, _re.S)」
  why: 對照同檔 t_precommit_whitelist_drift_guard 已在做幾乎一樣的事,寫法是載入模組後直接讀 m._VENDORED_TOOLKIT——用物件本身,不猜字串邊界、不怕格式化改變。改走正則是替同一件事引入第二種、還更弱的做法,repo 沒有其他先例支持。

- [minor] slim/ 五支加 SPDX 碰了 FROZEN.md 明講已凍結的目錄,但有在 slim/README.md 誠實交代理由。
  位置:`slim/README.md:608`
  引句：「這裡加授權標示是簿記,讓歷史副本也說得清自己是什麼。」
  why: 凍結公告只禁止「期待改動會被使用者拿到」與「在這裡動刀刪除」,沒明文禁止純簿記小改;而且守衛測試的清單沒把 slim/* 排進去,代表這五支不受機械把關、純手記,跟「簿記」的自我定位一致。

其餘 clean:檔頭插在 docstring 外是唯一不破壞 description=__doc__ 的位置,12 支一致無例外;HTML 註解放中繼資訊在該檔是既有慣例;README 中英與 ONBOARDING 的授權段位置與句式貼著各檔既有慣例;根目錄 LICENSE 的三段式結構 repo 過去沒有可比對象,談不上引入第二種形態,且決策區有把取捨講清楚。
