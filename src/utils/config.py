import yaml


def read_yaml(filename):
    with open(filename, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise exc


def attrs_ranker(attr):
    _, value = attr
    return value.points


class BaseConfig(dict):

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dikt):
        for k, v in dikt.items():
            setattr(self, k, v)


class Config(BaseConfig):
    def __init__(self, dikt):
        ranking_attrs = []
        for k, v in dikt.items():
            setattr(self, k, BaseConfig(v))
            ranking_attrs.append((k, getattr(self, k)))

        self.ranking_attrs = [attr[0] for attr in sorted(ranking_attrs, key=attrs_ranker, reverse=True)]
