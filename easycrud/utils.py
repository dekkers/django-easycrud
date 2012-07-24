from django.db.models.loading import get_model, get_models


# From http://stackoverflow.com/questions/128573/using-property-on-classmethods
class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def get_model_by_name(name):
    if '.' in name:
        app_label, model_name = name.split('.')
        model = get_model(app_label, model_name)
    else:
        model_list = get_models()
        found = False
        for m in model_list:
            if m.__name__.lower() == name.lower():
                if found:
                    raise ValueError("Multiple models with the name %s found, use app_label.model syntax" % name)
                found = True
                model = m

        if not found:
            raise ValueError("No model with name %s found" % name)

    return model
