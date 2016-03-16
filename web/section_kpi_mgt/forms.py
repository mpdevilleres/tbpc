import utils.forms as uforms

class AddSpecForm(uforms.EnhancedForm):

    model_choices = {
    }

    form_order = [
        ['spec_date', 'blank',
         'file', 'blank'],
    ]

    spec_date = uforms.EnhancedDateField(label='Date of Specification:')
    file = uforms.EnhancedFileField(ext_whitelist=['.xlsx'])

class AddKPIForm(uforms.EnhancedForm):

    model_choices = {
    }

    def __init__(self, *args, **kwargs):
        description = kwargs.pop('description', None)
        super(AddKPIForm, self).__init__(*args, **kwargs)
        for key, value in description.items():
            self.fields[key] = uforms.EnhancedDecimalField(label=value)

    @property
    def form_order(self):
        """

        Return as
        [element1, element2],
        [],
        []

        """
        keys = sorted(self.fields.keys())
        # group by n
        n = 2
        ordered_list = []
        for i in range(0, len(keys), 2):
            ordered_list.append(keys[i:i+n])

        return ordered_list