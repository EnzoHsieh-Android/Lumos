package sample.test

import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class CounterLaunchAdvancedTest {
    // 好例一:斷言前先推進排程器
    @Test
    fun incrementThenAdvance() = runTest {
        val counter = Counter()
        launch { counter.increment() }
        advanceUntilIdle()
        assertEquals(1, counter.value)
    }

    // 好例二:等 job 結束再斷言
    @Test
    fun loadJobJoined() = runTest {
        val loader = Loader()
        val job = launch { loader.load() }
        job.join()
        assertTrue(loader.loaded)
    }

    // 好例三:runTest 用 Unconfined,launch 立刻執行
    @Test
    fun unconfinedRunsEagerly() = runTest(UnconfinedTestDispatcher()) {
        val counter = Counter()
        launch { counter.increment() }
        assertEquals(1, counter.value)
    }

    // 好例四:runCurrent 推進目前時間點的工作
    @Test
    fun runCurrentBeforeAssert() = runTest {
        val counter = Counter()
        launch { counter.increment() }
        runCurrent()
        assertEquals(1, counter.value)
    }
}

// 容易誤報:用 async/await 拿結果再斷言,await 本身就等到完成
class LoaderAsyncTest {
    @Test
    fun loadsViaAsync() = runTest {
        val loader = Loader()
        val items = async { loader.load() }
        assertEquals(3, items.await().size)
    }
}
