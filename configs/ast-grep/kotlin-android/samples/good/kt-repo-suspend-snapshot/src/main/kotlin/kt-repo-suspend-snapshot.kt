package good

// case: stream-read
class ModelRepository2 { fun getModelStream(): Flow<Model> = dao.observe() }
// case: suspend-write
class ModelRepository3 { suspend fun saveModel(m: Model) { } }
// case: suspend-get-in-non-repo
class TokenProvider { suspend fun getToken(): String = "" }
