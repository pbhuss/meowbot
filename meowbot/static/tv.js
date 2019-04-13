function refreshTv() {
    $.get('/tv/channel').done(
        function(channel) {
            let tvFrame = $('#tvframe');
            if (tvFrame.attr('src') !== channel) {
                tvFrame.attr('src', channel);
            }
        }
    )
}

$(document).ready(function() {
    refreshTv();
    setInterval(refreshTv, 5000);
});
