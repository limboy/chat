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
    _results.push($("#room-" + room_id + " .header span").text("(" + users.length + "人在线)"));
  }
  return _results;
};
room_content_all = function(content) {
  var $body;
  $body = $("#room-" + content.room_id + " .body");
  $body.find('ul').append("<li class='new' title='" + content.user + " " + content.created + "'>" + content.content + "</li>");
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
      html += "<span>" + item + "</span>";
    }
  }
  return $('#room_online_user .user_list').html(html);
};
room_content = function(content) {
  var $msg, current_count, current_title, html, new_count;
  $msg = $("#msg-" + content.id);
  if (!$msg.length) {
    html = "<tr id='msg-" + content.id + "'>                <td>" + content.user + "</td>                <td>" + content.content + "</td>                <td>" + content.created + "</td>                </tr>            ";
    $('#chat_content table tbody').append(html);
    $("#chat_content table tbody tr:last-child").get(0).scrollIntoView();
    if (!window.entering_content) {
      if (document.title.substr(0, 1) !== '(') {
        return document.title = "(1) " + document.title;
      } else {
        current_title = document.title;
        current_count = parseInt(current_title.slice(current_title.indexOf('(') + 1, current_title.indexOf(')')));
        new_count = current_count + 1;
        return document.title = current_title.replace("(" + current_count + ")", "(" + new_count + ")");
      }
    }
  }
};
$(function() {
  if ($('#chat_content tbody tr').length) {
    $('#chat_content tbody tr:last-child').get(0).scrollIntoView();
  }
  $('#post_content').bind('submit', function(evt) {
    var data;
    evt.preventDefault();
    data = $(this).serialize();
    if ($.trim($(this).find('input[name="content"]').val()) === '') {
      return false;
    }
    return $.post($(this).attr('action'), data, function(result) {
      $('#post_content input[name="content"]').val('');
      window.entering_content = true;
      document.title = document.title.replace(/\([0-9]+\) /, '');
      return room_content(result);
    }, 'json');
  });
  $('#post_content input[name="content"]').bind('click', function(evt) {
    window.entering_content = true;
    return document.title = document.title.replace(/\([0-9]+\) /, '');
  });
  $('#post_content input[name="content"]').bind('blur', function(evt) {
    return window.entering_content = false;
  });
  $('.add_room').bind('click', function(evt) {
    return $('.chat-bubble').toggle();
  });
  return $('.header .close').bind('click', function(evt) {
    var room_id, room_info, rs;
    rs = confirm('do you really want to remove this room?');
    if (rs) {
      room_info = $(this).parent().parent().attr('id').split('-');
      room_id = room_info[room_info.length - 1];
      return $.post('/rm_room', {
        room_id: room_id
      }, function(result) {
        if (result.status === 'ok') {
          return window.location = result.content.url;
        } else {
          return alert(result.content.message);
        }
      }, 'json');
    }
  });
});