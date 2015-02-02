var PYTALKY = {
    template: _.template($("#option_template").text()),
    search: function(query) {
        var defer = $.Deferred();
        $.ajax({
            url: "./teachers",
            data: {
                lang_code: query.lang_code,
                user_type: query.user_type,
            },
            dataType: 'json',
            success: defer.resolve,
            error: defer.reject
        });
        return defer.promise();
    },
    view: {
        search_button: $('#search-button'),
        search_result: $('#search-result'),
        user_type: $('#user-type'),
        lang_code: $('#lang-code'),
        title_message: $('#title-message'),
        lang_action: $('#lang-action'),
    }
};
$(function() {
    PYTALKY.view.search_button.on('click', function() {
        var query = {
            user_type: PYTALKY.view.user_type.val(),
            lang_code: PYTALKY.view.lang_code.val(),
        };
        PYTALKY.search(query).done(function(data) {
//            console.log(data);
            var search_result = PYTALKY.template({user_list: data});
            PYTALKY.view.search_result.empty().append(search_result);
            PYTALKY.view.title_message.text('Here is your ' + query.user_type);
        });
    });
    PYTALKY.view.user_type.on('change', function(event) {
        PYTALKY.view.lang_action.text(($(event.target).val() === "student") ? "Speaks" : "Teaches");
    });

});
