var channel, create_chat_comet, create_room_comet, room_content, room_content_all, room_online_users, room_online_users_count_all;
channel = Math.floor(Math.random() * 1000000);
create_chat_comet = function(ts) {
  var arg;
  if (ts == null) {
    ts = '';
  }
  arg = "comet=room_online_users_count_all,room_content_all&channel=" + channel + "&ts=" + ts;
  return $.getJSON("/comet?uri=" + window.uri + "&" + arg, function(result) {
    if (result.type === 'room_online_users') {
      room_online_users_count_all(result.data);
    } else if (result.type === 'add_content') {
      room_content_all(result.data);
    }
    return create_chat_comet(result.ts);
  });
};
create_room_comet = function(ts) {
  var arg;
  if (ts == null) {
    ts = '';
  }
  arg = "comet=room_online_users,room_content&channel=" + channel + "&room_id=" + window.room_id + "&ts=" + ts;
  return $.getJSON("/comet?uri=" + window.uri + "&" + arg, function(result) {
    if (result.type === 'online_users') {
      online_users(result.data);
    } else if (result.type === 'room_online_users') {
      room_online_users(result.data);
    } else if (result.type === 'add_content') {
      room_content(result.data);
    }
    return create_room_comet(result.ts);
  });
};
room_online_users_count_all = function(data) {
  return $("#room-" + data.room_id + " .header span").text("(" + data.users.length + "人在线)");
};
room_content_all = function(data) {
  var $body, content, _i, _len, _ref, _results;
  $body = $("#room-" + data.room_id + " .body");
  _ref = data.content;
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    content = _ref[_i];
    $body.find('ul').append("<li class='new' title='" + content.user + " " + content.created + "'>" + content.content + "</li>");
  }
  _results = [];
  while ($body.find('ul li').length > 5) {
    _results.push($body.find('ul li:first-child').remove());
  }
  return _results;
};
room_online_users = function(data) {
  var html, item, _i, _len, _ref;
  html = '';
  _ref = data.users;
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    item = _ref[_i];
    html += "<span>" + item + "</span>";
  }
  return $('#room_online_user .user_list').html(html);
};
room_content = function(data) {
  var $msg, content, current_count, current_title, html, new_count, _i, _len, _ref, _results;
  console.log(data);
  _ref = data.content;
  _results = [];
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    content = _ref[_i];
    $msg = $("#msg-" + content.id);
    _results.push(!$msg.length ? (html = "<tr id='msg-" + content.id + "'>                    <td>" + content.user + "</td>                    <td>" + content.content + "</td>                    <td>" + content.created + "</td>                    </tr>                ", $('#chat_content table tbody').append(html), $("#chat_content table tbody tr:last-child").get(0).scrollIntoView(), !window.entering_content ? document.title.substr(0, 1) !== '(' ? document.title = "(1) " + document.title : (current_title = document.title, current_count = parseInt(current_title.slice(current_title.indexOf('(') + 1, current_title.indexOf(')'))), new_count = current_count + 1, document.title = current_title.replace("(" + current_count + ")", "(" + new_count + ")")) : void 0) : void 0);
  }
  return _results;
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
      return room_content({
        'content': [result]
      });
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