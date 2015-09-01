var display_bidding = function(element, bidding) {
    var popup = $('<div id="bidding_popup"></div>');
    popup.css({
        'position': 'absolute',
        'width': '250px',
        'left': element.offset().left + element.width(),
        'top': element.offset().top
    });
    popup.html(bidding);
    $('body').append(popup);
}

var load_bidding = function() {
    $('#bidding_popup').remove();
    var elem = $(this);
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
    return false;
};

var bind_bidding_links = function() {
    $('a.biddingLink').each(function() {
        $(this).unbind('click').click(load_bidding);
    });
    $(document).click(function() {
        $('#bidding_popup').remove();
    });
};

$(document).ready(function() {
    setInterval(bind_bidding_links, 1000);
});
