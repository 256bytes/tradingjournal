//Symbol search for Holdings Page
$(document).ready(function () {
  var symbols = [];
  function loadSymbols() {
    $.getJSON("/ac_search", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++) {
        symbols.push(data[i].script);
      }
    });
  }
  loadSymbols();

  $("#symbols").autocomplete({
    source: symbols,
    appendTo: $("#symbols").parent(),
    select: function (event, ui) {
      $("#symbols").val(ui.item.value);
      $("#acs_symbol_form").submit();
      return false;
    },
  });
});
//==========================================================
//Trading Code search for Holdings Page

$(document).ready(function () {
  var trading_code = [];
  function loadTradingCode() {
    $.getJSON("/acs_traders", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++) {
        trading_code.push(data[i].trading_code);
      }
    });
  }
  loadTradingCode();

  $("#trading_code").autocomplete({
    source: trading_code,
    appendTo: $("#trading_code").parent(),
    select: function (event, ui) {
      $("#trading_code").val(ui.item.value);
      $("#acs_trading_form").submit();
      return false;
    },
  });
});
//================================================================
//Symbol search for Analytics Page
$(document).ready(function () {
  var research_symbols = [];
  function loadResearchSymbols() {
    $.getJSON("/acs_research_symb", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++) {
        research_symbols.push(data[i].research_symb);
      }
    });
  }
  loadResearchSymbols();

  $("#research_symbols").autocomplete({
    source: research_symbols,
    appendTo: $("#research_symbols").parent(),
    select: function (event, ui) {
      $("#research_symbols").val(ui.item.value);
      $("#acs_symb_research_form").submit();
      return false;
    },
  });
});
//================================================================
// Analysts search for Analytics Page
$(document).ready(function () {
  var analysts = [];
  function loadAnalysts() {
    $.getJSON("/acs_analysts", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++) {
        analysts.push(data[i].analysts);
      }
    });
  }
  loadAnalysts();

  $("#analyst").autocomplete({
    source: analysts,
    appendTo: $("#analyst").parent(),
    select: function (event, ui) {
      $("#analyst").val(ui.item.value);
      $("#acs_analyst_form").submit();
      return false;
    },
  });
  
});

//================================================================
//Symbol search from bhav copy for Add Research Modal
$(document).ready(function () {
  var add_research_symb_form = [];
  function loadAddResearchSymb() {
    $.getJSON("/acs_bhavcopy_symb", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++){
        add_research_symb_form.push(data[i])
      }
    });
  }
  loadAddResearchSymb();

  $("#script").autocomplete({
    source: add_research_symb_form,
    appendTo: $("#script").parent(),
    select: function (event, ui) {
      $("#script").val(ui.item.value);
      return false;
    },
  });
});
//================================================================
// Analysts search for Add Research Modal
$(document).ready(function () {
  var analysts = [];
  function loadAnalysts() {
    $.getJSON("/acs_analysts", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++) {
        analysts.push(data[i].analysts);
      }
    });
  }
  loadAnalysts();

  $("#r_analyst").autocomplete({
    source: analysts,
    appendTo: $("#r_analyst").parent(),
    select: function (event, ui) {
      $("#r_analyst").val(ui.item.value);
      return false;
    },
  });
  
});

//================================================================
//Symbol search from bhav copy for Buy Stocks Form
$(document).ready(function () {
  var add_research_symb_form = [];
  function loadAddResearchSymb() {
    $.getJSON("/acs_bhavcopy_symb", function (data, status, xhr) {
      for (var i = 0; i < data.length; i++){
        add_research_symb_form.push(data[i])
      }
    });
  }
  loadAddResearchSymb();

  $("#buy_script").autocomplete({
    source: add_research_symb_form,
    appendTo: $("#buy_script").parent(),
    select: function (event, ui) {
      $("#buy_script").val(ui.item.value);
      return false;
    },
  });
});






