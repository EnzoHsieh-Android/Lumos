fun a(dto: UserDto) = dto.user!!.name // BAD
fun b(response: PageResponse) = response.data!!.items.first() // BAD
