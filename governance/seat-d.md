# Code Review — payload-L-early.patch (11 commits, LandmarkMember.Server / LandmarkMember.Pos)

Reviewed against the full repo snapshot (not just diff hunks) — cross-checked every SQL/behavior claim
in commit messages and doc updates against the actual call sites (InvoiceSupplementRepository,
RegistrationService, SmsTokenService, EventLogWriter, AdminKeyMiddleware, Program.cs DI registrations).

## Part 1 — Per-file verdicts

Files that appear in multiple commits are judged once, on the net cumulative diff.

| 檔案 | 判定 | 一句話理由 |
|---|---|---|
| `LandmarkMember.Pos/Repositories/Implementations/ReconciliationRepository.cs` | clean | SVC_DESK→`NOT EXISTS(InvoiceOrders…InvFlag='SUPPLEMENT')` upgrade verified correct: `InvoiceSupplementService` writes `Orders`+`InvoiceOrders` in one `SqlTransaction` (no partial-write race), so the exclusion condition can't ever see an orphaned half-written 補登 row. |
| `LandmarkMember.Pos/appsettings.json` | clean | Pure schedule-time bump 22:30→23:00, within `ReconciliationSelfHealService`'s `Clamp(hour,0,23,…)` bound. |
| `LandmarkMember.Server/Repositories/Implementations/SchedulerHeartbeatRepository.cs` | clean | Comment-only, no behavior change. |
| `LandmarkMember.Server/Repositories/Implementations/EventLogRepository.cs` | clean | `DateTime.SpecifyKind(CreatedAt, Utc)` fix verified against non-nullable `ReconciliationLogDto.CreatedAt` (compiles, no null issue) and against frontend `dayjs(r.createdAt)` call sites — adding `Z` is exactly what makes dayjs stop mis-parsing UTC as local. |
| `LandmarkMember.Server/Repositories/Implementations/CustomerRepository.cs` | minor | `UpdateLineBindingAsync` NULLIF/ISNULL fix is correct. But the two new methods added later in the same file (`GetTotalMemberCountAsync`, `GetDailyNewMemberCountsAsync`) don't apply the `CardStatus='Y' AND ISNULL(IsBlacklist,'N')='N'` filter that every other read method in this file uses — see finding F1. |
| `LandmarkMember.Server/Repositories/Interfaces/ICustomerRepository.cs` | clean | Interface additions match implementation signatures exactly. |
| `LandmarkMember.Server/Configuration/SmsSettings.cs` | clean | Net no-op (5→15 then reverted 15→5 same day); final state correct. |
| `LandmarkMember.Server/appsettings.Production.json` | clean | Net no-op, mirrors `SmsSettings.cs`. |
| `LandmarkMember.Server/appsettings.json` | clean | Net no-op, mirrors `SmsSettings.cs`. |
| `LandmarkMember.Server/Controllers/Admin/AdminSmsLookupController.cs` | minor | Functionally correct (verified `>` vs `>=` expiry semantics against `SmsTokenService.ExpiresAt` and `RegistrationService`'s `GetLatestUnverifiedAsync` window — all three now agree). IPv4-mapped-IPv6 normalization is a genuine, verified fix (matches `EventLogWriter`'s 15-char `ClientIP` truncation). Only concern is authorization scope — see finding F2. |
| `LandmarkMember.Server/Models/DTOs/Admin/SmsLookupDto.cs` | clean | All properties verified to camelCase-match every `smsResult.*` frontend reference. |
| `LandmarkMember.Server/Repositories/Implementations/SmsLogRepository.cs` | clean | `GetLatestByPhoneAsync` column list matches `SmsLog` entity exactly. |
| `LandmarkMember.Server/Repositories/Interfaces/ISmsLogRepository.cs` | clean | Interface addition matches implementation. |
| `LandmarkMember.Server/Controllers/Admin/AdminMemberStatsController.cs` | clean | `days` clamp [1,365] correct; route doesn't collide with any other `api/admin/*` controller. |
| `LandmarkMember.Server/Models/DTOs/Admin/MemberStatsDto.cs` | clean | All properties verified to camelCase-match `memberStats.*` frontend reference. |
| `LandmarkMember.Server/wwwroot/admin/logs/index.html` | clean | New tabs (SMS 查詢/會員統計), RWD breakpoint, `table.fit` fix, badge flex-wrap fix, POS date default — all scoped CSS/JS additions, no structural breakage found; `api()` helper's `json.data` unwrap pattern used consistently. |
| `docs/landmark-knowledge/Systems/維運儀表板.md` | clean | Tab count / feature descriptions track the final code state accurately across all revisions in this patch. |
| `docs/landmark-knowledge/Projects/對帳假差異自癒_計劃.md` | clean | Schedule-time note (22:30→23:00) matches `appsettings.json` + `SchedulerHeartbeatRepository.cs` comment. |
| `docs/landmark-knowledge/Verification/2026-07-16_對帳假差異自癒_lab_E2E.md` | clean | Text-only time reference update, consistent. |
| `docs/landmark-knowledge/Systems/認證與註冊.md` | clean | RegisterSource fix description matches the actual SQL. |
| `docs/landmark-knowledge/Systems/SMS簡訊.md` | clean | Parameter table reflects final state (ExpiryMinutes=5) after the same-day revert; OTP lookup tool section matches controller behavior. |

