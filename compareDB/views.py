from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from sqlalchemy import Column, Integer, String, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemydiff
import pandas as pd
from compareDB.utils import *
from django.shortcuts import redirect
from rest_framework.utils import json
from compareDB.models import DatabseDetails, User
import numpy as np


class CreateUser(APIView):
    def post(self, request):
        request = json.loads(request.body)
        prevUser = User.objects.filter(email_id=request['username'])
        print("prev: ", len(prevUser))
        if len(prevUser) == 0:
            user = User(email_id=request['username'], password=request['password'])
            print(user)
            print(user.save())
            return Response('data saved into DB')
        else:
            return HttpResponse('fail')


class CreateDatabaseConfig(APIView):
    def post(self, request):
        request = json.loads(request.body)
        print(request)
        db_type, uname, password, domain, dbname = request['dbType'], request['dbUname'], request['dbPassword'], \
                                                   request['dbDomain'], request['dbName']
        connector_string = getConnectorSTring(db_type, uname, password, domain, dbname)
        print(connector_string)
        try:
            engine = create_engine(connector_string)
            databaseDetails = DatabseDetails(email_id=request['emailId'],
                                             database_name=request['dbName'],
                                             database_config=connector_string,
                                             database_type=request['dbType'],
                                             database_desctiption=request['description'])

            print(engine.connect())
            print(engine.table_names())


            prevConfig = DatabseDetails.objects.filter(email_id=request['emailId'],
                                                       database_name=request['dbName']
                                                        )
            print(len(prevConfig))
            if len(prevConfig) != 0:
                print('already present')
                return Response("duplicate")
            databaseDetails.save()
            return Response('Added To Database')
        except:
            print('FAIL')
            return Response('FAIL')


class GetDatabaseNameForUser(APIView):
    def __init__(self):
        self.response_data = []

    def get(self, request):
        uname, dbtype = request.GET['username'], request.GET['dbType']
        databaseDetails = DatabseDetails.objects.filter(email_id=uname, database_type=dbtype)
        for item in databaseDetails:
            current_data = {}
            current_data["dbname"] = item.database_name
            current_data["id"] = item.id
            self.response_data.append(current_data)
        print(self.response_data)
        return Response(self.response_data)


class CompareSchema(APIView):
    # get database id and fetch connector string from the database
    # compare schemas after getting two connector strings
    def get(self, request):
        connString1QuerySet = DatabseDetails.objects.filter(id=request.GET['db1id'])
        connString2QuerySet = DatabseDetails.objects.filter(id=request.GET['db2id'])

        connString1 = connString1QuerySet[0].database_config
        connString2 = connString2QuerySet[0].database_config

        result = sqlalchemydiff.compare(connString1, connString2)
        difference_unfiltered = result.errors

        difference_filtered = get_filtered_schema_compare(difference_unfiltered)
        lst_response = []
        for i in difference_filtered:
            lst_response.append({i: difference_filtered[i]})
        return Response((lst_response))


class GetTableNames(APIView):

    def get(self, request):
        try:
            connStringQuerySet = DatabseDetails.objects.filter(id=request.GET['dbid'])
            connString = connStringQuerySet[0].database_config
            engine = create_engine(connString)
            tableNamesResponse = engine.table_names()
            return Response(tableNamesResponse)
        except:
            print('couldnt get table names')
            return Response(['Enter details'])


class GetTableData(APIView):

    def get(self, request):
        connStringQuerySet = DatabseDetails.objects.filter(id=request.GET['dbid'])
        connString = connStringQuerySet[0].database_config
        engine = create_engine(connString)
        print(connString)
        sqlQuery = "select * from " + request.GET['tableName'] + ';'
        result = pd.read_sql(sqlQuery, engine)
        print(result)
        return Response(result)


class CompareTwoFiles(APIView):

    def get(self, request):
        return Response("File reading")


# class SQLExecutor(APIView):
#
#     def get(self, request):
#         db_type, uname, password, domain, dbname = getUrlParamatersGeneral(request)
#         connector_string = getConnectorSTring(db_type, uname, password, domain, dbname)
#         engine = create_engine(connector_string)
#         print(connector_string)
#         sqlQuery = request.GET['sqlQuery']
#         result = pd.read_sql(sqlQuery, engine)
#         print(result)
#         return Response(result)


class CompareTwoData(APIView):

    def get(self, request):
        connString1QuerySet = DatabseDetails.objects.filter(id=request.GET['db1id'])
        connString2QuerySet = DatabseDetails.objects.filter(id=request.GET['db2id'])
        connString1 = connString1QuerySet[0].database_config
        connString2 = connString2QuerySet[0].database_config
        sqlQuery_left = "select * from " + request.GET['db1TableName'] + ';'
        sqlQuery_right = "select * from " + request.GET['db2TableName'] + ';'
        engine_left = create_engine(connString1)
        engine_right = create_engine(connString2)
        df1 = pd.read_sql(sqlQuery_left, engine_left)
        df2 = pd.read_sql(sqlQuery_right, engine_right)
        difference = (None if pd.concat([df1, df2]).drop_duplicates(keep=False).fillna('').empty
                      else pd.concat([df1, df2]).drop_duplicates(keep=False).fillna(''))
        print(type(difference))
        try:
            source_same = pd.merge(difference, df1, how='inner')
            target_same = pd.merge(difference, df2, how='inner')
            r, c = source_same.shape
            source_series = pd.Series(np.array(["source" for i in range(r)]))
            r, c = target_same.shape
            target_series = pd.Series(np.array(["target" for i in range(r)]))
            source_same['S/T'] = source_series
            target_same['S/T'] = target_series
            new_difference_with_label = pd.concat([source_same, target_same])
            print(new_difference_with_label)
            response = {'source': df1,
                        'target': df2,
                        'difference': new_difference_with_label
                        }
        except:
            response = {'source': df1,
                        'target': df2,
                        'difference': {}
                        }
        return Response(response)
