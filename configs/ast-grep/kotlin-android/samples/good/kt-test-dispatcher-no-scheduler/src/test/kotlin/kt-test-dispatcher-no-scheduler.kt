package sample.test

import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

// 好例一:傳入同一個排程器,虛擬時間只有一份
class RepoSharedSchedulerTest {
    @Test
    fun loadsWithSharedScheduler() = runTest {
        val io = StandardTestDispatcher(testScheduler)
        val repo = Repo(io)
        repo.refresh()
        advanceUntilIdle()
        assertEquals(3, repo.count())
    }

    // 好例二:寫在 runTest 參數位置的 dispatcher,由 runTest 自己接管
    @Test
    fun unconfinedAsRunTestArgument() = runTest(UnconfinedTestDispatcher()) {
        val repo = Repo(UnconfinedTestDispatcher(testScheduler))
        repo.refresh()
        assertEquals(3, repo.count())
    }
}

// 好例三:類別已換 Main,dispatcher 會取用 Main 的排程器
class RepoWithMainRuleTest {
    @get:Rule
    val mainRule = MainDispatcherRule()

    @Test
    fun loadsWithMainReplaced() = runTest {
        val io = StandardTestDispatcher()
        val repo = Repo(io)
        repo.refresh()
        advanceUntilIdle()
        assertEquals(3, repo.count())
    }
}
