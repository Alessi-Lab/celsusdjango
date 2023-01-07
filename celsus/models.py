import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from celsusdjango import settings


# Create your models here.

class ExtraProperties(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    curtain_link_limits = models.IntegerField(default=settings.CURTAIN_DEFAULT_USER_LINK_LIMIT)
    social_platform = models.ForeignKey("SocialPlatform", on_delete=models.RESTRICT, related_name="user_social_platform",
        blank=True,
        null=True)
    curtain_link_limit_exceed = models.BooleanField(default=False)
    curtain_post = models.BooleanField(default=settings.CURTAIN_DEFAULT_USER_CAN_POST)


class Author(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()
    email = models.EmailField()


class LabGroup(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class CellType(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class TissueType(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class Comparison(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()
    file = models.ForeignKey(
        "File", on_delete=models.CASCADE, related_name="comparisons",
        blank=True,
        null=True
    )


class DifferentialSampleColumn(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()

    column_type_choices = [
        ("P", "P-value"),
        ("FC", "Fold Change"),
        ("PS", "Probability Score"),
        ("SW", "Sequence Window"),
        ("PE", "Peptide Sequence"),
        ("PP", "PTM Position"),
        ("PI", "PTM Position in Peptide")
    ]

    column_type = models.CharField(
        max_length=2,
        choices=column_type_choices,
        default="P"
    )

    comparison = models.ForeignKey(
        "Comparison", on_delete=models.CASCADE, related_name="differential_sample_columns",
        blank=True,
        null=True
    )


class RawSampleColumn(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()
    file = models.ForeignKey(
        "File", on_delete=models.CASCADE, related_name="raw_sample_columns",
        blank=True,
        null=True
    )


class DifferentialAnalysisData(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    primary_id = models.TextField()
    gene_names = models.ForeignKey(
        "GeneNameMap", on_delete=models.RESTRICT,
        blank=True,
        null=True
    )
    fold_change = models.FloatField(null=True)
    significant = models.FloatField(null=True)
    probability_score = models.FloatField(null=True)
    sequence_window = models.TextField(null=True)
    peptide_sequence = models.TextField(null=True)
    ptm_position = models.IntegerField(null=True)
    ptm_position_in_peptide = models.IntegerField(null=True)
    ptm_data = models.BooleanField(default=False)
    comparison = models.ForeignKey(
        "Comparison", on_delete=models.CASCADE, related_name="differential_analysis_datas",
        blank=True,
        null=True
    )


class RawData(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    primary_id = models.TextField()
    value = models.FloatField(null=True)
    raw_sample_column = models.ForeignKey(
        "RawSampleColumn", on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    gene_names = models.ForeignKey(
        "GeneNameMap", on_delete=models.RESTRICT,
        blank=True,
        null=True
    )
    file = models.ForeignKey(
        "File", on_delete=models.RESTRICT, related_name="raw_datas",
        blank=True,
        null=True
    )


class SampleAnnotation(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()
    description = models.TextField()
    project = models.ForeignKey(
        "Project", on_delete=models.RESTRICT, related_name="sample_annotations",
        blank=True,
        null=True
    )


class Disease(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class Instrument(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class Keyword(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()

class UniprotRecord(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    entry = models.TextField()
    record = models.TextField()

class GeneNameMap(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    accession_id = models.TextField()
    gene_names = models.TextField()
    entry = models.TextField()
    uniprot_record = models.ManyToManyField(UniprotRecord, related_name="gene_map")
    primary_uniprot_record = models.ForeignKey(
        "UniprotRecord", on_delete=models.RESTRICT, related_name="gene_map_primary",
        blank=True,
        null=True
    )


class ProjectSettings(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    data = models.TextField(default="{}")
    project = models.ForeignKey(
        "Project", on_delete=models.RESTRICT, related_name="project",
        blank=True,
        null=True
    )


class Organism(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class Curtain(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    link_id = models.TextField(unique=True, default=uuid.uuid4, null=False)
    file = models.FileField(upload_to="media/files/curtain_upload/")
    description = models.TextField()
    owners = models.ManyToManyField(User, related_name="curtain")
    enable = models.BooleanField(default=True)
    curtain_type_choices = [
        ("TP", "Total Proteomics"),
        ("PTM", "Post-translational Modification"),
    ]

    curtain_type = models.CharField(
        max_length=3,
        choices=curtain_type_choices,
        default="TP"
    )

    project = models.ForeignKey(
        "Project", on_delete=models.RESTRICT, related_name="curtain",
        blank=True,
        null=True
    )

class CurtainAccessToken(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    curtain = models.ForeignKey(
        "Curtain", on_delete=models.RESTRICT, related_name="access_token",
        blank=True,
        null=True
    )
    token = models.TextField()


class OrganismPart(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class QuantificationMethod(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class OtherPersonnel(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()
    email = models.EmailField()
    is_collaborator = models.BooleanField()
    is_pi = models.BooleanField()
    project = models.ForeignKey(
        "Project", on_delete=models.RESTRICT, related_name="other_personnels",
        blank=True,
        null=True
    )


class File(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    file = models.FileField(upload_to="media/files/user_upload/")

    file_type_choices = [
        ("DA", "Differential Analysis"),
        ("R", "Raw"),
        ("O", "Other")
    ]

    file_type = models.CharField(
        max_length=2,
        choices=file_type_choices,
        default="O"
    )

    project = models.ForeignKey(
        "Project", on_delete=models.RESTRICT, related_name="files",
        blank=True,
        null=True
    )

    file_parameters = models.TextField()

    def __str__(self):
        return self.file.name + "(" + self.file_type + ")"


class SocialPlatform(models.Model):
    name = models.TextField()

class ExperimentType(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()


class Collaborator(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    name = models.TextField()
    email = models.EmailField()
    project = models.ForeignKey(
        "Project", on_delete=models.RESTRICT, related_name="collaborators",
        blank=True,
        null=True
    )



class Project(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)
    title = models.TextField()
    description = models.TextField()
    sample_processing_protocol = models.TextField()
    data_processing_protocol = models.TextField()
    experiment_type = models.ManyToManyField(ExperimentType, related_name="project")
    date = models.DateTimeField(default=timezone.now)
    database_version = models.TextField()
    enable = models.BooleanField(default=False)
    cell_type = models.ManyToManyField(CellType, related_name="project")
    tissue_type = models.ManyToManyField(TissueType, related_name="project")
    disease = models.ManyToManyField(Disease, related_name="project")
    instrument = models.ManyToManyField(Instrument, related_name="project")
    keyword = models.ManyToManyField(Keyword, related_name="project")
    organism = models.ManyToManyField(Organism, related_name="project")
    organism_part = models.ManyToManyField(OrganismPart, related_name="project")
    quantification_method = models.ManyToManyField(QuantificationMethod, related_name="project")
    lab_group = models.ManyToManyField(LabGroup, related_name="project")
    first_authors = models.ManyToManyField(Author, related_name="first_author_project")
    associated_authors = models.ManyToManyField(Author, related_name="associated_project")
    ptm_data = models.BooleanField(default=False)
    owners = models.ManyToManyField(User, related_name="project")
    project_type_choices = [
        ("TP", "Total Proteomics"),
        ("PTM", "PTM"),
    ]

    project_type = models.CharField(
        max_length=3,
        choices=project_type_choices,
        default="TP"
    )

    default_settings = models.ForeignKey(
        "ProjectSettings", on_delete=models.RESTRICT, related_name="project_default_settings",
        blank=True,
        null=True
    )

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_unique_proteins(self):
        unique_set = set()
        for i in GeneNameMap.objects.filter(rawdata__file__project=self).distinct():
            unique_set.add(i.gene_names)
        return unique_set


