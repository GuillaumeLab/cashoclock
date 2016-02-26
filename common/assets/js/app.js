;(function ($, window, document, undefined) {
  $(function () {

    // TABLE FLOAT THEAD
    // All tables should have thead-float enabled

    // FIXME: this is causing a bug in table width (half a pixel)
    /*$('table.table').floatThead({
      zIndex: 1
    });*/

    // SELECT2

    $('select').select2({
      language: 'pt-BR',
      allowClear: true
    });

    // DATEPICKER

    function setupDatepicker() {
      $('input.datepicker').each(function (i, input) {
        var format = $(input).data('format') || 'dd/mm/yyyy';
        $(input).datepicker({
          format: format,
          language: "pt-BR",
          autoclose: true,
          todayHighlight: true,
          orientation: "bottom auto"
        });
      });
    }
    $(document).on('show.bs.modal', setupDatepicker);
    $(document).on('show.bs.collapse', setupDatepicker);
    setupDatepicker();

    // CURRENCY

    function maskMoney() {
      $('.currency').maskMoney({
        prefix: 'R$ ',
        affixesStay: false,
        thousands: '.',
        decimal: ',',
        allowZero: true
      });
    }

    $(document).on('blur', '.currency', function () {
      $(this).val($(this).val().replace(/\./g, ''));
    });
    $(document).on('keypress', '.currency', function (e) {
      // force blur when pressing enter
      if (e.which == 13) {
        $(this).trigger('blur');
      }
    });
    $(document).on('show.bs.modal', maskMoney);
    $(document).on('ajax-success', maskMoney);
    maskMoney();

    // COLLAPSE

    $(document).on('click', '[data-toggle]', function () {
      $($(this).data('toggle')).toggleClass('open');
      if (!$(this).is('input')) {
        return false;
      }
    });

    // keep open state of checkboxes with data-toggle
    function collapse() {
      $('input[data-toggle]').each(function () {
        var $el = $(this);
        if ($el.prop('checked')) {
          $($el.data('toggle')).toggleClass('open');
        }
      });
    }

    $(document).on('open.fndtn.reveal', collapse);
    $(document).on('ajax-success', collapse);
    collapse();
  });

})(jQuery, window, document);


/**
 * Get a querystring parameter by name
 * @param name: name of the parameter
 */
function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
      results = regex.exec(location.search);
  return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

/**
 * Render a widget
 * @param name
 * @param urlParams
 * @param target
 */
function widget(name, urlParams, target) {
  urlParams = urlParams || '';
  var $target = $(target || '#' + name);
  if (!$target) {
    return;
  }
  $target.html('<div class="loading-widget"><i class="fa fa-refresh fa-spin"></i> Carregando...</div>');
  var url = WIDGETS_URL.replace(':name:', name) + '?' + urlParams;
  $.get(url, function(html) {
    $target.html(html);
  });
}
