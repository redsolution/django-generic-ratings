(function($) {
    $(document).ready(function() {
        var submit_form = function(form_object) {
            var values = {};
            form_object.find(':input').each(function() {
                values[this.name] = $(this).val();
            });
            $.ajax({  
                type: "POST",  
                url: form_object.attr('action'),  
                data: values,  
                success: function(data) {  
                    form_object.find('.success').show();
                    form_object.trigger('vote_submit', [data]);
                },
                error: function() {
                    form_object.find('.error').show();
                }
            });
        };
        $('form.ratings').each(function() {
            var form_object = $(this);
            form_object.submit(function() {
                submit_form(form_object);
                return false;
            });
            $(document).bind('star_change', function(event, value) {
                submit_form(form_object);
            });
            $(document).bind('star_delete', function(event) {
                submit_form(form_object);
            });
            $(document).bind('slider_delete', function(event) {
                submit_form(form_object);
            });
        });
    });
})(jQuery);