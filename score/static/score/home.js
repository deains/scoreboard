function Scoreboard() {
    this.socketListeners = {
        close: this.onSocketClose.bind(this),
        error: this.onSocketError.bind(this),
        message: this.onSocketMessage.bind(this),
        open: this.onSocketOpen.bind(this)
    };
    this.vars = JSON.parse($('#vars').text());
    this.open();
}

Scoreboard.prototype.onSocketClose = function(event) {
    this.reconnect();
};

Scoreboard.prototype.onSocketError = function(event) {
    this.reconnect();
};

Scoreboard.prototype.onSocketMessage = function(event) {
    let data = JSON.parse(event.data);
    data.players.forEach((player) => {
        $(`#s${data.sbid}p${player.pid}`).text(player.str);
    });
};

Scoreboard.prototype.onSocketOpen = function(event) {
};

Scoreboard.prototype.open = function() {
    var proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
    this.socket = new WebSocket(proto + location.host + this.vars.ws_url);
    for (var type in this.socketListeners) {
        this.socket.addEventListener(type, this.socketListeners[type]);
    }
};

Scoreboard.prototype.reconnect = function() {
    for (var type in this.socketListeners) {
        this.socket.removeEventListener(type, this.socketListeners[type]);
    }
    setTimeout(function() {
        this.open();
    }.bind(this), 1000);
};

$(function() {
    window.sb = new Scoreboard();

    $('form').each(function() {
        $(this).ajaxForm();
    });
});
