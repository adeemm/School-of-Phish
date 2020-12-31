(function($) {
  'use strict';

  $(function() {
    if (typeof $.fn.tooltip.Constructor === 'undefined') {
      throw new Error('Bootstrap Tooltip must be included');
    }

    var Tooltip = $.fn.tooltip.Constructor;

    var _show = Tooltip.prototype.show;

    Tooltip.prototype.show = function() {
      _show.apply(this, Array.prototype.slice.apply(arguments));

      if (this.config.customClass) {
        var tip = this.getTipElement();
        $(tip).addClass(this.config.customClass);
      }

    };
    $('[data-toggle="tooltip"]').tooltip();

  });
})(jQuery);