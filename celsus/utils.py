import io
import json

import numpy as np
import pandas as pd
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework_simplejwt.tokens import AccessToken
from uniprotparser.betaparser import UniprotParser

from celsus.models import Project, GeneNameMap, UniprotRecord, Comparison, DifferentialSampleColumn, \
    DifferentialAnalysisData, RawSampleColumn, RawData


def get_user_from_token(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        authorization = request.META['HTTP_AUTHORIZATION'].replace("Bearer ", "")
        access_token = AccessToken(authorization)
        user = User.objects.filter(pk=access_token["user_id"]).first()
        if user:
            return user
    return


def is_user_staff(request):
    user = request.user
    if not user:
        user = get_user_from_token(request)
    if user:
        if user.is_staff:
            return True
    return False


def delete_file_related_objects(file):
    for c in file.comparisons.all():
        with transaction.atomic():
            for column in c.differential_sample_columns.all():
                column.delete()
            for da in c.differential_analysis_datas.all():
                da.delete()
    with transaction.atomic():
        for r in file.raw_datas.all():
            r.delete()
    for rc in file.raw_sample_columns.all():
        with transaction.atomic():
            rc.delete()


def calculate_boxplot_parameters(values):
    q1, med, q3 = np.percentile(values, [25, 50, 75])

    iqr = q3 - q1

    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr

    wisker_high = np.compress(values <= high, values)
    wisker_low = np.compress(values >= low, values)

    real_high_val = np.max(wisker_high)
    real_low_val = np.min(wisker_low)

    return {"low": real_low_val, "q1": q1, "med": med, "q3": q3, "high": real_high_val}

def check_nan_return_none(value):
    if pd.notnull(value):
        return value
    return None

def get_uniprot_data(df, column_name):
    primary_id = df[column_name].str.split(";")
    primary_id = primary_id.explode().unique()
    parser = UniprotParser()
    uni_df = []
    for p in parser.parse(primary_id):
        uniprot_df = pd.read_csv(io.StringIO(p), sep="\t")
        uni_df.append(uniprot_df)
    if len(uni_df) == 1:
        uni_df = uni_df[0]
    elif len(uni_df) > 1:
        uni_df = pd.concat(uni_df, ignore_index=True)
    else:
        return pd.DataFrame()
    uni_df.set_index("From", inplace=True)
    return uni_df

def process_differential_analysis_data(data, file, df):
    geneMap = {}
    no_geneMap = []
    accession_id_column = "primary_id"
    ptm_data = False
    parameters = data
    file.file_parameters = json.dumps(parameters)
    if "project_id" in parameters:
        project = Project.objects.filter(pk=int(parameters["project_id"])).first()
        project.files.add(file)
        project.save()
        if project.ptm_data:
            accession_id_column = "accession_id"
            ptm_data = True
    file.save()
    for i in df[parameters[accession_id_column]]:
        if pd.notnull(i):
            g = GeneNameMap.objects.filter(accession_id=i).first()
            if g:
                geneMap[i] = g
            else:
                no_geneMap.append(i)
    uni_df = get_uniprot_data(
        df[df[parameters[accession_id_column]].isin(no_geneMap)],
        parameters[accession_id_column])
    uniprot_record_map = {}
    if not uni_df.empty:
        with transaction.atomic():
            for ind, row in uni_df.iterrows():
                uniprot_record = UniprotRecord.objects.filter(entry=row["Entry"]).first()
                if not uniprot_record:
                    uniprot_record = UniprotRecord(entry=row["Entry"], record=json.dumps(row.to_dict()))
                uniprot_record.save()
                uniprot_record_map[uniprot_record.entry] = uniprot_record
    for i in parameters["comparisons"]:
        if "data" in parameters["comparisons"][i]:
            comp = Comparison.objects.filter(pk=int(
                parameters["comparisons"][i]["data"]["id"])).first()
            comp.file = file
            comp.save()
            dsc_fc = DifferentialSampleColumn(name=i, column_type="FC")
            dsc_fc.comparison = comp
            dsc_s = DifferentialSampleColumn(name=parameters["comparisons"][i]["significant"], column_type="P")
            dsc_s.comparison = comp
            dsc_fc.save()
            dsc_s.save()
            columns = [parameters["primary_id"], dsc_fc.name, dsc_s.name]
            if ptm_data:
                columns = columns + [
                    parameters["sequence_window"],
                    parameters["peptide_sequence"],
                    parameters["probability_score"],
                    parameters["ptm_position"],
                    parameters["ptm_position_in_peptide"],
                    parameters[accession_id_column],
                ]
            temp_df = df[columns]
            temp_df["Gene Names"] = ""
            # da_objects = []

            for ind, row in temp_df.iterrows():
                if row[parameters[accession_id_column]] not in geneMap:
                    if pd.notnull(row[parameters[accession_id_column]]):
                        for p in row[parameters[accession_id_column]].split(";"):
                            if p in uni_df.index:
                                uni_d = uni_df.loc[p]
                                if type(uni_d) is pd.DataFrame:
                                    for uni_ind, uni_r in uni_d.iterrows():
                                        if not pd.isnull(uni_r["Gene Names"]):
                                            gene = GeneNameMap(
                                                accession_id=row[parameters[accession_id_column]],
                                                gene_names=uni_r["Gene Names"].upper(), entry=uni_r["Entry"])
                                            gene.save()
                                            if uni_r["Entry"] in uniprot_record_map:
                                                gene.uniprot_record.add(uniprot_record_map[uni_r["Entry"]])
                                            gene.save()
                                            geneMap[row[parameters[accession_id_column]]] = gene
                                            break
                                else:
                                    if not pd.isnull(uni_df.loc[p]["Gene Names"]):
                                        gene = GeneNameMap(accession_id=row[parameters[accession_id_column]],
                                                           gene_names=uni_df.loc[p]["Gene Names"].upper(),
                                                           entry=uni_df.loc[p]["Entry"])
                                        gene.save()
                                        if uni_df.loc[p]["Entry"] in uniprot_record_map:
                                            gene.uniprot_record.add(uniprot_record_map[uni_df.loc[p]["Entry"]])
                                        gene.save()
                                        geneMap[row[parameters[accession_id_column]]] = gene
                                break
                da = DifferentialAnalysisData(primary_id=row[parameters["primary_id"]],
                                              fold_change=check_nan_return_none(row[dsc_fc.name]),
                                              significant=check_nan_return_none(row[dsc_s.name]))
                da.comparison = comp
                if row[parameters[accession_id_column]] in geneMap:
                    da.gene_names = geneMap[row[parameters[accession_id_column]]]
                    if ptm_data:
                        da.peptide_sequence = check_nan_return_none(row[parameters["peptide_sequence"]])
                        da.probability_score = check_nan_return_none(row[parameters["probability_score"]])
                        da.ptm_position = check_nan_return_none(row[parameters["ptm_position"]])
                        da.ptm_position_in_peptide = check_nan_return_none(
                            row[parameters["ptm_position_in_peptide"]])
                        da.ptm_data = True
                        da.sequence_window = check_nan_return_none(row[parameters["sequence_window"]])

                da.save()
            # da_objects.append(da)
        # DifferentialAnalysisData.objects.bulk_create(da_objects)

def process_raw_data(parameters, file, df):
    df = df.where(pd.notnull(df), None)
    geneMap = {}
    no_geneMap = []
    file.file_parameters = json.dumps(parameters)
    file.save()

    if "project_id" in parameters:
        project = Project.objects.filter(pk=int(parameters["project_id"])).first()
        project.files.add(file)
        project.save()

    accession_id_column = parameters["primary_id"]
    s = ""
    if "accession_id" in parameters:
        if parameters["accession_id"]:
            accession_id_column = parameters["accession_id"]
    for i, r in df.iterrows():
        if pd.notnull(r[accession_id_column]):
            g = GeneNameMap.objects.filter(accession_id=r[accession_id_column]).first()

            if g:
                geneMap[r[accession_id_column]] = g
            else:
                g = DifferentialAnalysisData.objects.filter(primary_id=r[parameters["primary_id"]],
                                                            comparison__file__project_id=int(
                                                                parameters["project_id"])).first()
                if g:
                    if g.gene_names:
                        geneMap[r[accession_id_column]] = g.gene_names
                    else:
                        no_geneMap.append(r[accession_id_column])
                else:
                    no_geneMap.append(r[accession_id_column])
    uni_df = get_uniprot_data(df[df[accession_id_column].isin(no_geneMap)], accession_id_column)
    uniprot_record_map = {}

    if not uni_df.empty:
        with transaction.atomic():
            for ind, row in uni_df.iterrows():
                uniprot_record = UniprotRecord.objects.filter(entry=row["Entry"]).first()
                if not uniprot_record:
                    uniprot_record = UniprotRecord(entry=row["Entry"], record=json.dumps(row.to_dict()))
                uniprot_record.save()
                uniprot_record_map[uniprot_record.entry] = uniprot_record

        for i, row in df.iterrows():
            if pd.notnull(row[accession_id_column]):
                if row[accession_id_column] not in geneMap:
                    for p in row[accession_id_column].split(";"):
                        if p in uni_df.index:
                            uni_d = uni_df.loc[p]
                            if type(uni_d) is pd.DataFrame:
                                for uni_ind, uni_r in uni_d.iterrows():
                                    if not pd.isnull(uni_r["Gene Names"]):
                                        gene = GeneNameMap(
                                            accession_id=row[accession_id_column],
                                            gene_names=uni_r["Gene Names"].upper(),
                                            entry=uni_r["Entry"])
                                        if uni_r["Entry"] in uniprot_record_map:
                                            gene.uniprot_record.add(uniprot_record_map[uni_r["Entry"]])
                                        gene.save()
                                        geneMap[row[accession_id_column]] = gene
                                        break
                            else:
                                if not pd.isnull(uni_df.loc[p]["Gene Names"]):
                                    gene = GeneNameMap(accession_id=row[accession_id_column],
                                                       gene_names=uni_df.loc[p]["Gene Names"].upper(),
                                                       entry=uni_df.loc[p]["Entry"])
                                    gene.save()
                                    if uni_df.loc[p]["Entry"] in uniprot_record_map:
                                        gene.uniprot_record.add(uniprot_record_map[uni_df.loc[p]["Entry"]])
                                    gene.save()
                                    geneMap[row[accession_id_column]] = gene

                            break

    for s in parameters["samples"]:
        columns = [parameters["primary_id"], s]
        if accession_id_column != parameters["primary_id"]:
            columns = columns + [accession_id_column]
        temp_df = df[columns]
        rsc = RawSampleColumn(name=s, file=file)
        rsc.save()
        # raw_objects = []
        with transaction.atomic():
            for i, row in temp_df.iterrows():
                value = np.nan
                try:
                    value = float(row[s])
                except:
                    continue
                if row[accession_id_column] in geneMap:
                    # if row[accession_id_column] == s:
                    #    print(s)
                    #    print(geneMap[row[accession_id_column]].gene_names)

                    raw_data = RawData(primary_id=row[parameters["primary_id"]],
                                       raw_sample_column=rsc,
                                       gene_names=geneMap[row[accession_id_column]],
                                       value=check_nan_return_none(value),
                                       file=file)
                else:
                    raw_data = RawData(primary_id=row[parameters["primary_id"]], raw_sample_column=rsc,
                                       value=check_nan_return_none(value),
                                       file=file)
                raw_data.save()
            # raw_objects.append(raw_data)
        # RawData.objects.bulk_create(raw_objects)