$(document).ready(function() {
    $(".my-progress-bar").circularProgress({
                line_width: 18,
                color: '#1E90FF',
                starting_position: 75,
                percent: 0,
                percentage: true,
    }).circularProgress('animate', 100, 3000);
});
