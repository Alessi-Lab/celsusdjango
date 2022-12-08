from django.contrib import admin

from celsus.models import Project, File, Comparison, CellType, Author, Collaborator, ExperimentType, TissueType, \
    Keyword, Disease, Instrument, Organism, OrganismPart, Curtain, QuantificationMethod, DifferentialAnalysisData


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "created")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("file", "file_type", "created")

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "created")

@admin.register(CellType)
class CellTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created")

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created")

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created")

@admin.register(ExperimentType)
class ExperimentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created")


@admin.register(TissueType)
class TissueTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created")


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("name", "created")

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "created")


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ("name", "created")

@admin.register(Organism)
class OrganismAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created")

@admin.register(OrganismPart)
class OrganismPartAdmin(admin.ModelAdmin):
    list_display = ("name", "created")

@admin.register(Curtain)
class CurtainAdmin(admin.ModelAdmin):
    pass

@admin.register(QuantificationMethod)
class QuantificationMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "created")


@admin.register(DifferentialAnalysisData)
class DifferentialAnalysisDataAdmin(admin.ModelAdmin):
    list_display = ("primary_id", "gene_names", "fold_change", "significant", "comparison")
    search_fields = ["primary_id", "gene_names", "comparison__name"]