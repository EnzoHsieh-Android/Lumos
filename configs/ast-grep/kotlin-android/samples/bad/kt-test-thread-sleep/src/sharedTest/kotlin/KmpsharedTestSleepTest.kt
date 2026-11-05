// 路徑證明:src/sharedTest 也算測試碼
class KmpsharedTestSleepTest {
    @get:Rule val composeTestRule = createComposeRule()
    @Test fun t() {
        Thread.sleep(1_000) // BAD
        composeTestRule.onNodeWithTag("x").assertExists()
    }
}
