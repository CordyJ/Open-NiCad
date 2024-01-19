#!/usr/bin/env python
# coding: utf-8

# # Object-Oriented Machine Learning Pipeline for Pandas and Koalas DataFrames
# 
# ## End-to-end process of developing Spark-enabled machine learning pipeline using Pandas, Koalas, Scikit-Learn, and mlflow

# In the article [Python Data Preprocessing Using Pandas DataFrame, Spark DataFrame, and Koalas DataFrame](https://towardsdatascience.com/python-data-preprocessing-using-pandas-dataframe-spark-dataframe-and-koalas-dataframe-e44c42258a8f), I used a public dataset to evaluate and compare the basic functionality of Pandas, Spark, and Koalas DataFrames in typical data preprocessing steps for machine learning. 
# 
# In this article, I use the [Interview Attendance Problem for Kaggle competition](https://www.kaggle.com/vishnusraghavan/the-interview-attendance-problem) to demonstrate an end-to-end process of developing a machine learning pipeline for both Pandas and Koalas dataframes using Pandas, Koalas, Scikit-Learn, and mlflow. This is achieved by:
# * Developing a scikit-learn data preprocessing pipeline using Pandas with scikit-learn
# * Developing a scikit-learn data preprocessing pipeline for Spark by combining scikit-learn with Koalas
# * Developing a machine learning pipeline by combining scikit-learn with mlflow
# 
# The end-to-end development process is based on the [Cross-industry standard process for data mining](https://en.wikipedia.org/wiki/Cross-industry_standard_process_for_data_mining). As shown in the diagram below, it consists of six major phases:
# * Business Understanding
# * Data Understanding
# * Data Preparation
# * Modeling
# * Evaluation
# * Deployment
# 
# <img src="./images/standard_process.png" width="180" height="360">
# 
# For convenience of discussion, it is assumed that the following Python libraries have been installed on a local machine such as Mac:
# * Anaconda (conda 4.7.10) with Python 3.6, Numpy, Pandas, Matplotlib, and Scikit-Learn
# * [pyspark 2.4.4](https://spark.apache.org/releases/spark-release-2-4-4.html)
# * [Koalas](https://github.com/databricks/koalas)
# * [mlflow](https://www.mlflow.org/docs/latest/index.html)
# 
# ## 1. Business Understanding
# 
# The key point of business understanding is to understand the business problem to be solved. As an example, the following is a brief description of the Kaggle interview attendance problem: 
# 
# Given a set of questions that are asked by a recruiter while scheduling an interview with a candidate, how to use the answers to those questions from the candidate to determine whether the expected attendance is yes, no, or uncertain.
# 
# ## 2. Data Understanding
# 
# Once the business problem is understood, the next step is to identify where (i.e., data sources) and how we can collect data from which a machine learning solution to the problem can be built. 
# 
# The labeled dataset for the Kaggle interview attendance problem has been collected as a csv file from the recruitment industry in India by the researchers over a period of more than 2 years between September 2014 and January 2017.  
# 
# The following table shows the first five rows of the raw dataset. This dataset is collected for supervised machine learning and the column of Observed Attendance holds the labels.

# ## Setup Environment
# 
# * conda create -n python36 python=3.6 anaconda
# * conda activate python36
# * pip install koalas
# * pip install mlflow
# * pip install pyspark

# In[1]:


import numpy as np
import pandas as pd
import databricks.koalas as ks
import matplotlib.pyplot as plt
import matplotlib as mpl
from   datetime import datetime
import os

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

from sklearn.metrics import make_scorer
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

get_ipython().run_line_magic('matplotlib', 'inline')


# The following code is to load the dataset csv file (e.g., Interview_Attendance_Data.csv) from your local machine into Koalas DataFrame. The dataset can be downloaded from Kaggle site: https://www.kaggle.com/vishnusraghavan/the-interview-attendance-problem/

# In[2]:


dataset_file = './data/Interview_Attendance_Data.csv'
ks_df = ks.read_csv(dataset_file)
ks_df.head()


