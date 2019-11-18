var channelId;

function refreshTv() {
    $.get('/tv/channel').done(
        function(data) {
            if (channelId !== data.id) {
                channelId = data.id;
                $('#tvframe').attr('src', data.channel);
            }
        }
    )
}

$(document).ready(function() {
    refreshTv();
    setInterval(refreshTv, 5000);
});
