# 代碼審第七輪收貨紀錄

## 這一輪的做法(使用者 2026-11-02 第六輪後裁定「修完再派兩席驗收」)

- 編制:資安一席看全份凍結材料(處置閘要最後一版有資安席);正確性一席只看這一輪的修補差異(修前 34bef2d8 → 修後 c2335430;程式與測試在 e22b4083,之後只有卷證與帳本)。
- 修補前先依根因分組(見 r6-intake.md〈根因分組〉),每組先寫先紅測試,逐道改壞確認各自翻紅,並對大型與深層巢狀輸入量過效能與記憶體(見 r6-intake.md〈作者自驗(修後、派第七輪前)〉)。

## 配對案例(待驗範圍,不是已修好的證據)

| 組 | repair(原問題) | preserve(要維持的既有行為) | 兩版證據 |
|---|---|---|---|
| ①Kotest 匹配器 | catch 裡 `e.message.shouldNotBeNull()` 而 try 沒 fail 要列;try 有 fail、catch 用 `e.shouldBeInstanceOf<X>()`、`e.message.shouldBe("x")`、`e.message shouldBe("x")` 檢查不列;try 只有 `f().shouldBe(5)` 而 catch 只印出要列;catch 裡 `shouldRetry &&` 不算檢查 | 第五輪的 w1–w6(check(true)、require(true)、shouldRetry 宣告、logger.shouldLog(e) 不算檢查;中綴 shouldBe 算);第四輪的 shouldBe、check(、require( 檢查不列 | 修後 `-k tq_guard_catch` 綠;修前紅 6 條 |
| ②catch 型別 | 1 萬 2 千層巢狀 catch 型別括號 3 秒內 | 型別是 AssertionError、Error、Throwable 才判吞斷言 | 修前 14 秒,修後 3 秒內;端到端 2 萬層 39.5 → 0.47 秒 |
| ③函式名泛型 | `@Test fun <T : List<Int>> t()` 找得到名字 | 沒收尾的 `fun <` 250 行仍在上限內 | 修後 `-k rg_methods` 綠;修前紅 |
| ④空白字 | 行尾逗號後是 FF、VT、全形空白,類別路徑還在 | 第五輪的長註解、行尾空白、冒號接空行與註解行、CRLF | 修後 `-k rg_methods` 綠;修前紅 3 條 |
| ⑤訊息與說明 | 整支檔超過上限的 tq/too-large 帶「這支整支沒比對」;skill 參考頁的 test-guard 說明不提建置檔與 CI | 抓不到清單跟標準逐字同一份 | 修後 `-k tq_guard_cli` 綠;修前紅 |

## 收貨(兩席交回後)

- 兩份席報告從子代理逐字稿抽出原樣存檔(會談暫存區 save_r7.py),沒有改動。
- 機械收貨:report-normalize 兩份都已正規化(severity 行數 = 檔級一行 + 每條一行);quote-check 全數錨定;refcheck missing 0、out_of_range 0;seat-check 只有「報告沒寫材料檔名」的觀測項。

## 重現(編排者自己跑,修後 c2335430)

| 發現 | 命令 | 結果 | 判 |
|---|---|---|---|
| s1 c1(名字前綴把一般方法算成 Kotest 檢查) | 直接呼叫 `_tg_catch_no_fail`:`try { foo(); fail("x") } catch (e: AssertionError) { shouldNotify(e) }` | False(吞斷言漏列);同形的 `println(e)` 是 True | HIT |
| c2(清單漏掉真的 Kotest 匹配器) | 同上:`try { foo(); fail("x") } catch (e: Throwable) { e.message shouldInclude "boom" }` | True(正常檢查被誤列) | HIT |

## 根因分組(id = 席代碼 + 報告序號:c 正確性 3、s 資安 2,共 5 條,席位標 major 1 條:s1)

| 組 | 根因 | id | 性質 |
|---|---|---|---|
| ①catch 判讀靠字面猜「這個名字算不算檢查」 | 第五輪寬(should 開頭都算)、第六輪窄(只認中綴)、第七輪前綴白名單(後面接什麼都放行,又漏掉清單外的真匹配器);三輪都被一步改名打穿或誤列 | s1 c1 c2 | 修補回歸(s1 major) |
| ②新分支沒有測試釘住 | 宣告排除、前綴清單後七類、換行後空白、型別範圍改成本體 | c3 | 這輪新加分支的測試缺口 |
| ③兩層以上巢狀泛型 | 整支不比,已寫進抓不到清單 | s2 | 原有、已揭露 |

## 停在這裡

第七輪仍有 1 條 major(s1),而且是同一個字面判讀第三次被打穿;照承諾停下來攤給使用者裁,並附上網查到的換形狀做法(Error Prone 的 AssertionFailureIgnored:只看結構、不看 catch 內容)。

## 先查世界(使用者 2026-11-02 裁定這一步加進審查流程,這一輪先照做)

- PRIOR-ART:catch 吞斷言——Google Error Prone 的 AssertionFailureIgnored:try 裡有斷言或 fail()、catch 接 AssertionError 或更寬的型別就報,不看 catch 內容,誤報用標註放行,建議改 assertThrows(https://errorprone.info/bugpattern/AssertionFailureIgnored)。MissingFail:try 沒 fail()、catch 有斷言就報,並列一長串降誤報的排除(https://errorprone.info/bugpattern/MissingFail)。採用前者的判法;排除「靠名字猜 catch 裡算不算檢查」——r5 寬、r6 窄、r7 前綴白名單三輪各被打穿,Error Prone 本身也不做這件事。
- PRIOR-ART:效能——regexploit(Doyensec)只在開發時掃正規式的災難回溯(https://pypi.org/project/regexploit)。對比對工具的 38 條正規式掃過:36 條沒有平方級以上的回溯,2 條(_TG_CONST、_TG_LIT)用佔有式量詞、工具不支援語法而跳過(佔有式本身不回溯)。它看不到「每個起點各掃一段很遠的文字」的形狀(r5、r6 的 catch 與類別空白都是這種),所以另加一條通用的倍增耗時測試。
- 參考(第二批):Kotest 的 assertionMode=Error 在執行期把沒呼叫斷言的測試判失敗(https://kotest.io/docs/assertions/assertion-mode.html);PIT 的 Descartes 找「方法內容拿掉、測試照綠」的 pseudo-tested 方法(https://github.com/stamp-project/pitest-descartes);SpecBench 結論「只改進測試套件無法消除 reward hacking」(https://arxiv.org/html/2605.21384v1)。

## 處置(使用者 2026-11-02 第七輪後裁定「照 Error Prone 換形狀」)

- 折入:s1 c1 c2(catch 吞斷言只看結構,名字字表拿掉;try 沒 fail 那半寬判)、c3(補 catch 型別只看括號裡、catch 裡 fail 與重丟不算吞、換行後全部空白字的測試;宣告排除與前綴清單隨字表拿掉而不存在)。
- 放行(原報 minor,逐條指回席報告原條):
  - s2:兩層以上巢狀泛型的測試宣告整支不比,已寫進抓不到清單;改寫既有測試成這種宣告會列成測試被刪,只漏新增的。
- 條款改寫:S6 原本寫「catch 用 Kotest 匹配器、check(、require( 檢查不列」,改成接得住 AssertionError 的 catch 不看內容一律列;前幾輪「不列」的 s2、s7–s9、d2–d4、w6、d6 改成列(判錯的代價是多一條可放行的候選)。

## 作者自驗(修後、派第八輪前)

- 先紅:改了的 8 條期望與新加的 5 條(S6 r7)在修前程式上紅 8 條;修後全綠(`-k tq_guard` 247、`-k lint_new` 82、`-k lint_waive` 31、`-k rg_methods` 33、`-k test_guard_registered` 8)。
- 改壞檢查(會談暫存區 mutate8.py 加一次單獨的):吞斷言又看 catch 內容、型別範圍改成本體、重丟也算吞、catch 裡 fail 也算吞、換行後只認 ASCII 空白、catch 括號回原本的平方級寫法,6 道都翻紅;最後一道同時被既有大輸入與新的倍增測試抓到(4 倍輸入 1.26 → 19.76 秒)。
- 倍增耗時測試在修前程式上也綠:這輪列的 19 種觸發字目前都沒有平方級;它是一張網,不是證明。
- 考場重跑:真實歷史 44 條、對照表逐筆跟上一輪相同(考場歷史沒有 catch 的改動,這條規則的誤報量沒量到,回頭條件寫在計劃)。
- ruff(專案宣告的規則組)修前修後都是 1140 條。
