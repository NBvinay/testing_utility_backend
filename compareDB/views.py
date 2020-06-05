from rest_framework.views import APIView
from rest_framework.response import Response
from sqlalchemy import Column, Integer, String, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemydiff
import pandas as pd
from compareDB.utils import *
from django.shortcuts import redirect
from rest_framework.utils import json


class CompareSchema(APIView):

    def get(self, request):
        # engine = create_engine('sqlite:///sales1.db', echo=True)
        #
        # Base = declarative_base()
        #
        # class Customers(Base):
        #     __tablename__ = 'customers'
        #
        #     id = Column(Integer, primary_key=True)
        #     name = Column(String)
        #     address = Column(String)
        #     email1 = Column(String, primary_key=True)
        #
        # class Producers(Base):
        #     __tablename__ = 'producers1'
        #
        #     prod_id = Column(Integer, primary_key=True)
        #     prod_name = Column(String)
        #     prod_address = Column(String)
        #     prod_email1 = Column(String, primary_key=True)
        #
        # Base.metadata.create_all(engine)
        #

        # uri_left = "sqlite:///sales.db"
        # uri_right = "sqlite:///sales1.db"
        # uri_left = "mysql+pymysql://root:@localhost:3308/collegeDb"
        # uri_right = "mysql+pymysql://root:@localhost:3308/new_collegeDb"


        # engine = create_engine(uri_right)
        # meta = MetaData(engine)
        # print("METADATA ::", meta)
        # return redirect("http://www.google.com")


        from sqlalchemy import MetaData
        db_type_left, uname_left, password_left, domain_left, dbname_left = getUrlParamatersLeft(request)
        db_type_right, uname_right, password_right, domain_right, dbname_right = getUrlParamatersRight(request)
        uri_left = getConnectorSTring(db_type_left, uname_left, password_left, domain_left, dbname_left)


        uri_right = getConnectorSTring(db_type_right, uname_right, password_right, domain_right, dbname_right)
        result = sqlalchemydiff.compare(uri_left, uri_right)
        print(result.is_match)
        print(result.errors)
        response = result.errors










        return Response(response)


class GetTableNames(APIView):

    def get(self, request):
        db_type, uname, password, domain, dbname = getUrlParamatersGeneral(request)
        print("request params : ", db_type, uname, password, domain, dbname)
        connector_string = getConnectorSTring(db_type, uname, password, domain, dbname)
        print("connector String: ", connector_string)
        try:
            engine = create_engine(connector_string)
            print(connector_string)
            print(engine.table_names())
            print("*" * 10)
            tableNamesResponse = engine.table_names()
            return Response(tableNamesResponse)
        except:
            print('couldnt get table names')
            return Response(['Enter details'])

class GetTableData(APIView):

    def get(self, request):
        db_type, uname, password, domain, dbname = getUrlParamatersGeneral(request)
        connector_string = getConnectorSTring(db_type, uname, password, domain, dbname)
        engine = create_engine(connector_string)
        print(connector_string)
        sqlQuery = "select * from "+request.GET['tableName']+';'
        result = pd.read_sql(sqlQuery, engine)
        print(result)
        return Response(result)

class CompareTwoFiles(APIView):

    def get(self, request):
        return Response("File reading")

#
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
        db_type_left, uname_left, password_left, domain_left, dbname_left, sqlQuery_left = getUrlParamatersLeftWithQuery(
            request)
        db_type_right, uname_right, password_right, domain_right, dbname_right, sqlQuery_right = getUrlParamatersRightWithQuery(
            request)
        uri_left = getConnectorSTring(db_type_left, uname_left, password_left, domain_left, dbname_left)
        uri_right = getConnectorSTring(db_type_right, uname_right, password_right, domain_right, dbname_right)
        engine_left = create_engine(uri_left)
        engine_right = create_engine(uri_right)
        df1 = pd.read_sql(sqlQuery_left, engine_left)
        df2 = pd.read_sql(sqlQuery_right, engine_right)

        print(df1)
        print(df2)
        print('DIFFERENCE')
        print(pd.concat([df1, df2]).drop_duplicates(keep=False))
        # request_body = json.loads(request.body)
        # df1, df2 = pd.DataFrame(request_body[0]), pd.DataFrame(request_body[1])
        return Response(
            None if pd.concat([df1, df2]).drop_duplicates(keep=False).fillna('').empty
            else pd.concat([df1, df2]).drop_duplicates(keep=False).fillna(''))
