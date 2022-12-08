import factory
from factory.django import DjangoModelFactory

from celsus.models import Author, TissueType, Disease, Organism, OrganismPart, Instrument, \
    QuantificationMethod, Keyword
from celsus.models import CellType as ct
from faker_biology.physiology import CellType, Organ

from faker_web import WebProvider

factory.Faker.add_provider(CellType)
factory.Faker.add_provider(Organ)
factory.Faker.add_provider(WebProvider)


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Faker("name")
    email = factory.Faker("email")


class CellTypeFactory(DjangoModelFactory):
    class Meta:
        model = ct

    name = factory.Faker("celltype")


class TissueTypeFactory(DjangoModelFactory):
    class Meta:
        model = TissueType

    name = factory.Faker("organ")


class DiseaseFactory(DjangoModelFactory):
    class Meta:
        model = Disease

    name = factory.Faker("organ")


class OrganismFactory(DjangoModelFactory):
    class Meta:
        model = Organism

    name = factory.Faker("organ")


class OrganismPartFactory(DjangoModelFactory):
    class Meta:
        model = OrganismPart

    name = factory.Faker("organ")


class InstrumentFactory(DjangoModelFactory):
    class Meta:
        model = Instrument

    name = factory.Faker("server_token")


class QuantificationMethodFactory(DjangoModelFactory):
    class Meta:
        model = QuantificationMethod

    name = factory.Faker("content_type")


class KeywordFactory(DjangoModelFactory):
    class Meta:
        model = Keyword

    name = factory.Faker("word")
