var ws = new WebSocket("ws://tictactoe.vcxz.se/websocket");
ws.onmessage = function (evt) {
  setState(JSON.parse(evt.data));
};

function setState(state) {
  for (var i = 1; i <= 9; i++) {
    var btn = document.getElementById(i);
    btn.innerHTML = state['positions'][i] || '_';
  }
  var turnMessage = document.getElementById('turn');
  turnMessage.innerHTML = state['turn'];
  var winner = document.getElementById('winner');
  winner.innerHTML = state['winner'];
}

function handleClick(evt) {
  var btn = evt.target;
  ws.send(btn.id);
}

buttons = document.querySelectorAll("button")

for (var i = 0; i < buttons.length; i++) {
  var btn = buttons[i];
  btn.addEventListener('click', handleClick);
}
