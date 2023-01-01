import json
import os
import re

from django.contrib.auth.models import User
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from celsus.models import CellType, TissueType, ExperimentType, Instrument, Organism, OrganismPart, \
    QuantificationMethod, Project, Author, File, Keyword, Disease, Curtain, DifferentialSampleColumn, RawSampleColumn, \
    DifferentialAnalysisData, RawData, Comparison, GeneNameMap, LabGroup, UniprotRecord, ProjectSettings
from celsusdjango import settings


class CellTypeSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, cell_type):
        try:
            return cell_type.project_count
        except:
            return 0

    class Meta:
        model = CellType
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class TissueTypeSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, tissue_type):
        try:
            return tissue_type.project_count
        except:
            return 0

    class Meta:
        model = TissueType
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class ExperimentTypeSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, experiment_type):
        try:
            return experiment_type.project_count
        except:
            return 0

    class Meta:
        model = ExperimentType
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class InstrumentSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, instrument):
        try:
            return instrument.project_count
        except:
            return 0

    class Meta:
        model = Instrument
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class OrganismSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, organism):
        try:
            return organism.project_count
        except:
            return 0

    class Meta:
        model = Organism
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class OrganismPartSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, organism_part):
        try:
            return organism_part.project_count
        except:
            return 0

    class Meta:
        model = OrganismPart
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class QuantificationMethodSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, quantification_method):
        try:
            return quantification_method.project_count
        except:
            return 0

    class Meta:
        model = QuantificationMethod
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class UserSerializer(FlexFieldsModelSerializer):
    project = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    curtain = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    can_delete = serializers.SerializerMethodField()

    def get_can_delete(self, user):
        if settings.CURTAIN_ALLOW_NON_STAFF_DELETE:
            return True
        else:
            return user.is_staff

    class Meta:
        model = User
        fields = ["id", "username", "is_staff", "is_authenticated", "project", "curtain", "can_delete"]
        expandable_fields = dict(
            project=("celsus.serializers.ProjectSerializer",
                            dict(many=True, read_only=True)),
            curtain=(
            "celsus.serializers.CurtainSerializer", dict(fields=["id", "description"], many=True, read_only=True))
        )


class DiseaseSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, disease):
        try:
            return disease.project_count
        except:
            return 0

    class Meta:
        model = Disease
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class AuthorSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Author
        fields = [f.name for f in model._meta.fields]


class UniprotRecordSerializer(FlexFieldsModelSerializer):
    record = serializers.SerializerMethodField()
    def get_record(self, record):
        try:
            rec = re.sub(r'\bNaN\b', '""', record.record)
            return json.loads(rec)
        except:
            return None

    class Meta:
        model = UniprotRecord
        fields = ["id", "entry", "record"]

class KeywordSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, keyword):
        try:
            return keyword.project_count
        except:
            return 0

    class Meta:
        model = Keyword
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class GeneNameMapSerializer(FlexFieldsModelSerializer):
    uniprot_record = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    primary_uniprot_record = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = GeneNameMap
        fields = [f.name for f in model._meta.fields] + ["uniprot_record", "primary_uniprot_record"]
        expandable_fields = dict(
            uniprot_record=("celsus.serializers.UniprotRecordSerializer", dict(fields=["id", "entry", "record"], many=True, read_only=True)),
            primary_uniprot_record=("celsus.serializers.UniprotRecordSerializer", dict(fields=["id", "entry", "record"], read_only=True))
        )


class ProjectSettingsSerializer(FlexFieldsModelSerializer):
    data = serializers.SerializerMethodField()

    def get_data(self, settings):
        try:
            rec = re.sub(r'\bNaN\b', '""', settings.data)
            return json.loads(rec)
        except:
            return None

    class Meta:
        model = ProjectSettings
        fields = ["id", "data", "project"]


class LabGroupSerializer(FlexFieldsModelSerializer):
    project_count = serializers.SerializerMethodField()

    def get_project_count(self, lab_group):
        try:
            return lab_group.project_count
        except:
            return 0

    class Meta:
        model = LabGroup
        fields = [f.name for f in model._meta.fields] + ["project_count"]


class CurtainSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, record):
        _, filename = os.path.split(record.file.name)
        return filename

    class Meta:
        model = Curtain
        fields = ["id", "created", "link_id", "file", "enable", "description", "curtain_type"]
        lookup_field = "link_id"


