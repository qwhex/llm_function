import json


class Validators:
    @staticmethod
    def str(obj):
        if not isinstance(obj, str):
            raise ValueError('Not a string')
        return obj


validators = Validators()