# ## 3. Data Preparation
# 
# The main goal of data preparation is to transform the raw dataset into appropriate format so that the transformed data can be effectively consumed by a target machine learning model. 
# 
# In the raw dataset, the column of Name(Cand ID)	contains candidate unique identifier, which does not have much prediction power and thus can be dropped. In addition, all of the columns (i.e., columns from _c22 to _c26 for Koalas dataframe, or columns from Unnamed: 22 to Unnamed: 26 for Pandas dataframe) have no data and thus can safely be dropped as well.
# 
# Except for the date of interview, all of the other columns in the dataset have categorical (textual) values. In order to use machine learning to solve the problem, those categorical values must be transformed into numerical values because a machine learning model can only cosume numerical data. 
# 
# The column of Date of Interview should be splitted into Day, Month, and Year to increase prediction power since the information of individual Day and Month can be more coorelated with seasonable jobs compared with a string of date. 
# 
# The columns of Nature of Skillset and Candidate Native location have a large number of unique entries. These will introduce a large number of new derived features after one-hot encoding. Too many features can lead to a [curse of dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality) problem. To alleviate such problem, the values of these two columns are re-divided into a smaller number of buckets.
# 
# The above data preprocessing/transformation can be summarized as following steps:
# * Bucketing skillset
# * Bucketing candidate native location
# * Parsing interview date
# * Changing categorical values to uppercase and dropping less useful features 
# * One-Hot encoding categorical values
# 
# These steps are implemented by developing an Object-Oriented data preprocessing pipeline for both Pandas and Koalas dataframes using Pandas, Koalas and scikit-learn pipeline API (i.e., BaseEstimator, TransformerMixin, Pipeline).

# Main Goals:
# 
# 
# 
# 1. Create a model predicting if a candidate will attend an interview. This will be indicated by the "Observed Attendance" column in the data set. Create the model only using the records where this column is not null
# 
# 2. Provide a probability and a prediction for the candidates where the "Observed Attendance" column is null.

# ### 3.1 Transforming Column Values
# 
# Several data preprocessing steps share a common operation of transforming the values of a particular column in a Koalas dataframe. But, as described in [Koalas Series](https://koalas.readthedocs.io/en/latest/reference/api/databricks.koalas.Series.iloc.html#databricks.koalas.Series.iloc), the Koalas Series does not support some of the common Pandas indexing mechanisms such as df.iloc[0]. Because of this, there is no simple method of traversing and changling the values of a column in a Koalas dataframe. The other difficulty is that Koalas does not allow to build a new Koalas Series object from scratch and then add it as a new column in an existing Koalas dataframe. It only allows to use a new Koalas Series object that is built from the existing columns of a Koalas dataframe. These difficulties are avoided by defining a global function to call the apply() method of a Koalas Series object. 

# In[3]:


def transformColumn(column_values, func, func_type):
    '''
    This function is to transform a given column (column_values) of a Koalas DataFrame or Series.
    This function is needed because the current Koalas requires that the applied function has 
    an explictly specified return type. Because of this, we cannot use lambda function directly 
    since lambda function does not have an explicit return type.
    '''
    def transform_column(column_element) -> func_type:
        return func(column_element)
    
    cvalues = column_values
        
    cvalues = cvalues.apply(transform_column)
            
    return cvalues


# ### 3.2 Bucketing Skillset
# 
# To alleviate the curse of dimensionality issue, the transform() method of the BucketSkillset class divides the unique values of the skillset column into smaller number of buckets by combining those values that appear less than 9 times into one same value of Others.

# In[4]:


