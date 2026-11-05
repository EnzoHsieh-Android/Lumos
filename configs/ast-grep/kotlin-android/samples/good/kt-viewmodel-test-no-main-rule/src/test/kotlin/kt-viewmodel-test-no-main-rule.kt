package sample.test

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test

// 好例一:用 MainDispatcherRule 換 Main
class LoginViewModelRuleTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun loginSucceeds() = runTest {
        val vm = LoginViewModel(FakeAuth())
        vm.login("amy", "pw")
        assertEquals(LoginState.Success, vm.state.value)
    }
}

// 好例二:@Before 手動 setMain
class ProfileViewModelSetMainTest {
    @Before
    fun setUp() {
        Dispatchers.setMain(StandardTestDispatcher())
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun loadsProfile() {
        val vm = ProfileViewModel(FakeRepo())
        vm.load()
        assertEquals("amy", vm.name.value)
    }
}

// 好例三:繼承共用基底類別(基底負責換 Main)
class SettingsViewModelTest : BaseViewModelTest() {
    @Test
    fun togglesDarkMode() {
        val vm = SettingsViewModel(FakePrefs())
        vm.toggleDark()
        assertEquals(true, vm.dark.value)
    }
}

// 好例四:測試的不是 ViewModel 建構(只是名稱含 Model 的普通類別)
class PriceModelTest {
    @Test
    fun formatsPrice() {
        val model = PriceModel(100)
        assertEquals("$1.00", model.display())
    }
}

// 容易誤報:專案自己命名的換 Main Rule(CoroutineTestRule、TestDispatcherRule…)
class FeedViewModelTest {
    @get:Rule val coroutineRule = CoroutineTestRule()
    @Test fun t() = runTest { FeedViewModel(FakeRepo()).load() }
}
class CartViewModelTest {
    @get:Rule val rule = TestDispatcherRule()
    @Test fun t() = runTest { CartViewModel().add() }
}

// 容易誤報:JUnit5 用 Extension 換 Main
@ExtendWith(MainDispatcherExtension::class)
class SearchViewModelTest {
    @Test fun t() = runTest { SearchViewModel().query("a") }
}

// 容易誤報:Robolectric 測試有真的 Main looper
@RunWith(AndroidJUnit4::class)
class A5ViewModelTest {
    @Test fun t() { A5ViewModel().load() }
}
