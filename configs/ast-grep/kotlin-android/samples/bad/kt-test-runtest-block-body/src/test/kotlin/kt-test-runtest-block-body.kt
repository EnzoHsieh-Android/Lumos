package sample.test

import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test
import kotlin.time.Duration.Companion.seconds

class CounterBlockBodyTest {
    @Test
    fun increments() {
        runTest { // BAD
            val counter = Counter()
            counter.increment()
            assertEquals(1, counter.value)
        }
    }

    @Test
    fun incrementsWithTimeout() {
        runTest(timeout = 5.seconds) { // BAD
            val counter = Counter()
            counter.increment()
            assertEquals(1, counter.value)
        }
    }

    @Test
    fun incrementsInScope() {
        val scope = TestScope()
        scope.runTest { // BAD
            val counter = Counter()
            counter.increment()
            assertEquals(1, counter.value)
        }
    }
}
