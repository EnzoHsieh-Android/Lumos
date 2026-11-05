// 路徑證明:src/jvmTest 也算測試碼
class KmpjvmTestSleepTest {
    @get:Rule val composeTestRule = createComposeRule()
    @Test fun t() {
        Thread.sleep(1_000) // BAD
        composeTestRule.onNodeWithTag("x").assertExists()
    }
}
