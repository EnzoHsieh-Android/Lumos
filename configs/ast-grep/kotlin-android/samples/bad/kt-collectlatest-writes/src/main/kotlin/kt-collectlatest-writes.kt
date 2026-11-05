suspend fun a() {
    events.collectLatest { db.insert(it) } // BAD
    changes.collectLatest { change -> // BAD
        val x = transform(change)
        repo.saveAll(x)
    }
}
