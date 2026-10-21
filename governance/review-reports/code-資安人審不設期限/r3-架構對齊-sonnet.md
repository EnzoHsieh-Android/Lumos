severity: minor

## finding 1:`_secapr_signer_revoked` 後面少了空行,把 `_SECAPR_*` 常數群切開
severity: minor
blocking: 否
引句:「    return e.get("signer") in revoked
_SECAPR_KEY_RE = re.compile(」
file: `scripts/lumos:9461-9467`

新函式 `_secapr_signer_revoked` 結束後,下一行直接接模組常數 `_SECAPR_KEY_RE`。鄰居的做法是函式與頂層定義之間空兩行,例如 `_secev_canon` 到 `_SECAPR_NS` 之間(`scripts/lumos:9439-9444`)和 `_SECAPR_MAX_ENTRIES` 到 `def _secapr_ssh_keygen`(`scripts/lumos:9468-9475`)。結構是對的,只是排版沒跟鄰居一致。

## 三問

**1. 分層與依賴方向:對齊。**
- 方向沒有跨層。新碼都在同一個 `_sec*` 區塊。`_secapr_*` 呼叫 `_secev_*` 是原本就有的方向,例如 `_secev_canon` 在 `scripts/lumos:9439`、`_secev_int` 在 `scripts/lumos:8559`。
- `_secapr_signer_revoked`(`scripts/lumos:9461`)和 `_secapr_entry_status`(`scripts/lumos:9602`)、`_secapr_verify`(`scripts/lumos:9692`)呼叫 `_secev_expiry_null_ok`(`scripts/lumos:9455`)。
- `_secev_ip_review`(`scripts/lumos:8625`)是 `_secev_*` 判斷項,呼叫定義在後面的 `_secev_expiry_null_ok`。這是 Python 執行時才解析名字,而且 `_secev_canon` 一樣放在 `_SECAPR_*` 區塊旁邊,有先例。
- 兩處常數各歸各家:`_SECEV_NO_EXPIRY_KINDS` 在 `scripts/lumos:8498`,`_SECAPR_NO_EXPIRY_TYPES` 在 `scripts/lumos:9452`。這跟 `_SECEV_JUDGMENT_FORMATS` 與 `_SECAPR_TYPES` 各放自己區塊的做法相同。
- 修補把原本的 `_sec_no_expiry`(沒有 `_secev_`/`_secapr_` 前綴)改成 `_secev_expiry_null_ok`。這一步讓命名回到專案慣例。

**2. 命名與錯誤處理:大致對齊,有 1 條 minor(排版,見 finding 1)。**
- 常數 `_SECEV_NO_EXPIRY_KINDS`、`_SECAPR_NO_EXPIRY_TYPES` 沿用 `_SECEV_*`、`_SECAPR_*` 的前綴與全大寫 tuple 寫法(對照 `_SECEV_SCAN_CATS` 在 `scripts/lumos:8485`、`_SECEV_CONDITIONAL_JUDGMENTS`)。
- null 的表示與判讀:不設期限只認 `value is None` 且種類在白名單內。缺鍵或寫錯都回到原本的 `_secinv_date` 檢查,錯誤碼仍是 `approval_fields_missing`(`scripts/lumos:9569`)和 review 的 `expires_on 是 review_record 必填`(`scripts/lumos:8625`),沒有新增錯誤代碼。
- 撤銷沿用原有的 `approval_signer_revoked`,逐筆判和回溯判用同一個碼,和 `_secapr_entry_status` 原本的回傳一致。
- 這是我的判斷:`_secev_expiry_null_ok` 的參數叫 `kind`,但核可鏈那邊傳的是 `typ`。鄰居 `_secapr_entry_shape` 用 `typ`。這只是參數名,不算不對齊。
- 測試 ③' 沿用 ③ 的 `_SgRepo`、`add_entry`、`_sg_eval`、`_sg_codes` 寫法,命名成 `[S69] ③'` 並附 `★前置★` 斷言,跟同函式內其他編號一樣。

**3. 第二種做法:沒有。**
- 兩條撤銷判斷(逐筆判、回溯判)收成同一支 `_secapr_signer_revoked`。證據圍欄和核可鏈共用同一支 null 判斷。上一輪的 `_sec_no_expiry` 加上兩處手寫比對,等於重複的做法,這輪已經合併。
- `retro=False` 這個布林旗標讓一支函式有兩種模式。專案裡 `_secapr_*` 沒有同形的先例,但它不是新的流程或新的依賴,我不算第二種做法。⚠ 交編排者決定要不要追究。
- 沒有引入新依賴,也沒有新的 I/O 路徑。

不對齊共 1 條,其中 major 0 條
