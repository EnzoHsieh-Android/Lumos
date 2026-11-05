package sample.test

import kotlinx.coroutines.delay
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class PollerVirtualTimeTest {
    // 好例一:runTest 裡的 delay 走虛擬時間
    @Test
    fun pollsAfterVirtualDelay() = runTest {
        val poller = Poller(this)
        poller.start()
        delay(1_000)
        assertTrue(poller.polled)
    }

    // 好例二:用 advanceTimeBy 推進、讀 currentTime 而不是系統時鐘
    @Test
    fun measuresVirtualElapsed() = runTest {
        val poller = Poller(this)
        poller.start()
        advanceTimeBy(500)
        assertEquals(500L, currentTime)
    }

    // 好例三:注入假時鐘
    @Test
    fun usesFakeClock() {
        val clock = FakeClock(now = 1_000L)
        val poller = Poller(clock = clock)
        clock.advance(500)
        assertEquals(1_500L, poller.lastSeen())
    }
}

// 容易誤報:delay 寫在 runTest 裡的 launch(虛擬時間),不在 runBlocking 裡
class SearchDebounceTest {
    @Test
    fun debouncesTyping() = runTest {
        val vm = SearchModel(this)
        launch {
            delay(300)
            vm.type("a")
        }
        advanceUntilIdle()
        assertEquals("a", vm.query)
    }
}
