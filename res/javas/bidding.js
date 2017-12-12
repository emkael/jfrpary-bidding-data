var display_bidding = function(element, bidding) {
    var popup = $('<tr class="bidding_popup"><td class="n">&nbsp;</td><td class="bidding_cell noc" colspan="1000"></td></tr>');
    popup.find('.bidding_cell').html(bidding);
    element.closest('tr').after(popup);
    element.data('bidding-row', popup);
}

var load_bidding = function() {
    var elem = $(this);
    if (elem.data('bidding-row')) {
        elem.data('bidding-row').remove();
        elem.removeData('bidding-row');
    } else {
        $.ajax(
            {
                url: elem.attr('data-bidding-link'),
                complete: function(xhr, status) {
                    if (status == 'success') {
                        display_bidding(elem, xhr.responseText);
                    }
                    else {
                        display_bidding(elem, 'Brak danych');
                    }
                }
            }
        );
    }
    return false;
};

var bind_bidding_links = function() {
    $('a.biddingLink').each(function() {
        $(this).unbind('click').attr('title', 'Pokaż/ukryj licytację').click(load_bidding);
    });
};

$(document).ready(function() {
    setInterval(bind_bidding_links, 1000);
});
