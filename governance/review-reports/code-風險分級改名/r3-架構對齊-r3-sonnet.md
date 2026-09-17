severity: clean

對照過的既有寫法:

1. `_is_code_file` 內讀 base 樹內容那段(patch:「g = subprocess.run(["git", "-C", str(rr), "show", f"{base}:{path}"], capture_output=True, errors=None)」)看起來像另起一份「讀某提交檔案」的實作,但同一個 `_sc_*` 家族(小改動閘)裡本來就有一支孿生函式 `_sc_churn` 用一模一樣的原生 subprocess 寫法讀 base 樹(scripts/lumos:5716,非本次改動、context 行):「g = subprocess.run(["git", "-C", str(rr), "show", f"{base}:{old}"], capture_output=True, text=True, errors="replace")」。兩者同樣用 `rr`/`base` 命名、同樣是 capture_output=True 的 git show,唯一差別是 `_is_code_file` 要 bytes(判 shebang)所以不帶 `text=True`、errors=None。這是跟著同層對照檔(`_sc_churn`)的既有慣例走,不是另開第三套讀法;`_nodehome_reader`/`_lens_git` 是另一個子系統(節點還原)的讀法,不是這一族的既有入口。

2. `_head_is_shebang` 是把 `_nodehome_required`(scripts/lumos 原 20846 行區段)裡原本內嵌的判斷抽成共用函式,兩處(每支檔有家的 `_is_code_file` 與節點還原的 `_nodehome_required`)改成呼叫同一支,函式簽章與回傳值跟抽出前的內嵌運算式等價,是收斂重複、不是引入新做法。

3. `_nodehome_code_kind`(既有分類器,scripts/lumos:20665)被 `_is_code_file` 直接沿用而非重刻;`_ledger_has_manual_only` 讀圖譜的寫法「find_vault(Path(repo_root))」跟既有兩處呼叫(scripts/lumos:22009、22099)完全同構。

4. `_spec_gate_push_report`/`manual_only` 相關舊函式確認已整支移除,`grep -n "_spec_gate_push_report" scripts/lumos` 無殘留呼叫;取代它的 `_rec_plan_risk` 是真實定義過的既有輔助函式(scripts/lumos:4840),被多處呼叫沿用同一套判斷,不是新開一條平行路徑。

引句:「檔案開頭那段 bytes 的第一行是不是 #!(每支檔有家與 _is_code_file 共用這一支——代碼審 r2 架構席:別各寫一份)。」