class BucketSkillset(BaseEstimator, TransformerMixin):
    def __init__(self):
        '''
        This class is to re-bucket the skill sets and candidates location features 
        to combine small catogaries into one catogary 'Others'.
        '''
        self.skillset = ['JAVA/J2EE/Struts/Hibernate', 'Fresher', 'Accounting Operations', 'CDD KYC', 'Routine', 'Oracle', 
          'JAVA/SPRING/HIBERNATE/JSF', 'Java J2EE', 'SAS', 'Oracle Plsql', 'Java Developer', 
          'Lending and Liabilities', 'Banking Operations', 'Java', 'Core Java', 'Java J2ee', 'T-24 developer', 
          'Senior software engineer-Mednet', 'ALS Testing', 'SCCM', 'COTS Developer', 'Analytical R & D', 
          'Sr Automation Testing', 'Regulatory', 'Hadoop', 'testing', 'Java', 'ETL', 'Publishing']       
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        '''
        This method is to re-bucket the skill sets features.
        '''
        
        func = lambda x: x if x in self.skillset else 'Others'
               
        X1 = X.copy()
        
        cname = 'Nature of Skillset'
        cvalue = X1[cname]
        
        if type(X1) == ks.DataFrame:  
            cvalue = transformColumn(cvalue, func, str)
            X1[cname] = cvalue
        elif type(X1) == pd.DataFrame:
            X2 = map(func, cvalue)
            X1[cname] = pd.Series(X2)
        else:
            print('BucketSkillset: unsupported dataframe: {}'.format(type(X1)))
            pass
            
        return X1  


# ### 3.3 Bucketing candidate native location
# Similarly to bucketing skillset, to alleviate the curse of dimensionality issue, the transform() method of the BucketLocation class divides the unique values of the candidate native location column into smaller number of buckets by combining those values that appear less than 12 times into one same value of Others.

# In[5]:


class BucketLocation(BaseEstimator, TransformerMixin):
    def __init__(self):
        '''
        This class is to re-bucket the candidates location features 
        to combine small catogaries into one catogary 'Others'.
        '''
        
        self.candidate_locations = ['Chennai', 'Hyderabad', 'Bangalore', 'Gurgaon', 'Cuttack', 'Cochin', 
                          'Pune', 'Coimbatore', 'Allahabad', 'Noida', 'Visakapatinam', 'Nagercoil',
                          'Trivandrum', 'Kolkata', 'Trichy', 'Vellore']
        
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        '''
        This method is to re-bucket the candidates native locations features.
        '''
            
        X1 = X.copy()
        
        func = lambda x: x if x in self.candidate_locations else 'Others'
        
        cname = 'Candidate Native location'
        cvalue = X1[cname]
        if type(X1) == ks.DataFrame: 
            cvalue = transformColumn(cvalue, func, str)
            X1[cname] = cvalue
        elif type(X1) == pd.DataFrame:
            X2 = map(func, cvalue)
            X1[cname] = pd.Series(X2)
        else:
            print('BucketLocation: unsupported dataframe: {}'.format(type(X1)))
            pass
            
        return X1  


# ### 3.4 Parsing Interview Date
# 
# The values of the column of Date of Interview are messy in that various formats are used. For instance not only different delimits are used to separate day, month, and year, but also different orders of day, month, and year are followed. This is handled by the local \_parseDate() and transform_date() methods of the ParseInterviewDate class.  The overall functionality of the transform() method is to separate the interview date string into individual day, month, and year values. 

# In[6]:


