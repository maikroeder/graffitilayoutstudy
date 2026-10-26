// Loads the numbers of the dashboard boxes after the page has been rendered.
// Called for every dashboard tile on page load and by the tiles editor / lazy loaded rows (jsinit).
function initGraffitiTileDashboard($tile){
  var $boxes = $tile.find('.tile-dashboard-boxes');

  if (!$boxes.length || $boxes.data('dashboardLoaded')) {
    return;
  }
  $boxes.data('dashboardLoaded', true);

  $.getJSON($boxes.data('url'))
    .done(function (data) {
      var counts = (data && data.counts) || {};
      $boxes.find('.tile-dashboard-box').each(function () {
        var $box = $(this);
        var count = counts[$box.data('boxId')];
        $box.find('.tile-dashboard-count').text(count === undefined ? '-' : count);
        // only boxes that asked for it (data-urgent), and only with a number above zero
        $box.toggleClass('is-urgent', $box.attr('data-urgent') === 'true' && count > 0);
      });
      $tile.addClass('tile-dashboard-loaded');
    })
    .fail(function () {
      $boxes.find('.tile-dashboard-count').text('-');
      $tile.addClass('tile-dashboard-failed');
    });
}

$(document).ready(function () {
  $('.tile.tile-dashboard').each(function () {
    initGraffitiTileDashboard($(this));
  });
});
