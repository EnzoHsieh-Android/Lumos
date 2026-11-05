package sample.test

import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class LoginViewModelTest { // BAD
    @Test
    fun loginSucceeds() = runTest {
        val vm = LoginViewModel(FakeAuth())
        vm.login("amy", "pw")
        assertEquals(LoginState.Success, vm.state.value)
    }
}

class ProfileViewModelTest { // BAD
    private val vm = ProfileViewModel(FakeRepo())

    @Test
    fun loadsProfile() {
        vm.load()
        assertEquals("amy", vm.name.value)
    }
}
