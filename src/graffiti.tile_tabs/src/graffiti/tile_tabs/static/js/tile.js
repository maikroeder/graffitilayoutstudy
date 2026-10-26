// Switches the tabs of a tab lists tile. Delegated to the document, so it also works for
// tiles the editor renders later and needs no initialisation per tile.
$(document).on('click', '.tile-tabs .tile-tabs-nav button', function () {
  var $button = $(this);
  var $tile = $button.closest('.tile-tabs');
  var tabId = $button.attr('data-tab');

  $tile.find('.tile-tabs-nav-item').removeClass('active');
  $tile.find('.tile-tabs-nav button').attr('aria-selected', 'false');
  $button.attr('aria-selected', 'true').closest('.tile-tabs-nav-item').addClass('active');
  $tile.find('.tile-tabs-panel').each(function () {
    var $panel = $(this);
    $panel.prop('hidden', $panel.attr('data-tab') !== tabId);
  });
});