class ParseInterviewDate(BaseEstimator, TransformerMixin):
    def __init__(self):
        '''
        This class is to splits the date of interview into day (2 digits), month (2 digits), year (4 digits).
        '''     
    def __parseDate(self, string, delimit):
        try:
            if ('&' in string):
                subs = tuple(string.split('&'))
                string = subs[0]
        except:
            print ('TypeError: {}'.format(string))
            return None
        
        string = string.strip()
        
        try:
            d = datetime.strptime(string, '%d{0}%m{0}%Y'.format(delimit))
        except:
            try:
                d = datetime.strptime(string, '%d{0}%m{0}%y'.format(delimit))
            except:
                try:
                     d = datetime.strptime(string, '%d{0}%b{0}%Y'.format(delimit))
                except:
                    try:
                         d = datetime.strptime(string, '%d{0}%b{0}%y'.format(delimit))
                    except:
                        try:
                            d = datetime.strptime(string, '%b{0}%d{0}%Y'.format(delimit))
                        except:
                            try:
                                d = datetime.strptime(string, '%b{0}%d{0}%y'.format(delimit))
                            except:
                                d = None
        return d
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        '''
        This method splits the date of interview into day (2 digits), month (2 digits), year (4 digits).
        '''
        
        def transform_date(ditem):
            if (isinstance(ditem, str) and len(ditem) > 0):
                if ('.' in ditem):
                    d = self.__parseDate(ditem, '.')
                elif ('/' in ditem):
                    d = self.__parseDate(ditem, '/')
                elif ('-' in ditem):
                    d = self.__parseDate(ditem, '-')
                elif (' ' in ditem):
                    d = self.__parseDate(ditem, ' ')
                else:
                    d = None
                    
                if (d is None):
                    return 0, 0, 0
                else:
                    return d.day, d.month, d.year
                
        def get_day(column_element) -> int:
            try:
                day, month, year = transform_date(column_element)
                return int(day)
            except:
                return 0
        
        def get_month(column_element) -> int:
            try:
                day, month, year = transform_date(column_element)
                return int(month)
            except:
                return 0
        
        def get_year(column_element) -> int:
            try:
                day, month, year = transform_date(column_element)
                return int(year)
            except:
                return 0
            
        def pandas_transform_date(X1):
            days = []
            months = []
            years = []
            ditems = X1['Date of Interview'].values
            for ditem in ditems:
                if (isinstance(ditem, str) and len(ditem) > 0):
                    if ('.' in ditem):
                        d = self.__parseDate(ditem, '.')
                    elif ('/' in ditem):
                        d = self.__parseDate(ditem, '/')
                    elif ('-' in ditem):
                        d = self.__parseDate(ditem, '-')
                    elif (' ' in ditem):
                        d = self.__parseDate(ditem, ' ')
                    else:
                        d = None
                    
                    if (d is None):
                        # print("{}, invalid format of interview date!".format(ditem))
                        days.append(0) # 0 - NaN
                        months.append(0)
                        years.append(0)
                    else:
                        days.append(d.day) 
                        months.append(d.month)
                        years.append(d.year)
                else:
                    days.append(0)
                    months.append(0)
                    years.append(0)
        
            X1['Year'] = years
            X1['Month'] = months
            X1['Day'] = days
            
            return X1
        
        X1 = X.copy()
        
        if type(X1) == ks.DataFrame: 
            X1['Year'] = X1['Date of Interview']
            X1['Month'] = X1['Date of Interview']
            X1['Day'] = X1['Date of Interview']
        
            func_map = {'Year' : get_year, 'Month' : get_month, 'Day' : get_day}
            for cname in func_map:
                cvalue = X1[cname]
                cvalue = cvalue.apply(func_map[cname])
                X1[cname] = cvalue
        elif type(X1) == pd.DataFrame:
            X1 = pandas_transform_date(X1)
        else:
            print('ParseInterviewDate: unsupported dataframe: {}'.format(type(X1)))
            pass 
         
        return X1   


# ### 3.5 Changing Categorical Values to Uppercase and Dropping Less Useful Features
# 
# The transform() method of the FeaturesUppercase class is to change the values of categorical features to uppercase and at the same time drop less useful features.

# In[7]:


class FeaturesUppercase(BaseEstimator, TransformerMixin):
    def __init__(self, feature_names, drop_feature_names):
        '''
        This class is to change feature values to uppercase.
        '''
        self.feature_names      = feature_names
        self.drop_feature_names = drop_feature_names
    
    def fit(self, X, y=None):
        return self
        
    def transform(self, X, y=None):
        '''
        This method is to change feature values to uppercase.
        '''
        
        func = lambda x: x.strip().upper()
        
        X1 = X.copy()
        
        for fname in self.feature_names:
            values = X1[fname]
            values = values.fillna('NaN')
            if type(X1) == ks.DataFrame: 
                values = transformColumn(values, func, str)
            elif type(X1) == pd.DataFrame:
                values = map(lambda x: x.strip().upper(), values)
            else:
                print('FeaturesUppercase: unsupported dataframe: {}'.format(type(X1)))   
            X1[fname] = values
            
        # drop less important features
        X1 = X1.drop(self.drop_feature_names, axis=1)
            
        return X1   