class ComparisonSerializer(FlexFieldsModelSerializer):
    file = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comparison
        fields = [f.name for f in model._meta.fields]
        expandable_fields = dict(
            file=("celsus.serializers.FileSerializer",
                  #dict(fields=["id", "file_type", "project"])
                  )
        )


class DifferentialAnalysisDataSerializer(FlexFieldsModelSerializer):
    gene_names = GeneNameMapSerializer(many=False)
    comparison = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DifferentialAnalysisData
        fields = [f.name for f in model._meta.fields]
        expandable_fields = dict(
            comparison=(ComparisonSerializer,)
        )


class RawSampleColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawSampleColumn
        fields = [f.name for f in model._meta.fields]


class RawDataSerializer(serializers.ModelSerializer):
    gene_names = GeneNameMapSerializer(many=False)
    raw_sample_column = RawSampleColumnSerializer(many=False)

    class Meta:
        model = RawData
        fields = [f.name for f in model._meta.fields]


class FileSerializer(FlexFieldsModelSerializer):
    comparisons = ComparisonSerializer(many=True, read_only=True)
    raw_sample_columns = RawSampleColumnSerializer(many=True, read_only=True)
    file = serializers.SerializerMethodField()
    #project = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_file(self, record):
        _, filename = os.path.split(record.file.name)
        return filename

    class Meta:
        model = File
        fields = ["id", "created", "file", "file_type", "comparisons", "raw_sample_columns", "project"]
        expandable_fields = dict(
            project=("celsus.serializers.ProjectSerializer", dict(fields=["id", "title"]))
        )


class ProjectSerializer(FlexFieldsModelSerializer):
    quantification_method = QuantificationMethodSerializer(many=True, read_only=True)
    cell_type = CellTypeSerializer(many=True, read_only=True)
    tissue_type = TissueTypeSerializer(many=True, read_only=True)
    disease = DiseaseSerializer(many=True, read_only=True)
    instrument = InstrumentSerializer(many=True, read_only=True)
    keyword = KeywordSerializer(many=True, read_only=True)
    organism = OrganismSerializer(many=True, read_only=True)
    organism_part = OrganismPartSerializer(many=True, read_only=True)
    curtain = CurtainSerializer(many=True, read_only=True)
    experiment_type = ExperimentTypeSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    associated_authors = AuthorSerializer(many=True, read_only=True)
    first_authors = AuthorSerializer(many=True, read_only=True)
    lab_group = LabGroupSerializer(many=True, read_only=True)
    owners = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    default_settings = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "sample_processing_protocol",
            "data_processing_protocol",
            "associated_authors",
            "first_authors",
            "database_version",
            "date",
            "enable",
            "tissue_type",
            "quantification_method",
            "cell_type", "disease",
            "instrument",
            "keyword",
            "organism",
            "organism_part",
            "curtain",
            "experiment_type",
            "files",
            "ptm_data",
            "lab_group",
            "project_type",
            "owners",
            "default_settings"
        ]
        expandable_fields = dict(
            quantification_method=(QuantificationMethodSerializer, dict(many=True, read_only=True)),
            cell_type=(CellTypeSerializer, dict(many=True, read_only=True)),
            tissue_type=(TissueTypeSerializer, dict(many=True, read_only=True)),
            disease=(DiseaseSerializer, dict(many=True, read_only=True)),
            instrument=(InstrumentSerializer, dict(many=True, read_only=True)),
            keyword=(KeywordSerializer, dict(many=True, read_only=True)),
            organism=(OrganismSerializer, dict(many=True, read_only=True)),
            organism_part=(OrganismPartSerializer, dict(many=True, read_only=True)),
            curtain=(CurtainSerializer, dict(many=True, read_only=True)),
            experiment_type=(ExperimentTypeSerializer, dict(many=True, read_only=True)),
            files=(FileSerializer, dict(many=True, read_only=True)),
            associated_authors=(AuthorSerializer, dict(many=True, read_only=True)),
            first_authors=(AuthorSerializer, dict(many=True, read_only=True)),
            lab_group=(LabGroupSerializer, dict(many=True, read_only=True)),
            default_settings=(ProjectSettingsSerializer,)
        )


class DifferentialSampleColumnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DifferentialSampleColumn
        fields = "__all__"
