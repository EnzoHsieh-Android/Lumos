package sample.test

import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class ProfileHotFlowTest {
    @Test
    fun stateToList() = runTest {
        val vm = ProfileModel(FakeRepo())
        val all = vm.uiState.toList() // BAD
        assertEquals(2, all.size)
    }

    @Test
    fun eventsCollect() = runTest {
        val vm = ProfileModel(FakeRepo())
        val seen = mutableListOf<Event>()
        vm.events.collect { seen += it } // BAD
        assertEquals(1, seen.size)
    }

    @Test
    fun sharedFlowToList() = runTest {
        val bus = EventBus()
        val got = bus.messagesSharedFlow.toList() // BAD
        assertEquals(0, got.size)
    }
}
