channel = Math.floor(Math.random()*1000000)

create_room_comet = ->
	arg = "comet=online_users,room_online_users,room_content&channel=#{channel}&room=#{window.room_name}"
	$.getJSON "/comet?uri=#{window.uri}&#{arg}", (data) ->
		for key, val of data
			if key == 'online_users'
				online_users data.online_users
			else if key == 'room_online_users'
				room_online_users data.room_online_users
			else if key == 'type' and data.type == 'add_content'
				room_content data.content
		create_room_comet()

online_users = (content) ->
	html = ''
	for val in content
		html += "<span>#{val}</span>"
	$('#global_online_user .user_list').html(html)

room_online_users = (content) ->
	html = ''
	for val in content
		html += "<span>#{val}</span>"
	$('#room_online_user .user_list').html(html)

room_content = (content) ->
	html = "<tr>
			<td>#{content.user}</td>
			<td>#{content.content}</td>
			<td>#{content.created}</td>
			</tr>
		"
	$('#chat_content table tr:last-child').after(html)

$ ->
	create_room_comet()
	$('#post_content').bind 'submit', (evt) ->
		evt.preventDefault()
		data = $(this).serialize()
		$.post(
			$(this).attr('action')
			data
			(result) -> console.log(result)
			'json'
		)
