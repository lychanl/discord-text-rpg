from dtrpg.data.loaders import Loader

from typing import Collection


class AttributeLoader(Loader):
    pass


class SimpleAttributeLoader(AttributeLoader):
    def __init__(self, type_loader: Loader):
        super(SimpleAttributeLoader, self).__init__()
        self.type_loader = type_loader


class CollectionLoader(AttributeLoader):
    def __init__(self, *attributes: Collection[SimpleAttributeLoader]):
        super(CollectionLoader, self).__init__()
        self._attributes = attributes
