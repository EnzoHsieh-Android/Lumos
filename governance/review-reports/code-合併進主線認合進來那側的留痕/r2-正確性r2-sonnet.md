severity: clean

## 正確性:cache 與第二關的 why
已讀無 finding。cache["side"] 只在 _codeloop_merge_side 正常回傳後才寫,第二關拿到的是同一個 (None, why),訊息一致;只有 side 判定拿到 side 時兩關各自用自己的期限走紀錄查找。
引句:「cache["side"] = _codeloop_merge_side(repo_root, marker_sha, raw_range, deadline)」

## 正確性:例外收成判不了
已讀無 finding。例外在賦值之前就被外層 except 接走,cache["side"] 不會被寫入,第二關會用自己的新期限重算(慢一點但結果同向,不會因第一關例外走到放行)。淺 clone 判斷的 TimeoutExpired(_git_is_shallow 只接 OSError)也被這層接住。
引句:「return None, f"判不了合進來那一側({ex.__class__.__name__}),不認"」

## 正確性:_disp_record_for 四元組呼叫端
已讀無 finding。Grep 全檔:定義一處(scripts/lumos:47076)、呼叫一處(scripts/lumos:47104,已改成四元組解包),測試 t_codeloop_merge_side_edges ⑧ 也用 _ 接第四個值。deadline 延後後,_dispositions_verdict 後面唯一用 deadline 的地方(scripts/lumos:47208 的逐題 over_budget 判斷)吃到的是延後後的值,deadline=None 時保持 None。
引句:「rec, ok, why, deadline = _disp_record_for(repo_root, marker_sha, marker_branch, merge_side, deadline)」

## 正確性:_merge_side_left 回 None 各分支
已讀無 finding。parents、caught_up、ledger、rev-list、merge-base 各自在 left 為 None 時不呼叫 git 並回「時間不夠」類原因;_git_is_shallow 用 `or 0.01` 會逾時丟例外,由外層收成不認;_codeloop_record_valid_ex 前有明確 None 檢查。皆為不認,方向安全。
引句:「if _git_is_shallow(repo_root, timeout=_merge_side_left(deadline) or 0.01):」

## 正確性:_esc_clean(ev['kind'], 20)
已讀無 finding。_codeloop_ledger_events 已保證 kind 在 kinds 內(passed/skipped),取值不會 KeyError;branch 缺值時印成「None」只是外觀。
引句:「_esc_clean(ev['kind'], 20)」

## 正確性:ledger 事件重構的行為等價
已讀無 finding。舊的子字串預篩與 kind、gate、head_sha 檢查在新共用函式中等價,只多了 isinstance(ev, dict) 與 head_sha 必為字串(更嚴,方向安全)。
引句:「and isinstance(ev.get("head_sha"), str) and ev.get("head_sha")):」

## 資料狀態五問
新舊互讀:舊帳行格式不變,共用解析等價,無影響。寫一半:帳本被截斷的半行會 json 解析失敗被略過,不認。衍生資料:cache 只活在單次判定內,無跨次殘留。時間:monotonic 期限,延後只加回合併判斷花掉的時間。不可逆:全程唯讀 git 操作,放行才寫的既有 fail-open 帳不變。

## 測試鏡頭
已讀無 finding。python3.14 scripts/test_lumos.py -k merge_side 實跑 22 passed、0 failed。⑥ 的 monkeypatch 對象是 _load_lumos_inproc() 的單例模組,finally 有還原,不污染其他測試;⑥ 前一格 ⑤ 證明流程能走到淺 clone 檢查,拿掉例外收斂則 ⑥ 會因例外落進 except 分支而紅,不是假綠。⑧ 的過期表態 marker 檔名與 _codeloop_read_dispositions 的路徑格式一致,且 base 到 md 之間有程式改動,確為「過期」而非讀不到。
引句:「m._git_is_shallow = orig」

## 圖譜鏡頭
已讀無 finding。固定席節點中 INVARIANT 各條(search 排除 superseded、re-inject sentinel、guard kill rc 與 JSON、測試假綠前置斷言、design-loop 處置閘第五步只管設計審)都不在這次動到的路徑上:改動限於 code-loop 的留痕與表態判定,新測試只新增不改既有。pitfalls-code-loop 節點的 WHY 與新章節已隨提交更新,與程式行為一致。
引句:「WHY:[2026-10-07 [[Projects/合併進主線認合進來那側的留痕_計劃]]]推送檢查遇到合併提交時」

## 角色卡
未附卡,略過。

總結:第 2 輪修正未發現新缺陷,測試實跑全綠,修正本身沒有引入新的失敗路徑。
