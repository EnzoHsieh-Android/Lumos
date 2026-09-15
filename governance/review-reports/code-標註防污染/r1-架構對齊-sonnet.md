severity: major

# 架構對齊審查——code-標註防污染 r1

只判「跟既有做法一不一樣」,不判對錯與 bug。逐條列在下面,每條附引句與既有做法的出處。

## 發現一:洗牌的種子推導自己另開一套,沒有沿用題庫腳本既有的雜湊做法

`cmd_delta` 要讓待標清單可重現地洗牌,取種子的方式是直接把兩個欄位串起來當種子字串餵給 `random.Random()`:

引句:「_salt = str(gs.get("split_salt") or gs.get("snapshot_commit") or "")」

同一個目錄裡,建題庫那支腳本要做同一件事(可重現洗牌)時,做法是先用 `hashlib.sha256` 把 key 雜湊過、拿雜湊值的十六進位字串當種子,而且種子鹽固定用模組層級常數 `SALT`,不是臨時去讀資料欄位:

file: `governance/eval/build_goldset.py:52`
```
rnd = random.Random(hashlib.sha256((q + SALT).encode()).hexdigest())
```
（另一處同樣做法在 `governance/eval/build_goldset.py:166`）。`SALT` 定義在 `governance/eval/build_goldset.py:12`,是固定字面常數 `"lumos-retr-v1"`,建題庫時原樣寫進 goldset 的 `split_salt` 欄位(`governance/eval/build_goldset.py:240`),而 `governance/golden/retrieval/spec.md:266` 也把「用 split_salt 洗牌」寫成規格的一部分。

新程式要用的正是同一個 `split_salt` 欄位,但拿到之後**不雜湊、直接把字串塞進 `random.Random()`**,而且鹽的取得多了一條 `gs.get("split_salt") or gs.get("snapshot_commit") or ""` 的 fallback 鏈,這條 fallback 邏輯在既有腳本裡沒有對應版本——等於為「可重現洗牌」這件事另開一套推導規則,而不是照抄 `build_goldset.py` 已經在用、規格書也點名的那一套。

severity: major
blocking: 是——這是「同一個問題、同一個目錄下已有一種做法,新程式碼另開一種」的典型情況,不是命名或風格差異;種子推導方式不同會讓兩支腳本對「同一份 split_salt 該怎麼用」有兩種互不相通的解讀,之後任何人想查「洗牌怎麼做的」要分別讀兩套邏輯。

## 發現二:新測試重新刻一份載入 retrieval_eval.py 的樣板碼,沒有呼叫既有共用 fixture 函式;還因此直接呼叫 cmd_delta 本體、繞過既有測試一律走 subprocess 的入口

`t_delta_sheet_is_shuffled` 為了拿到「洗牌前的名次序」做比對,自己重新寫了一次載入 `retrieval_eval.py` 模組的樣板碼:

引句:「_sp = _ilu.spec_from_file_location("_re_sh", repo / "governance" / "eval" / "retrieval_eval.py")」

但這段樣板碼(spec_from_file_location + module_from_spec + exec_module + 設 ROOT/VAULT)在同一支測試檔案裡早就抽成共用函式:

file: `scripts/test_lumos.py:26687-26697`
```
def _load_retrieval_eval(root):
    """以 fixture 為根載入 retrieval_eval 模組(獨立實例,不污染其他測試)。"""
    import importlib.util
    repo = Path(GRAPHCTL).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        f"retrieval_eval_fx_{id(root)}", repo / "governance" / "eval" / "retrieval_eval.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ROOT = root
    m.VAULT = root / "docs" / "kg-knowledge"
    return m
```
這個 `_load_retrieval_eval(root)` 在同檔案裡被呼叫超過十次(例如 `scripts/test_lumos.py:26704, 26776, 26843, 26865, 26917, 26961, 26995, 27027, 27063, 27099, 27137, 27221`,以及新測試之後的 `27542, 27572, 27601, 27635, 27732`)——新測試前後的既有測試都在用同一個入口,唯獨這支自己重刻一份。這是「引入第二種做法」的直接例子:兩份邏輯字元幾乎一樣,只是模組名字取了不同的字串(`"_re_sh"` vs `f"retrieval_eval_fx_{id(root)}"`),之後任一份改了行為(例如共用函式加了防污染的清理邏輯),另一份不會跟著變。

同一段程式接下來為了注入「上游順序被打亂」這個情境,又匯入一次 `refresh_labels.py` 本體,直接呼叫命令處理函式:

引句:「_rl._load_re = _load_shuffled」

這一步繞過了既有測試一律用 subprocess 呼叫 CLI 入口(`sys.executable ... "delta" ...`)的慣例,改成 in-process 直接呼叫 `cmd_delta(_args)`。本檔案裡確實有「白箱注入時可以繞開 CLI、直接匯入模組」的前例——`t_refresh_atomic_and_lock` 也是匯入 `refresh_labels.py` 後 monkeypatch:

