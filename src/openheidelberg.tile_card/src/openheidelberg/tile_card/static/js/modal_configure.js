//noinspection JSUnusedGlobalSymbols
function initializeConfigureTileCardModal(modal) {
  var $header = modal.$modal.find('.interaktivbasetiles-modal-header');

  // one icon only: choosing a vector icon clears the icon font choice and the other way round
  modal.$modal.on('change', 'input[name="card_icon_svg"]', function () {
    if (this.value) {
      modal.$modal.find('input[name="card_icon"][value=""]').prop('checked', true);
    }
  });
  // click, not change: while a vector icon is chosen "No icon" is already checked in the form, so clicking it
  // fires no change event
  modal.$modal.on('click', 'input[name="card_icon"]', function () {
    // "No icon" (empty value) clears the vector icon too
    modal.$modal.find('input.card-svg-icon-none').prop('checked', true);
  });

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
