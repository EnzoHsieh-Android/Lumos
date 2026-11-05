package sample.test

import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.flow.take
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class NumberSourceBackgroundTest {
    @Test
    fun emitsNumbers() = runTest {
        val source = NumberSource()
        val values = mutableListOf<Int>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) {
            source.numbers.toList(values)
        }
        source.emit(1)
        assertEquals(listOf(1), values)
    }

    // 有 take 限量,收滿就結束
    @Test
    fun takesTwo() = runTest {
        val source = NumberSource()
        val values = mutableListOf<Int>()
        launch {
            source.numbers.take(2).toList(values)
        }
        source.emit(1)
        source.emit(2)
        advanceUntilIdle()
        assertEquals(listOf(1, 2), values)
    }

    // Job 存起來,測試自己取消
    @Test
    fun cancelsCollector() = runTest {
        val source = NumberSource()
        val values = mutableListOf<Int>()
        val job = launch(UnconfinedTestDispatcher(testScheduler)) {
            source.numbers.toList(values)
        }
        source.emit(1)
        job.cancelAndJoin()
        assertEquals(listOf(1), values)
    }
}

// 容易誤報:冷流先 take 再直接 toList,不在 launch 裡
class NumberSourceDirectTest {
    @Test
    fun firstThree() = runTest {
        val values = NumberSource().cold.take(3).toList()
        assertEquals(listOf(1, 2, 3), values)
    }
}
