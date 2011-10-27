var channel, create_room_comet, online_users, room_content, room_online_users;
channel = Math.floor(Math.random() * 1000000);
create_room_comet = function() {
  var arg;
  arg = "comet=online_users,room_online_users,room_content&channel=" + channel + "&room=" + window.room_name;
  return $.getJSON("/comet?uri=" + window.uri + "&" + arg, function(data) {
    var key, val;
    for (key in data) {
      val = data[key];
      if (key === 'online_users') {
        online_users(data.online_users);
      } else if (key === 'room_online_users') {
        room_online_users(data.room_online_users);
      } else if (key === 'type' && data.type === 'add_content') {
        room_content(data.content);
      }
    }
    return create_room_comet();
  });
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
  var html, val, _i, _len;
  html = '';
  for (_i = 0, _len = content.length; _i < _len; _i++) {
    val = content[_i];
    html += "<span>" + val + "</span>";
  }
  return $('#room_online_user .user_list').html(html);
};
room_content = function(content) {
  var html;
  html = "<tr>			<td>" + content.user + "</td>			<td>" + content.content + "</td>			<td>" + content.created + "</td>			</tr>		";
  return $('#chat_content table tr:last-child').after(html);
};
$(function() {
  create_room_comet();
  return $('#post_content').bind('submit', function(evt) {
    var data;
    evt.preventDefault();
    data = $(this).serialize();
    return $.post($(this).attr('action'), data, function(result) {
      return console.log(result);
    }, 'json');
  });
});