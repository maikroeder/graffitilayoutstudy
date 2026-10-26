//noinspection JSUnusedGlobalSymbols
function initializeConfigureTileCardModal(modal) {
  var $header = modal.$modal.find('.interaktivbasetiles-modal-header');

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
