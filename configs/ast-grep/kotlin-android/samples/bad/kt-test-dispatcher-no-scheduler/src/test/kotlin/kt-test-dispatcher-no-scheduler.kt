package sample.test

import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import kotlin.time.Duration.Companion.seconds
import org.junit.Assert.assertEquals
import org.junit.Test

class RepoDispatcherTest {
    private val scope = TestScope()

    @Test
    fun loadsWithOwnStandardDispatcher() = runTest {
        val io = StandardTestDispatcher() // BAD
        val repo = Repo(io)
        repo.refresh()
        advanceUntilIdle()
        assertEquals(3, repo.count())
    }

    @Test
    fun loadsWithOwnUnconfinedDispatcher() = runTest(timeout = 5.seconds) {
        val repo = Repo(UnconfinedTestDispatcher()) // BAD
        repo.refresh()
        assertEquals(3, repo.count())
    }

    @Test
    fun scopedRunTest() = scope.runTest {
        val bg = StandardTestDispatcher() // BAD
        val repo = Repo(bg)
        assertEquals(0, repo.count())
    }
}
