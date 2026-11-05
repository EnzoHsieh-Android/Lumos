package sample.test

import kotlinx.coroutines.test.runTest
import org.junit.Test

class ProfileRepositoryNoAssertTest {
    @Test // BAD
    fun savesProfile() {
        val repo = ProfileRepository(FakeDb())
        repo.save(Profile("ann"))
    }

    @Test // BAD
    fun loadsProfile() = runTest {
        val repo = ProfileRepository(FakeDb())
        val profile = repo.load("ann")
        println(profile)
    }
}
