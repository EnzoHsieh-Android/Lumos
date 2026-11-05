class VmTest {
    @Test fun a() = runTest {
        val values = mutableListOf<Int>()
        launch { vm.state.collect { values += it } } // BAD
        vm.load()
    }
    @Test fun b() = runTest {
        val values = mutableListOf<Int>()
        launch(UnconfinedTestDispatcher(testScheduler)) { vm.state.toList(values) } // BAD
    }
}
