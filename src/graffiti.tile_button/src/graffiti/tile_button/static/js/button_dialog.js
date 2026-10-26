// Tab "CSS classes" in the dialog of the button tile (graffiti.tile_button).
// The dialog of interaktiv.tile_button shows only the error type of a failed save. For invalid CSS classes
// the description tells the editor what to change, so it replaces the type in the message of the dialog.
// jQuery fires the global ajaxError event after the error callback of the dialog has shown its message.
$(document).ajaxError(function(event, xhr, settings){
  if(!settings.url || !/\/update_content$/.test(settings.url)){
    return;
  }
  var response = {};
  try {
    response = JSON.parse(xhr.responseText) || {};
  } catch(e) {
    return;
  }
  if(response.error_type !== 'InvalidCssClasses' || !response.error_description){
    return;
  }
  $('.interaktivbasetiles-modal-content .alert-danger').filter(function(){
    return $.trim($(this).text()) === response.error_type;
  }).text(response.error_description);
});