file: `scripts/test_lumos.py:27825-27847`(節錄)
```
spec = importlib.util.spec_from_file_location("refresh_labels_t", repo / "governance" / "eval" / "refresh_labels.py")
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
...
rl.os.replace = boom
try:
    rl._atomic_write_json(tgt, {"new": 1})
```
但這個前例碰的是內部私有函式 `_atomic_write_json`(供多個 `cmd_*` 共用的底層原語),而且事後在 `finally` 裡把 `rl.os.replace` 換回原值。新測試碰的是 `cmd_delta` 本身——`main()` 分派表裡對外的命令入口那一層,而且沒有對應的還原動作(雖然因為是獨立載入的模組實例,不還原不會波及其他測試,這點沒有實害)。也就是說:「繞開 CLI 直接匯入模組」是既有前例允許的手法,但這次多繞了一層——連命令處理函式本體都直接呼叫,而不是像前例只碰底層私有原語。

severity: major
blocking: 是——「有共用 fixture 卻另刻一份」在這份程式碼旁邊十幾處呼叫點都看得到對照組,是可以直接改成呼叫 `_load_retrieval_eval(root)` 就消掉的重複;直接呼叫 `cmd_delta()` 本體那段雖然有動機(CLI 邊界注入不了假的 `collect_unjudged`),但已經比既有前例多跨一層,值得在收斂時明確記一筆「這裡例外繞過入口的理由」,而不是悄悄比照前例的名義卻做了不同範圍的事。

## 發現三:測試假造 args 物件用自訂 class,沒有沿用同一個測試檔案裡已有的 SimpleNamespace 慣例

`t_delta_sheet_is_shuffled` 直接呼叫 `cmd_delta()` 前,要準備一個假的 `args`,做法是手寫一個 class:

引句:「class _A:   # delta 子命令要的欄位(參數解析包在 main 裡,沒有獨立入口可借)」

同一份測試檔案裡,同樣是「要繞過 argparse、直接呼叫內部函式,所以手造一個帶欄位的 args-like 物件」這件事,既有做法是用標準庫的 `types.SimpleNamespace`:

file: `scripts/test_lumos.py:27550`
```
args = types.SimpleNamespace(k=8, snapshot=None)
```
（同一支測試 `t_eval_history_record_fields` 裡第二次呼叫在 `scripts/test_lumos.py:27563`,也是同樣寫法。）兩者功能上等價,但新測試沒有沿用檔案裡已經在用的標準庫寫法,而是另外定義一個帶類別屬性的空 class 來頂替。

severity: minor
blocking: 否——純粹是「造一個帶固定欄位的假物件」這件小事有兩種等價寫法並存,不涉及跨層呼叫或行為分歧,對測試本身的正確性與其他測試都沒有影響。

## 發現四:新增 material 子命令後,檔案開頭的子命令總覽沒有同步列入

`refresh_labels.py` 的分派表新增了一項:

引句:「mt = sub.add_parser("material", help="[S13] 給評審讀的題目卷(★不含任何標註★)")」

但檔案最上方的模組 docstring 是這支腳本自己維護的子命令索引,列出「delta / repin / merge / apply / signal」五項、各配一行說明:

file: `governance/eval/refresh_labels.py:4-9`
```
子命令:
  delta   對目標語料算評測母體、diff labels → 未標清單+delta 標註表(觀測,恆 rc0;輸入壞 rc2)
  repin   評測母體 unjudged==0 才寫 snapshot_commit(rc0=已重釘/rc1=有未標硬擋/rc2=輸入壞)
  merge   雙評審輸出合併:一致(同值)→agreed;不一致→disputed;B 席缺→degraded 全 disputed
  apply   人放行動作:把 merge(+人裁 adjudication)寫進 goldset labels(atomic;唯一寫 labels 入口)
  signal  讀 history 最後一筆考卷的 unjudged_rate,advisory 輸出(週閘薄接線消費)
```
這份 diff 沒有動這段(hunk 起點在第 102 行之後),所以 `material` 沒有被補進這份「跑 `--help` 之外、給人看整份腳本在幹嘛」的索引裡,現存五個子命令都各佔一行,新加的第六個沒有。

severity: minor
blocking: 否——不影響任何行為或測試,是文件索引跟分派表兩份清單其中一份沒同步更新,補一行就能對齊,不需要因此擋下這次改動。

## 其餘核對過、沒有發現落差的部分

逐一對照 delta/repin/merge/apply/signal 五個既有子命令的參數命名、預設值來源、輸出路徑決定方式、退出碼、訊息格式、鎖與原子寫入之後,`material` 子命令本身的形狀跟既有慣例是貼合的:`--goldset` 預設值沿用同一個 `HERE / "retrieval-goldset.json"` 寫法,`--out` 的預設值一樣是在函式體內用 `args.out or ...` 決定(跟 `delta` 同款),讀取失敗一律回 `_read_goldset` 這個既有入口而非自己重新解析 JSON,輸出檔用 `write_text` 裸寫且不上鎖——這點恰好對得上 `delta` 表自己註明的既有裁定(`governance/eval/refresh_labels.py` 裡「delta 表為觀測性產物…裸寫可接受,毋須 atomic(code-r1 f12 裁定)」那條),因為 `material` 產出的也是可重跑重算的衍生文件而非權威金標,不需要鎖或原子寫入。這幾項都沒有另開新規則。

全篇最嚴重的等級屬於「重大」,其中有 2 條會擋下這次改動。
