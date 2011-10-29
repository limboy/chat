channel = Math.floor(Math.random()*1000000)

create_chat_comet = ->
    arg = "comet=room_online_users_count_all,room_content_all&channel=#{channel}"
    $.getJSON "/comet?uri=#{window.uri}&#{arg}", (result) ->
        if result.type == 'room_online_users'
            room_online_users_count_all result.data
        else if result.type == 'add_content'
            room_content_all result.data
        create_chat_comet()

create_room_comet = ->
    arg = "comet=online_users,room_online_users,room_content&channel=#{channel}&room_id=#{window.room_id}"
    $.getJSON "/comet?uri=#{window.uri}&#{arg}", (result) ->
        if result.type == 'online_users'
            online_users result.data
        else if result.type == 'room_online_users'
            room_online_users result.data
        else if result.type == 'add_content'
            room_content result.data
        create_room_comet()

room_online_users_count_all = (content) ->
    for room_id, users of content
        $("#room-#{room_id} .header span").text("(#{users.length}人在线)")

room_content_all = (content) ->
    $body = $("#room-#{content.room_id} .body")
    $body.find('ul').append("<li class='new' title='#{content.user} #{content.created}'>#{content.content}</li>")
    if $body.find('ul li').length > 5
        $body.find('ul li:first-child').remove()

online_users = (content) ->
    html = ''
    for val in content
        html += "<span>#{val}</span>"
    $('#global_online_user .user_list').html(html)

room_online_users = (content) ->
    html = ''
    for room_id, val of content
        for item in val
            html += "<span>#{val}</span>"
    $('#room_online_user .user_list').html(html)

room_content = (content) ->
    html = "<tr>
            <td>#{content.user}</td>
            <td>#{content.content}</td>
            <td>#{content.created}</td>
            </tr>
        "
    $('#chat_content table tbody').append(html)
    $("#chat_content table tbody tr:last-child").get(0).scrollIntoView()

$ ->
    if $('#chat_content tbody tr').length
        $('#chat_content tbody tr:last-child').get(0).scrollIntoView()

    $('#post_content').bind 'submit', (evt) ->
        evt.preventDefault()
        data = $(this).serialize()
        $.post(
            $(this).attr('action')
            data
            (result) -> $('#post_content input[name="content"]').val('')
            'json'
        )
    $('.add_room').bind 'click', (evt) ->
        title = prompt('要创建的包间名')
        if title
            $.post(
                '/chat',
                {title: title},
                (result) ->
                    if result.status == 'ok'
                        window.location.href = result.content.url
                    else
                        msg = ''
                        for key,val of result.content
                            msg += val + '\n'
                        alert msg
                ,
                'json'
            )
