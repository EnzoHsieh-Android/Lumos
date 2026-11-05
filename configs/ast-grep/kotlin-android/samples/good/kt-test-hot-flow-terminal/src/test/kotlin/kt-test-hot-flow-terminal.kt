package sample.test

import app.cash.turbine.test
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class ProfileHotFlowSafeTest {
    // 好例一:Turbine 收熱流
    @Test
    fun stateWithTurbine() = runTest {
        val vm = ProfileModel(FakeRepo())
        vm.uiState.test {
            assertEquals(UiState.Loading, awaitItem())
        }
    }

    // 好例二:放進 backgroundScope.launch 收集
    @Test
    fun eventsInBackground() = runTest {
        val vm = ProfileModel(FakeRepo())
        val seen = mutableListOf<Event>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) {
            vm.events.collect { seen += it }
        }
        vm.refresh()
        assertEquals(1, seen.size)
    }

    // 好例三:冷流(名稱不像熱流)toList 會正常結束
    @Test
    fun coldFlowToList() = runTest {
        val repo = FakeRepo()
        val items = repo.pagedItems.toList()
        assertEquals(3, items.size)
    }

    // 好例四:熱流先 take 再收集
    @Test
    fun stateTakeFirst() = runTest {
        val vm = ProfileModel(FakeRepo())
        val firstTwo = vm.uiState.take(2).toList()
        assertEquals(2, firstTwo.size)
    }
}

// 容易誤報:讀熱流的目前值 .value,不是 collect/toList
class ProfileStateValueTest {
    @Test
    fun startsLoading() = runTest {
        val vm = ProfileModel(FakeRepo())
        assertEquals(UiState.Loading, vm.uiState.value)
    }
}
