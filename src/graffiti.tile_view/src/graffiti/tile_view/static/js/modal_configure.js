//noinspection JSUnusedGlobalSymbols
function initializeConfigureTileViewModal(modal) {
  var $header = modal.$modal.find('.interaktivbasetiles-modal-header');
  var $select = modal.$modal.find('select[name="view_id"]');
  var $description = modal.$modal.find('.tile-view-description');

  function showDescription() {
    var $option = $select.find('option:selected');
    $description.text($option.data('description') || '');
  }
  showDescription();
  $select.on('change', showDescription);

  modal.$modal.on('click', '.modal-action-save', function (e) {
    e.preventDefault();
    e.stopPropagation();
    modal.submitForm(
      $header.data('base_url') + '/update_content', 'json',
      function (success, response) {
        if (success) {
          refreshTiles(response.uid, response.render);
          modal.close();
        }
      }
    );
  });
}
