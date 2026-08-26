### d-f1 [S3] 條件性條款重犯 [S2] 剛修好的「回頭條件不可驗」模式
severity: major
引句:「條件性條款:Landmark 若宣告 lint,smoke 接其 daily-governance 排程(有既有基建),屆時另立小案。」
佐證:file: `scripts/lumos:6698`
說明:「Landmark 若宣告」=靠人記得查的未來事件,無 revalidate_when 無 Issue 無機械落點——散文預言,鐵則四不過。

### d-f2 [L2] 讀宣告檔的 repo_root 解析懸空:doctor 手上只有 env.vault,直覺寫法對 Landmark 永遠讀不到=靜默假綠
severity: major
引句:「四種格式 problem:非 dict/value 非 list/命令空/缺佔位符——不加 PATH、不加必填鍵、不提新鮮度」
佐證:file: `scripts/lumos:500`
佐證:file: `scripts/lumos:10911`
佐證:file: `scripts/lumos:722`
說明:repo 內已有兩套 repo_root 解法(cwd→.git vs vault-parents→docs);env.vault/.lumos/lint.json 永不存在;「逐字複用」只覆蓋驗證核心,I/O 與路徑解析沒抽——會長第二份或讀錯位置。

### d-f3 [L2] 代號撞 hook 分層既定詞彙(L1/L2/L3=三道防線)
severity: minor
引句:「段名 [L2](守 doctor 單字母+數字慣例)」
佐證:file: `scripts/hooks/pre-commit:2`
說明:同 repo 兩個「L2」意義,誤導 grep/search 與下個 session。

## 查過乾淨
decisions 寫 system 節點合法(該節點已有 d1/d2 生產中);Landmark 真宣告檔五棧全過四檢=零日爆紅風險;服務面兩條件=既有機制自然推論非空話。
