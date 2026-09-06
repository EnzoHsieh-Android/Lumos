severity: major

- [major] 守衛測試的白名單抽取正則會被例行重構繞過(把 _VENDORED_TOOLKIT 拆成兩個 tuple 相加),LICENSE 進了真正的 deinit 白名單而守衛仍報綠。
  位置:`scripts/test_lumos.py:25923`
  引句：「m = _re.search(r"_VENDORED_TOOLKIT = \((.*?)\)", src, _re.S)」
  why: 正則非貪婪,停在第一個右括號。沙箱驗證:重構成 ("scripts/lumos","scripts/test_lumos.py") + (...,"LICENSE") 時只抓到第一組,判斷通過,而執行期 tuple 確實含 LICENSE。_deinit_remove_vendored 對白名單每項無條件刪檔,這正是整個功能要防的情境。改成 list 或 tuple(...) 呼叫會失敗而非假綠,只有 tuple 相加這個形狀危險。

- [major] LICENSE 與產出 HTML 都宣稱 3d-force-graph 1.80.0,但預設(非 standalone)模式用的 CDN 網址沒鎖版,歸屬對那個頁面實際載入的碼並不正確。
  位置:`scripts/lumos:8525`
  引句：「3d-force-graph": ("https://cdn.jsdelivr.net/npm/3d-force-graph",」
  why: marked 有鎖 @12.0.2 且與文字相符,3d-force-graph 沒有。預設匯出時瀏覽器載入 jsdelivr 當下的最新版,可能隨時變成不同主版本而 repo 一行沒改;而註解無條件寫死 1.80.0。只有 standalone 保證正確(它讀已快取的 vendor 檔,實測確為 1.80.0)。

- [minor] 新增的 HTML head 授權註解內文含 --,HTML 註解文法不允許。
  位置:`scripts/lumos:8051`
  引句：「Third-party components used by this page (embedded verbatim when exported with --standalone):」
  why: 實際產生一份頁面用 html.parser 解析,註解正確在真正的 --> 收尾、後續標籤解析正常,所以目前不影響渲染;屬規格符合度問題。

- [minor] 檔頭檢查是對前 45 行做字串包含,不是確認那段真的是註解區塊,所以只要那 45 行裡任何地方出現該字面就算通過。
  位置:`scripts/test_lumos.py:25902`
  引句：「missing = [f for f in targets if "SPDX-License-Identifier: MIT" not in "\n".join((root / f).read_text(encoding="utf-8").splitlines()[:45])]」
  why: 沙箱構造一支開頭沒有真正授權標頭、但維護者註記裡提到該字面的檔,判斷為「有標頭」。今天 13 支檔都有真標頭所以風險低,但測試名字承諾的嚴謹度高於實作。

其餘查過乾淨:--help 輸出前後逐位元組相同(授權區塊在 shebang/coding 行與 docstring 之間,description=__doc__ 未受影響);跑完 slim-gen 並比對產出檔頭,一致、無重複、無錯位,仍能 ast.parse;所有動過的 bash 腳本 bash -n 過,沒有哪支的 shebang 之後有必須緊接的指令;LICENSE 第三方登記與 vendor 兩支檔實際內容核對相符(marked 檔頭 v12.0.2、Copyright 2011-2024 Christopher Jeffrey;3d-force-graph 只有一行版本註解,證實上游無 banner);README 中英兩版授權段語意等價;根目錄 LICENSE 與檔頭的 MIT 文字互相逐字相同,也與標準條款相同;anchor baseline 的雜湊重算後與五個被錨檔案的現況相符。
