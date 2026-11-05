package sample.test

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.onAllNodesWithTag
import org.junit.Rule
import org.junit.Test

class SplashWaitTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    // 好例一:waitUntil 等條件成立
    @Test
    fun splashDisappears() {
        composeTestRule.setContent { SplashScreen() }
        composeTestRule.waitUntil(timeoutMillis = 2_000) {
            composeTestRule.onAllNodesWithTag("home").fetchSemanticsNodes().isNotEmpty()
        }
        composeTestRule.onNodeWithTag("home").assertIsDisplayed()
    }

    // 好例二:推進 Compose 的 mainClock
    @Test
    fun animationEnds() {
        composeTestRule.mainClock.autoAdvance = false
        composeTestRule.setContent { SplashScreen() }
        composeTestRule.mainClock.advanceTimeBy(2_000)
        composeTestRule.onNodeWithTag("home").assertIsDisplayed()
    }

    // 好例三:假時鐘自己的 sleep 方法,不是 Thread.sleep
    @Test
    fun fakeClockSleep() {
        val clock = FakeClock()
        clock.sleep(500)
        check(clock.now == 500L)
    }
}

// 容易誤報:協程用虛擬時間推進,沒有真的睡
class DebounceVirtualTimeTest {
    @Test
    fun debouncesInput() = runTest {
        val vm = SearchModel(this)
        vm.type("a")
        advanceTimeBy(300)
        runCurrent()
        assertEquals("a", vm.query)
    }
}
