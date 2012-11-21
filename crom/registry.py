# -*- coding: utf-8 -*-

from zope.interface import providedBy, implementedBy
from zope.interface.interfaces import ISpecification
from zope.interface.adapter import AdapterRegistry

from ._compat import CLASS_TYPES
from .interfaces import IRegistry, ILookup
from .directives import implements


def interfaces(requirements):
    ifaces = []
    for requirement in requirements:
        if ISpecification.providedBy(requirement):
            ifaces.append(requirement)
            continue
        if isinstance(requirement, CLASS_TYPES):
            ifaces.append(implementedBy(requirement))
        else:
            raise TypeError("Sources must either be "
                            "an interface or a class.")
    return ifaces


@implements(IRegistry, ILookup)
class Registry(object):
    """A base component registry.
    """

    def __init__(self):
        self.registry = AdapterRegistry()

    def register(self, sources, target, name, component):
        required = interfaces(sources)
        self.registry.register(required, target, name, component)

    def subscribe(self, sources, target, component):
        required = interfaces(sources)
        self.registry.subscribe(required, target, component)

    def lookup(self, obs, target, name):
        return self.registry.lookup(map(providedBy, obs), target, name)

    def subscriptions(self, obs, target):
        return self.registry.subscriptions(map(providedBy, obs), target)

    def adapt(self, obs, target, name):
        # self-adaptation
        if len(obs) == 1 and target.providedBy(obs[0]):
            return obs[0]
        adapter = self.lookup(obs, target, name)
        if adapter is None:
            return None
        try:
            return adapter(*obs)
        except TypeError, e:
            raise TypeError(str(e) + " (%s)" % adapter)
