suspend fun loadHome(api: Api, userId: Long): Home {
    val user = api.user(userId)
    val feed = api.feed(page = 1) // BAD:跟 user 沒關係卻串著等
    return Home(user, feed)
}

suspend fun loadCart(repo: Repo, ads: Ads): Cart {
    val items = repo.items()
    val banner = ads.banner("cart") // BAD
    return Cart(items, banner)
}
