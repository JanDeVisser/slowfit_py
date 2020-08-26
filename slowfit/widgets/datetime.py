from django.forms import DateTimeInput, DateInput


class DateTimePickerInput(DateTimeInput):
    template_name = 'widgets/datetimepicker.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['date'] = 'true'
        context['widget']['time'] = 'true'
        context['widget']['format'] = 'Y-m-d H:i'
        return context


class DatePickerInput(DateInput):
    template_name = 'widgets/datetimepicker.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # context['widget']['date'] = 'true'
        # context['widget']['time'] = 'false'
        context['widget']['format'] = 'yyyy-mm-dd'
        return context
