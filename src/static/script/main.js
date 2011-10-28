var channel, create_chat_comet, create_room_comet, online_users, room_content, room_content_all, room_online_users, room_online_users_count_all;
channel = Math.floor(Math.random() * 1000000);
create_chat_comet = function() {
  var arg;
  arg = "comet=room_online_users_count_all,room_content_all&channel=" + channel;
  return $.getJSON("/comet?uri=" + window.uri + "&" + arg, function(result) {
    if (result.type === 'room_online_users') {
      room_online_users_count_all(result.data);
    } else if (result.type === 'add_content') {
      room_content_all(result.data);
    }
    return create_chat_comet();
  });
};
create_room_comet = function() {
  var arg;
  arg = "comet=online_users,room_online_users,room_content&channel=" + channel + "&room_id=" + window.room_id;
  return $.getJSON("/comet?uri=" + window.uri + "&" + arg, function(result) {
    if (result.type === 'online_users') {
      online_users(result.data);
    } else if (result.type === 'room_online_users') {
      room_online_users(result.data);
    } else if (result.type === 'add_content') {
      room_content(result.data);
    }
    return create_room_comet();
  });
};
room_online_users_count_all = function(content) {
  var room_id, users, _results;
  _results = [];
  for (room_id in content) {
    users = content[room_id];
    _results.push($("#room-" + room_id + " .header span").text("(" + users.length + ")"));
  }
  return _results;
};
room_content_all = function(content) {
  var $body;
  $body = $("#room-" + content.room_id + " .body");
  $body.find('ul').append("<li title='" + content.user + " " + content.created + "'>" + content.content + "</li>");
  if ($body.find('ul li').length > 5) {
    return $body.find('ul li:first-child').remove();
  }
};
online_users = function(content) {
  var html, val, _i, _len;
  html = '';
  for (_i = 0, _len = content.length; _i < _len; _i++) {
    val = content[_i];
    html += "<span>" + val + "</span>";
  }
  return $('#global_online_user .user_list').html(html);
};
room_online_users = function(content) {
  var html, item, room_id, val, _i, _len;
  html = '';
  for (room_id in content) {
    val = content[room_id];
    for (_i = 0, _len = val.length; _i < _len; _i++) {
      item = val[_i];
      html += "<span>" + val + "</span>";
    }
  }
  return $('#room_online_user .user_list').html(html);
};
room_content = function(content) {
  var html;
  html = "<tr>			<td>" + content.user + "</td>			<td>" + content.content + "</td>			<td>" + content.created + "</td>			</tr>		";
  return $('#chat_content table tr:last-child').after(html);
};
$(function() {
  $('#post_content').bind('submit', function(evt) {
    var data;
    evt.preventDefault();
    data = $(this).serialize();
    return $.post($(this).attr('action'), data, function(result) {
      return console.log(result);
    }, 'json');
  });
  return $('.add_room').bind('click', function(evt) {
    var title;
    title = prompt('要创建的包间名');
    if (title) {
      return $.post('/chat', {
        title: title
      }, function(result) {
        var key, msg, val, _ref;
        if (result.status === 'ok') {
          return window.location.href = result.content.url;
        } else {
          msg = '';
          _ref = result.content;
          for (key in _ref) {
            val = _ref[key];
            msg += val + '\n';
          }
          return alert(msg);
        }
      }, 'json');
    }
  });
});