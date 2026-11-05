package sample.test

import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.Dispatchers
import org.junit.Assert.assertTrue
import org.junit.Test

class PollerRealTimeTest {
    @Test
    fun pollsAfterDelay() = runBlocking {
        val poller = Poller()
        poller.start()
        delay(1_000) // BAD
        assertTrue(poller.polled)
    }

    @Test
    fun pollsOnIo() = runBlocking(Dispatchers.IO) {
        val poller = Poller()
        poller.start()
        delay(500L) // BAD
        assertTrue(poller.polled)
    }

    @Test
    fun measuresElapsed() {
        val start = System.currentTimeMillis() // BAD
        Poller().pollOnce()
        val tookNs = System.nanoTime() // BAD
        assertTrue(tookNs > 0 && start > 0)
    }
}
