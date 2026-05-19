$(function () {
    var $form = $('#booking-form');
    if (!$form.length) return;

    function getCsrf() {
        return $('[name=csrfmiddlewaretoken]').val();
    }

    function recalcPrice() {
        $.post('/booking/quote/', {
            csrfmiddlewaretoken: getCsrf(),
            slot_id: $('#slot_id').val(),
            persons: $('#persons').val(),
            duration_hours: $('#duration_hours').val(),
            package_id: $('#package_id').val()
        }).done(function (amount) {
            $('#total_price').text(amount);
        });
    }

    $('#persons, #duration_hours, #package_id').on('change keyup', recalcPrice);

    $('#package_id').on('change', function () {
        var hours = $(this).find(':selected').data('hours');
        if (hours) {
            $('#duration_hours').val(hours);
        }
        recalcPrice();
    });

    function submitBooking(action) {
        $('#booking-message').text('Обработка...');
        $.post('/booking/slot/slot_id=' + $('#slot_id').val() + '/', {
            csrfmiddlewaretoken: getCsrf(),
            action: action,
            slot_id: $('#slot_id').val(),
            persons: $('#persons').val(),
            duration_hours: $('#duration_hours').val(),
            package_id: $('#package_id').val(),
            special_requests: $('#special_requests').val()
        }).done(function (resp) {
            if (action === 'book' && resp.indexOf('/payment/') === 0) {
                window.location.href = resp;
                return;
            }
            $('#booking-message').text('Готово! Окно можно закрыть.');
            if (window.opener) {
                window.opener.location.reload();
            }
        }).fail(function (xhr) {
            $('#booking-message').text(xhr.responseText || 'Ошибка бронирования');
        });
    }

    $('#btn-book').on('click', function () {
        submitBooking('book');
    });

    $('#btn-reserve').on('click', function () {
        submitBooking('reserve');
    });
});
