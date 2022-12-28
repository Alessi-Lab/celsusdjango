import six

from filters.schema import base_query_params_schema
from filters.validations import DatetimeWithTZ, IntegerLike, CSVofIntegers, Alphanumeric, GenericSeparatedValidator

organism_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "created": DatetimeWithTZ(),
        "name": six.text_type,
        "project_count": IntegerLike()
    }
)

comparison_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "created": DatetimeWithTZ(),
        "name": six.text_type,
        "file_id": IntegerLike(),
    }
)

differential_data_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "created": DatetimeWithTZ(),
        "primary_id": six.text_type,
        "gene_names": six.text_type,
        "gene_names_exact": six.text_type,
        "accession_id": six.text_type,
        "accession_id_exact": six.text_type,
        "primary_id_exact": six.text_type,
        "comparison": CSVofIntegers(),
        "ids": CSVofIntegers(),
        "ptm_data": IntegerLike(),
    }
)

raw_data_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "created": DatetimeWithTZ(),
        "primary_id": six.text_type,
        "gene_names": six.text_type,
        "gene_names_exact": six.text_type,
        "accession_id": six.text_type,
        "accession_id_exact": six.text_type,
        "primary_id_exact": six.text_type,
        "file_id": CSVofIntegers(),
        "ids": CSVofIntegers(),
    }
)

project_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "created": DatetimeWithTZ(),
        "title": six.text_type,
        "ids": CSVofIntegers(),
        "owner_ids": CSVofIntegers(),
        "project_type": GenericSeparatedValidator(str, ",")
    }
)

gene_name_map_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "accession_id": six.text_type,
        "gene_names": six.text_type,
        "project": IntegerLike()
    }
)

uniprot_record_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "created": DatetimeWithTZ(),
        "entry": six.text_type,
    }
)

curtain_query_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "link_id": six.text_type,
        "created": DatetimeWithTZ(),
        "username": six.text_type,
        "description": six.text_type,
        "curtain_type": GenericSeparatedValidator(str, ",")
    }
)