## Part 2 — Findings

### F1 (minor) — `會員統計` counts include cancelled/blacklisted customers, inconsistent with the rest of the file

**File:** `LandmarkMember.Server/Repositories/Implementations/CustomerRepository.cs:190-206`

```csharp
public async Task<IEnumerable<DailyNewMemberDto>> GetDailyNewMemberCountsAsync(int days)
{
    const string sql = @"
        SELECT CONVERT(varchar(10), CreateDate, 23) AS [Date], COUNT(*) AS [Count]
        FROM Customer
        WHERE CreateDate >= DATEADD(DAY, -(@Days - 1), CAST(GETDATE() AS date))
        GROUP BY CONVERT(varchar(10), CreateDate, 23)
        ORDER BY [Date] DESC";
    ...
}

public async Task<int> GetTotalMemberCountAsync()
{
    const string sql = "SELECT COUNT(*) FROM Customer";
    ...
}
```

Every other read method in this same file (`GetByCustNoAsync`, `GetByLineUserIdAsync`, `GetByPhoneAsync`, lines 47-84) filters `WHERE ... AND CardStatus = 'Y' AND ISNULL(IsBlacklist, 'N') = 'N'` before treating a row as "a member". The two new stats methods select `COUNT(*)` over the raw table with no such filter.

**Concrete scenario:** a customer whose card gets cancelled (`CardStatus='N'`) or who gets blacklisted (`IsBlacklist='Y'`) is, by every other part of this codebase's convention, no longer "a member" (they can't log in — `GetByCustNoAsync`/`GetByLineUserIdAsync`/`GetByPhoneAsync` would all return null for them). But they are still counted in `會員統計` → `會員總數` and in whichever day's row their `CreateDate` falls into, forever. Operationally: the "昨天新增了多少會員" headline number the dashboard shows to whoever reads it daily includes registrations that were subsequently cancelled/blacklisted, with no way to tell from the UI that the number doesn't mean the same thing as "member" means everywhere else in this system.

### F2 (minor) — OTP lookup endpoint shares the same broadly-distributed key as read-only log viewing, with no additional throttle on the lookup itself

**File:** `LandmarkMember.Server/Controllers/Admin/AdminSmsLookupController.cs:684-726`

`AdminSmsLookupController.Lookup` is gated only by `AdminKeyMiddleware` (`?key=AdminSettings.LogViewerKey`), the same single shared secret used for `/admin/logs` dashboard viewing, invoice supplement, order void/waive, etc. (per `docs/landmark-knowledge/Systems/QA驗收清單.md:139` and `發票補登.md:176`, this key is explicitly described as "跟 /admin/logs/ 同把,存在...GitHub secret" and shared with 服務台/後台 broadly). The endpoint itself has no per-phone or per-caller rate limit (unlike the customer-facing SMS-send path, which has `MaxSendsPerHour`/`IpMaxSendsPerHour`), so any holder of that key can query the currently-valid OTP for **any** phone number with no additional friction beyond the one shared key.

**Concrete scenario:** anyone in possession of `LogViewerKey` (documented as shared across 服務台/後台 staff for unrelated purposes like viewing error logs) can call `GET /api/admin/sms/lookup?phone=<victim phone>&key=<key>` to obtain the victim's current OTP code, then — using their own, unrelated LINE login — call the public (non-admin-gated) `POST /api/internal/register/verify-sms` with that phone+code to bind their own `LineUserId` to the victim's `Customer` record, fully taking over the account (points balance, coupons, PII). The lookup step is audited (`Event_Log` `ADMIN_SMS_LOOKUP`), but the actual takeover step (the `verify-sms` call) is not linked to the admin key in any way and leaves no trace back to who read the OTP.

This is a known, explicitly-reasoned-about tradeoff by the author (the controller's own doc comment says "看得到OTP=帳號接管向量,留痕不可省", and audit logging was added as the mitigation), and it's consistent with — not a new departure from — this codebase's existing precedent of gating other high-impact actions (creating invoices, voiding orders) behind the same single key. It is also arguably inherent to the feature's stated purpose (staff must be able to read the real code to relay it by phone when SMS is blocked). Flagging as **minor** rather than major/blocker because it doesn't deviate from the established trust model and the risk was consciously accepted with a stated mitigation — but the mitigation (audit-after-the-fact) does not actually prevent the described takeover path, which is worth the submitter's awareness going forward (e.g. a future hardening could require entering the account's registered store/last-4-digits as a secondary check, or scope this specific endpoint to a narrower key).

## No blockers or majors found

Every SQL query, expiry-semantics change, and transaction-safety claim in the commit messages was independently verified against the actual call sites rather than taken at face value, and all held up. The two findings above are both `minor` per the stated severity anchor (measurement-definition ambiguity and an already-accepted, already-mitigated authorization tradeoff — neither is "the code does the wrong thing" or "a contract is silently dropped").