# ### 3.6 One-Hot Encoding Categorical Values
# 
# The transform() method of the OneHotEncodeData class calls the get_dummies() method of Koalas dataframe to one-hot encode the values of categorical values. 

# In[8]:


# https://www.guru99.com/pyspark-tutorial.html
class OneHotEncodeData(BaseEstimator, TransformerMixin):
    def __init__(self):
        '''
        This class is to one-hot encode the categorical features.
        '''
        self.one_hot_feature_names = ['Client name', 
                        'Industry', 
                        'Location', 
                        'Position to be closed', 
                        'Nature of Skillset',
                        'Interview Type', 
                        #'Name(Cand ID)', 
                        'Gender', 
                        'Candidate Current Location',
                        'Candidate Job Location', 
                        'Interview Venue', 
                        'Candidate Native location',
                        'Have you obtained the necessary permission to start at the required time',
                        'Hope there will be no unscheduled meetings',
                        'Can I Call you three hours before the interview and follow up on your attendance for the interview',
                        'Can I have an alternative number/ desk number. I assure you that I will not trouble you too much',
                        'Have you taken a printout of your updated resume. Have you read the JD and understood the same',
                        'Are you clear with the venue details and the landmark.',
                        'Has the call letter been shared', 
                        'Marital Status']
        self.label_encoders   = None
        self.one_hot_encoders = None
        
    def fit(self, X, y=None):       
        return self
    
    def transform(self, X, y=None):  
        X1 = X.copy()
        if type(X1) == ks.DataFrame: 
            X1 = ks.get_dummies(X1)
        elif type(X1) == pd.DataFrame:
            X1 = pd.get_dummies(X1)
        else:
            print('OneHotEncodeData: unsupported dataframe: {}'.format(type(X1)))
            pass
        
        return X1


# ## 4. Modeling
# 
# Once the dataset has been prepared, the next step is modeling. The main goals of modeling are:
# * Identify machine learning algorithm
# * Create and train machine learning model
# * Tune the hyperparameters of machine learning algorithm
# 
# In this article we use the scikit-learn RandomForestClassifier algorithm for demonstration purpose. Grid search is used to tune the hyperparameters (number of estimators and max depth) of the algorithm, and mlflow is used to train model, track, and compare the performance metrics of different models. 
# 
# The GridSearch class is to implement grid search and the method of mlFlow() of the PredictInterview class is to call other methods to train model, use a trained model to predict results, and record model performance metrocs using mlflow API.

# In[9]:


class GridSearch(object):
    def __init__(self, cv=10):
        '''
        This class finds the best model via Grid Search.
        '''
        self.grid_param = [
            {'n_estimators': range(68,69), # range(60, 70) # best 68
             'max_depth'   : range(8,9)}   # range(5, 10)}  # best 8
        ]
        self.cv = cv
        self.scoring_function = make_scorer(f1_score, greater_is_better=True) 
        self.gridSearch = None
        
    def fit(self, X, y):
        rfc = RandomForestClassifier()
        self.gridSearchCV = GridSearchCV(rfc, self.grid_param, cv=self.cv, scoring=self.scoring_function)
        self.gridSearchCV.fit(X, y)
        return self.gridSearchCV.best_estimator_


# In[10]:


class PredictInterview(object):
    def __init__(self, dataset_file=dataset_file, use_koalas=True):
        '''
        This class is to predict the probability of a candidate attending scheduled interviews.
        '''
        self.use_koalas = use_koalas
        self.dataset_file_name = dataset_file
        self.feature_names = ['Date of Interview', 
                       'Client name', 
                       'Industry', 
                       'Location', 
                       'Position to be closed', 
                       'Nature of Skillset',
                       'Interview Type', 
                       #'Name(Cand ID)',
                       'Gender', 
                       'Candidate Current Location',
                       'Candidate Job Location', 
                       'Interview Venue', 
                       'Candidate Native location',
                       'Have you obtained the necessary permission to start at the required time',
                       'Hope there will be no unscheduled meetings',
                       'Can I Call you three hours before the interview and follow up on your attendance for the interview',
                       'Can I have an alternative number/ desk number. I assure you that I will not trouble you too much',
                       'Have you taken a printout of your updated resume. Have you read the JD and understood the same',
                       'Are you clear with the venue details and the landmark.',
                       'Has the call letter been shared', 'Marital Status']
        
        if self.use_koalas:
            self.drop_feature_names = [
                'Name(Cand ID)',
                'Date of Interview', 
                '_c22',
                '_c23',
                '_c24',
                '_c25',
                '_c26']
        else: # use Pandas
            self.drop_feature_names = [
                'Unnamed: 22',
                'Unnamed: 23',
                'Unnamed: 24',
                'Unnamed: 25',
                'Unnamed: 26']
        
        self.dataset = None
        self.rfc     = None
        self.gridSearch = None
        self.X_train = None
        self.y_train = None
        self.X_test  = None
        self.y_test  = None
        self.y_pred  = None
        self.X_clean = None
        self.y_clean = None
        self.X_train_encoded = None
        self.X_test_encoded  = None
        self.y_train_encoded = None
        self.accuracy_score  = None 
        self.f1_score        = None
        self.oneHotEncoder   = None
        self.X_test_name_ids = None
        self.pipeline = None
        
        
    def loadData(self, path=None):
        '''
        This method loads a dataset file as a Pandas DataFrame, assuming that the dataset file is in csv format.
        It also shuffles the loaded dataset as part of data preprocessing.
        '''
        if (path != None):
            path = os.path.join(path, self.dataset_file_name)
        else:
            path = self.dataset_file_name
         
        if self.use_koalas:
            dataset = ks.read_csv(path)  
        else:
            dataset = pd.read_csv(path)
        
        # shuffle data 
        self.dataset = dataset.sample(frac=1.0) 
        
        return self.dataset     
    
    def PreprocessData(self):
        '''
        This method preprocesses the loaded dataset before applying one-hot encoding.
        '''
            
        y = self.dataset['Observed Attendance']      # extract labels y
        if self.use_koalas:
            X = self.dataset.drop('Observed Attendance') # extract features X
        else:
            X = self.dataset.drop(['Observed Attendance'], axis=1) 
        
        self.oneHotEncoder = OneHotEncodeData()
        
        self.pipeline = Pipeline([
            ('bucket_skillset', BucketSkillset()),
            ('bucket_location', BucketLocation()),
            ('parse_interview_date', ParseInterviewDate()),
            ('features_to_uppercase', FeaturesUppercase(self.feature_names, self.drop_feature_names)),
            ('one_hot_encoder', self.oneHotEncoder)
        ])
        
        X_1hot = self.pipeline.fit_transform(X)
        
        # fill up missing labels and then change labels to uppercase
        y = y.fillna('NaN')
        
        if self.use_koalas:
            func = lambda x: x.strip().upper()
            y_uppercase = transformColumn(y, func, str) 
        else:
            y_uppercase = map(lambda x: x.strip().upper(), y.values)
            y_uppercase = pd.Series(y_uppercase)
        
        # separate labeled records from unlabeled records
        self.X_train_encoded = X_1hot[y_uppercase != 'NAN']
        self.X_test_encoded  = X_1hot[y_uppercase == 'NAN']
        
        # save Names/ID for reporting later one
        self.X_test_name_ids = self.dataset['Name(Cand ID)'].loc[y_uppercase == 'NAN']
        
        y_train = y_uppercase.loc[y_uppercase != 'NAN']
        
        # encode labels as follows: 0 - NO, 1 - YES, NAN - NAN
        if self.use_koalas:
            func = lambda x: 1 if x == 'YES' else 0
            y = transformColumn(y_train, func, int)
        else:
            y = map(lambda x: 1 if x == 'YES' else 0, y_train)
            y = pd.Series(y)
        
        self.y_train_encoded = y
        
        self.X_clean = X_1hot
        self.y_clean = y_uppercase
        
        return None
    
    def __splitData(self):
        '''
        This method triggers data preprocsssing and split dataset into training and testing datasets.
        '''
        if self.use_koalas:
            X_train_encoded = self.X_train_encoded.to_numpy()
            y_train_encoded = self.y_train_encoded.to_numpy()
        else:
            X_train_encoded = self.X_train_encoded.values
            y_train_encoded = self.y_train_encoded.values
            
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_train_encoded, 
                                                                                y_train_encoded, 
                                                                                test_size = 0.25, random_state = 0)
        return (self.X_train, self.X_test, self.y_train, self.y_test)
    
    def trainModel(self):
        '''
        This method triggers splitting dataset and then find a best RandomForest model via grid search 
        using the training features and labels.
        '''
        X_train, X_test, y_train, y_test = self.__splitData()
        self.gridSearch = GridSearch()
        self.rfc = self.gridSearch.fit(X_train, y_train)
        return self.rfc
    
    def predictClasses(self):
        '''
        This method predicts classes (YES or NO) using a trained model.
        '''
        if (self.rfc is None):
            print("No trained model available, please train a model first!")
            return None
        
        self.y_pred = self.rfc.predict(self.X_test)
        return self.y_pred
    
    def getModelMetrics(self):
        '''
        This method obtains the class prediction scores: (Accuracy Score, R2, F1).
        '''
        if (self.y_test is None or self.y_pred is None):
            print('Failed to get model performance metrics because y_test is null or y_pred is null!')
            return None
        
        self.accuracy_score = accuracy_score(self.y_test, self.y_pred)
        self.f1_score = f1_score(self.y_test, self.y_pred)
        
        pred = self.predictAttendanceProbability(self.X_test)[:, 1]
        actual = self.y_test.astype(float)
        
        self.rmse_score = np.sqrt(mean_squared_error(actual, pred))
        self.mae_score = mean_absolute_error(actual, pred)
        self.r2_score = r2_score(actual, pred)
        
        return (self.accuracy_score, self.f1_score, self.rmse_score, self.mae_score, self.r2_score)
    
    def predictNullAttendanceProbability(self):
        '''
        This method uses a trained model to predict the attendance probability for 
        the candidates where the "Observed Attendance" column is null.
        '''
        y_pred = self.rfc.predict_proba(self.X_test_encoded.to_numpy())
        return y_pred
    
    def predictNullAttendanceClasses(self):
        '''
        This method predicts classes (YES or NO) using a trained model for unlabeled data records.
        '''
        y_pred = self.rfc.predict(self.X_test_encoded.to_numpy())
        return y_pred
    
    def predictAttendanceProbability(self, X):
        '''
        Given one preprocessed (including one-hot encoding) data smaple X,
        this method returns the probability of attendance probability.
        '''
        y_pred = self.rfc.predict_proba(X)
        return y_pred
    
    def predictAttendanceClass(self, X):
        '''
        Given one preprocessed (including one-hot encoding) data smaple X,
        this method returns the attendance Yes/No.
        '''
        y_pred = self.rfc.predict(X)
        return y_pred
    
    def mlFlow(self):
        '''
        Training model in mlflow
        * https://www.mlflow.org/docs/latest/tutorial.html
        '''
        np.random.seed(40)
        with mlflow.start_run():
            self.loadData()
            self.PreprocessData()
            self.trainModel()
            self.predictClasses()
            accuracy_score, f1_score, rmse_score, mae_score, r2_score = self.getModelMetrics()

            print("Random Forest model:")
            print("  RMSE: {}".format(rmse_score))
            print("  MAE: {}".format(mae_score))
            print("  R2: {}".format(r2_score))
            print("Accuracy Score: {}".format(accuracy_score))
            print("  f1: {}".format(f1_score))
            
            best_params = self.gridSearch.gridSearchCV.best_params_ 

            mlflow.log_param("n_estimators", best_params["n_estimators"])
            mlflow.log_param("max_depth", best_params["max_depth"])
            mlflow.log_metric("rmse", rmse_score)
            mlflow.log_metric("r2", r2_score)
            mlflow.log_metric("mae", mae_score)
            mlflow.log_metric("accuracy", accuracy_score)
            mlflow.log_metric("f1", f1_score)

            mlflow.sklearn.log_model(self.rfc, "random_forest_model")


