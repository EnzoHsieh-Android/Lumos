class VmTest {
    @Test fun a() = runTest {
        val values = mutableListOf<Int>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { vm.state.toList(values) } // GOOD
        assertEquals(listOf(0), values)
    }
    @Test fun b() = runTest {
        val values = mutableListOf<Int>()
        launch { vm.state.take(2).toList(values) } // GOOD
        vm.load()
        advanceUntilIdle()
        assertEquals(2, values.size)
    }
    @Test fun c() = runTest {
        val values = mutableListOf<Int>()
        val job = launch { vm.state.collect { values += it } } // GOOD
        vm.load()
        advanceUntilIdle()
        job.cancelAndJoin()
        assertTrue(values.isNotEmpty())
    }
}

// 容易誤報:runTest 裡 launch 收集,但用 first { } 收到就結束
class VmFirstTest {
    @Test fun d() = runTest {
        val loaded = async { vm.state.first { it > 0 } } // GOOD
        launch { vm.state.first { it > 0 } } // GOOD
        vm.load()
        advanceUntilIdle()
        assertEquals(1, loaded.await())
    }
}
