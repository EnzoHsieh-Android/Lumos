// 路徑證明:src/androidUnitTest 也算測試碼
class KmpandroidUnitTestSleepTest {
    @get:Rule val composeTestRule = createComposeRule()
    @Test fun t() {
        Thread.sleep(1_000) // BAD
        composeTestRule.onNodeWithTag("x").assertExists()
    }
}