# Task 1 
# 
# (a) Create a model predicting if a candidate will attend an interview. This will be indicated by the "Observed Attendance" column in the data set. Create the model only using the records where this column is not null

# In[11]:


predictInterview = PredictInterview(use_koalas=True)
predictInterview.mlFlow()


# ## 5. Evaluation
# 
# Once a machine learning model is trained with expected performance, the next step is to assess the prediction results of the model in a controlled close-to-real settings to gain confidence that the model is valid, reliable, and meets business requirements before deployment.
# 
# As an example, for the Kaggle interview attendance project, one possible method of evaluation is to use mlflow to deploy the model as a Web service locally and then develop a client program to call the model Web service to get the prediction results of a testing dataset processed by data preparation. These prediction results can then be used to generate a table or csv file for recruitment industry domain experts to review.
# 
# The code below obtains a probability and a prediction for each of the candidates where the "Observed Attendance" column is null.

# In[12]:


pred_probs   = predictInterview.predictNullAttendanceProbability()
pred_classes = predictInterview.predictNullAttendanceClasses()

x = predictInterview.X_test_name_ids.to_numpy() 
z = zip(x, pred_probs, pred_classes)
answers = ('no', 'yes')

result = [[x1, p1[1], answers[c]] for x1, p1, c in z]
result_df = pd.DataFrame(np.array(result), columns=['Names/ID', 'Probability', 'Yes/No'])
result_df.to_csv('./data/interview_prediction_results.csv')
result_df.head(15)


