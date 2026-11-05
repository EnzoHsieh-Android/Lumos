fun a(dto: UserDto) = dto.user?.name ?: "" // GOOD
fun b(response: Response<User>) = if (response.isSuccessful) response.body()!! else null // GOOD body()!! 歸 kt-retrofit-body-bang 管,且已先看 isSuccessful
fun c(view: View) = view.parent!!.toString() // GOOD 不是 API 物件
