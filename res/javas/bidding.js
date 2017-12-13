var BIDDING_DATA = {
    toggle_bidding: function() {
        var element = $(this);
        if (element.data('bidding-row')) {
            element.data('bidding-row').remove();
            element.removeData('bidding-row');
        } else {
            var popup = $('<tr class="bidding_popup"><td class="n">&nbsp;</td><td class="bidding_cell noc" colspan="1000"></td></tr>');
            var bidding = BIDDING_DATA.data[element.attr('data-bidding-link')] || BIDDING_DATA.errorString;
            popup.find('.bidding_cell').html(bidding);
            element.closest('tr').after(popup);
            element.data('bidding-row', popup);
        }
        return false;
    },

    load_bidding: function() {
        $('a.biddingLink').hide();
        var dataLink = $('link[rel="bidding-file"]');
        if (dataLink.size() > 0) {
            $.ajax(
                {
                    url: dataLink.eq(0).attr('src'),
                    complete: function(xhr, status) {
                        if (status == 'success') {
                            BIDDING_DATA.data = JSON.parse(xhr.responseText);
                        }
                        $('a.biddingLink').show();
                    }
                }
            );
        }
    },

    bind_bidding_links: function() {
        $('a.biddingLink').each(function() {
            $(this).unbind('click').attr('title', 'Pokaż/ukryj licytację').click(BIDDING_DATA.toggle_bidding);
        });
    },

    data: {},
    errorString: 'Brak danych'
};

$(document).ready(function() {
    BIDDING_DATA.load_bidding();
    setInterval(BIDDING_DATA.bind_bidding_links, 1000);
});
