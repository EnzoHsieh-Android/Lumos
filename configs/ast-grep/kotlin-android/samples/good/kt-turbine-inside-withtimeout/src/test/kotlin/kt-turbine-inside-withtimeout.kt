package sample.test

import app.cash.turbine.test
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withTimeout
import kotlin.time.Duration.Companion.seconds
import org.junit.Assert.assertEquals
import org.junit.Test

class FeedTurbineTest {
    // 好例一:逾時交給 Turbine 自己的 timeout 參數
    @Test
    fun firstItemWithTurbineTimeout() = runTest {
        val vm = FeedModel(FakeFeed())
        vm.items.test(timeout = 5.seconds) {
            assertEquals(3, awaitItem().size)
        }
    }

    // 好例二:withTimeout 只包一般的 suspend 呼叫,沒有 Turbine
    @Test
    fun loadWithinTimeout() = runTest {
        val feed = FakeFeed()
        val items = withTimeout(1_000) { feed.load() }
        assertEquals(3, items.size)
    }

    // 好例三:test 在外、withTimeout 在 test 裡面包一般呼叫
    @Test
    fun timeoutInsideTurbine() = runTest {
        val vm = FeedModel(FakeFeed())
        vm.items.test {
            val first = withTimeout(1_000) { awaitItem() }
            assertEquals(3, first.size)
        }
    }
}

// 容易誤報:withTimeout 與 Turbine 的 test 是並排的兩句,沒有包住
class FeedSequentialTest {
    @Test
    fun loadThenObserve() = runTest {
        val vm = FeedModel(FakeFeed())
        withTimeout(1_000) { vm.refresh() }
        vm.items.test(timeout = 3.seconds) {
            assertEquals(3, awaitItem().size)
        }
    }
}
