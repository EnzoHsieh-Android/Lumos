package sample.test

import app.cash.turbine.test
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.time.Duration.Companion.seconds
import org.junit.Assert.assertEquals
import org.junit.Test

class FeedTurbineTimeoutTest {
    @Test
    fun firstItemWithinTimeout() = runTest {
        val vm = FeedModel(FakeFeed())
        withTimeout(1_000) { // BAD
            vm.items.test {
                assertEquals(3, awaitItem().size)
            }
        }
    }

    @Test
    fun maybeItem() = runTest {
        val vm = FeedModel(FakeFeed())
        withTimeoutOrNull(5.seconds) { // BAD
            vm.items.test(name = "feed") {
                assertEquals(3, awaitItem().size)
                cancelAndIgnoreRemainingEvents()
            }
        }
    }
}
