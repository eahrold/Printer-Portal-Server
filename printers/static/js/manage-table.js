$(document).ready(function() {
var light_gray = 'DarkGray'
// Table
  $('table').addClass('table table-striped table-condensed table-bordered');

  $dt = $('.data-table');
  $dt.dataTable({
    "sPaginationType": "bootstrap",
  });

// Table Rows (but not headers)
  $row = $('tr:not(":has(th)")');
  var defaultOpacity = 0.7;

  $row.css('opacity', defaultOpacity);
  $row.mouseenter(function(){
    $(this).fadeTo('fast', 1.0);
  });

  $row.mouseleave(function(){
    $(this).fadeTo('fast', defaultOpacity)
  });

// Description text
  $('dd').css( {
    'color' : light_gray,
  });
});
