// 路徑證明:src/androidInstrumentedTest 也算測試碼
class KmpandroidInstrumentedTestSleepTest {
    @get:Rule val composeTestRule = createComposeRule()
    @Test fun t() {
        Thread.sleep(1_000) // BAD
        composeTestRule.onNodeWithTag("x").assertExists()
    }
}
