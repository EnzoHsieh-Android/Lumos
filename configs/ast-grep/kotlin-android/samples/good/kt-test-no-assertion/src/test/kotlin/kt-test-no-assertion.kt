package sample.test

import app.cash.turbine.test
import kotlin.test.assertFailsWith
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class ProfileRepositoryAssertTest {
    @Test
    fun savesProfile() {
        val repo = ProfileRepository(FakeDb())
        repo.save(Profile("ann"))
        assertEquals(1, repo.count())
    }

    // 預期丟例外:用 assertFailsWith
    @Test
    fun rejectsBlankName() {
        val repo = ProfileRepository(FakeDb())
        assertFailsWith<IllegalArgumentException> { repo.save(Profile("")) }
    }

    // 預期丟例外:用 @Test(expected = …)
    @Test(expected = IllegalStateException::class)
    fun failsWhenClosed() {
        val repo = ProfileRepository(FakeDb())
        repo.close()
        repo.save(Profile("ann"))
    }

    // Turbine 的 test { awaitItem() } 算斷言
    @Test
    fun emitsProfile() = runTest {
        val repo = ProfileRepository(FakeDb())
        repo.profiles.test {
            repo.save(Profile("ann"))
            assertEquals("ann", awaitItem().name)
        }
    }
}

// 容易誤報:斷言用 Kotest 的中綴 shouldBe,沒有 assert 字樣
class ProfileKotestStyleTest {
    @Test
    fun countsProfiles() {
        val repo = ProfileRepository(FakeDb())
        repo.save(Profile("ann"))
        repo.count() shouldBe 1
    }
}
