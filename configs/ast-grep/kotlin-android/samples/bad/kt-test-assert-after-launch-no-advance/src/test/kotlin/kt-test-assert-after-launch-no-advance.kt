package sample.test

import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CounterLaunchTest {
    private val scope = TestScope()

    @Test
    fun incrementWithoutAdvance() = runTest {
        val counter = Counter()
        launch { counter.increment() }
        assertEquals(1, counter.value) // BAD
    }

    @Test
    fun loadJobNotJoined() = scope.runTest {
        val loader = Loader()
        val job = launch { loader.load() }
        loader.prepare()
        assertTrue(loader.loaded) // BAD
    }
}