# In[13]:


# start mlflow UI
# ! mlflow ui


# In[14]:


columns = predictInterview.X_train_encoded.columns
data1 = predictInterview.X_test[1]
test_df1 = pd.DataFrame(data1.reshape((1,-1)))
test_df1.columns = columns
test_df = test_df1.loc[:2]
test_df.head()


# In[15]:


data_json_obj = test_df.to_json(orient='split')
# data_json_obj


# In[16]:


import requests
import json

headers = {'Content-Type': 'application/json',
           'Format': 'pandas-split'}
url = 'http://127.0.0.1:1234/invocations'


# In[17]:


headers_json_str = json.dumps(headers)
headers_json_obj = json.loads(headers_json_str)


# In[19]:


response = requests.post(url, data=data_json_obj, headers = headers_json_obj)
response.text


# ## 6. Deployment
# 
# Once the model evaluation includes that the model is ready for deployment, the final step is to deploy an evaluated model into a production system. As described in [Data Science for Business](http://data-science-for-biz.com/), the specifics of deployment depend on the target production system. 
# 
# Taking the Kaggle interview attendance project as an example, one possible scenario is to deploy the model as a Web service on a server, which can be called by other components in a target production system to get prediction results. In a more complicated scenario that the development of the target production system is based on a programming language that is different from the modeling lanuage (e.g., Python), then the chance is that the model needs to be reimplemented in the target programming language as a component of the production system.  
# 
# As described before, mlflow has built-in capability of starting a logged model as a Web service:
# 
# mlflow models serve -m /Users/yuhuang/yuefeng/machine-learning-spark/mlruns/0/258301f3ac5f42fb99e885968ff17c2a/artifacts/random_forest_model -p 1234

# ## Summary
# 
# In this article, I use a close-to-real challenging dataset, the [Interview Attendance Problem for Kaggle competition](https://www.kaggle.com/vishnusraghavan/the-interview-attendance-problem), to demonstrate an end-to-end process of developing a machine learning pipeline for both Pandas and Koalas dataframes by combining Pandas and Koalas with Scikit-Learn and mlflow. This end-to-end development process follows the [Cross-industry standard process for data mining](https://en.wikipedia.org/wiki/Cross-industry_standard_process_for_data_mining). A brief description for each of the major phases of the standard process is provided. 
