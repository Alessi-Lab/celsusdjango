from django.test import TestCase
from celsus.models import Author, CellType, TissueType, Organism, OrganismPart, Disease, Instrument, \
    QuantificationMethod, Project, Keyword
from celsus.factories import CellTypeFactory, AuthorFactory, TissueTypeFactory, OrganismFactory, OrganismPartFactory, \
    DiseaseFactory, InstrumentFactory, QuantificationMethodFactory, KeywordFactory


class AuthorTestCase(TestCase):
    def setUp(self) -> None:
        AuthorFactory()

    def test_author(self):
        a = Author.objects.all()
        for i in a:
            print(i.name, i.email)


class CellTypeTestCase(TestCase):
    def setUp(self) -> None:
        CellTypeFactory()

    def test_cell_type(self):
        c = CellType.objects.all()
        for i in c:
            print(i.name)

class TissueTypeTestCase(TestCase):
    def setUp(self) -> None:
        TissueTypeFactory()

    def test_tisse_type(self):
        c = TissueType.objects.all()
        for i in c:
            print(i.name)


class OrganismTestCase(TestCase):
    def setUp(self) -> None:
        OrganismFactory()

    def test_organism(self):
        c = Organism.objects.all()
        for i in c:
            print(i.name)


class OrganismPartTestCase(TestCase):
    def setUp(self) -> None:
        OrganismPartFactory()

    def test_organism_part(self):
        c = OrganismPart.objects.all()
        for i in c:
            print(i.name)


class DiseaseTestCase(TestCase):
    def setUp(self) -> None:
        DiseaseFactory()

    def test_disease(self):
        c = Disease.objects.all()
        for i in c:
            print(i.name)

class InstrumentTestCase(TestCase):
    def setUp(self) -> None:
        InstrumentFactory()

    def test_instrument(self):
        c = Instrument.objects.all()
        for i in c:
            print(i.name)


class QuantificationMethodTestCase(TestCase):
    def setUp(self) -> None:
        QuantificationMethodFactory()

    def test_disease(self):
        c = QuantificationMethod.objects.all()
        for i in c:
            print(i.name)

class KeywordTestCase(TestCase):
    def setUp(self) -> None:
        KeywordFactory()

    def test_disease(self):
        c = Keyword.objects.all()
        for i in c:
            print(i.name)

class ProjectMethodTestCase(TestCase):
    def setUp(self) -> None:
        author = AuthorFactory()
        author.save()
        cell_type = CellTypeFactory()
        cell_type.save()
        tissue_type = TissueTypeFactory()
        tissue_type.save()
        organism = OrganismFactory()
        organism.save()
        organism_part = OrganismPartFactory()
        organism_part.save()
        keyword = KeywordFactory()
        keyword.save()
        instrument = InstrumentFactory()
        instrument.save()
        quantification_method = QuantificationMethod()
        quantification_method.save()
        disease = DiseaseFactory()
        disease.save()
        p = Project()
        p.save()
        p.authors.set([author])
        p.cell_types.set([cell_type])
        p.tissue_types.set([tissue_type])
        p.organisms.set([organism])
        p.organism_parts.set([organism_part])
        p.keywords.set([keyword])
        p.instruments.set([instrument])
        p.quantification_methods.set([quantification_method])
        p.diseases.set([disease])


    def test_project(self):
        c = Project.objects.all()
        for i in c:
            print(i.title, i.authors.all())
