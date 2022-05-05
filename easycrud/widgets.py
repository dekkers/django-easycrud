from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.conf import settings


class EasyCrudSelect(Select):
    def __init__(self, model, *args, **kwargs):
        self.model = model
        return super(EasyCrudSelect, self).__init__(*args, **kwargs)

    def render(self, *args, **kwargs):
        output = super(EasyCrudSelect, self).render(*args, **kwargs)
        if self.model.has_create:
            output += '<a href="{0.create_url}"><img src="{1}admin/img/icon-addlink.svg"></a>'.format(self.model, settings.STATIC_URL)
        return mark_safe(output)
