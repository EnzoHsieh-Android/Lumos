package sample.test

import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class NumberSourceTest {
    @Test
    fun emitsNumbers() = runTest {
        val source = NumberSource()
        val values = mutableListOf<Int>()
        launch(UnconfinedTestDispatcher(testScheduler)) {
            source.numbers.toList(values) // BAD
        }
        source.emit(1)
        assertEquals(listOf(1), values)
    }

    @Test
    fun emitsInOrder() = runTest {
        val source = NumberSource()
        val values = mutableListOf<Int>()
        launch {
            source.numbers.toList(values) // BAD
        }
        source.emit(1)
        source.emit(2)
        advanceUntilIdle()
        assertEquals(listOf(1, 2), values)
    }
}
