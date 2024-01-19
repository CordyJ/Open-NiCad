import numpy as np
import pandas as pd
import databricks.koalas as ks
import matplotlib.pyplot as plt
import matplotlib as mpl
from   datetime import datetime
import os
import subprocess
import requests
import json

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

ks_df = ks.read_csv('Interview_Attendance_Data.csv')

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
    
class PredictInterview(object):
    def __init__(self, use_koalas=True):
        '''
        This class is to predict the probability of a candidate attending scheduled interviews.
        '''
        self.use_koalas = use_koalas
        self.dataset_file_name = 'Interview_Attendance_Data.csv'
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
            
            
if __name__ == "__main__":
    predictInterview = PredictInterview()
    
    print('start mlflow ...')
    predictInterview.mlFlow()
    
    print('process null attendance ...')
    pred_probs   = predictInterview.predictNullAttendanceProbability()
    pred_classes = predictInterview.predictNullAttendanceClasses()

    x = predictInterview.X_test_name_ids.to_numpy() 
    z = zip(x, pred_probs, pred_classes)
    answers = ('no', 'yes')

    result = [[x1, p1[1], answers[c]] for x1, p1, c in z]
    result_df = pd.DataFrame(np.array(result), columns=['Names/ID', 'Probability', 'Yes/No'])
    
    print('output interview_prediction.csv ...')
    result_df.to_csv('interview_prediction.csv')
    
    #
    # start model Web service
    # Notes:
    # (1)  that the model unique universal ID b6e8b1936c44400bb973a13cc40a9b8f needs to be modified to match your case
    # (2) the model Web service must starts first before the following model Web service client code can run!
    #
    # print('start model Web service ...')
    # cmd = "mlflow models serve -m /Users/yuhuang/yuefeng/machine-learning-spark/mlruns/0/b6e8b1936c44400bb973a13cc40a9b8f/artifacts/random_forest_model -p 1234"
    # returned_value = os.system(cmd) 
    # print('model Web service started')
    
    #
    # call model Web service
    #
    headers = {'Content-Type': 'application/json',
           'Format': 'pandas-split'}
    headers_json_str = json.dumps(headers)
    headers_json_obj = json.loads(headers_json_str)
    
    url = 'http://127.0.0.1:1234/invocations'
    
    columns = predictInterview.X_train_encoded.columns
    data1 = predictInterview.X_test[1]
    test_df1 = pd.DataFrame(data1.reshape((1,-1)))
    test_df1.columns = columns
    test_df = test_df1.loc[:2]
    data_json_obj = test_df.to_json(orient='split')
    
    print('call model Web service ...')
    response = requests.post(url, data=data_json_obj, headers = headers_json_obj)
    print('intervice attendance: ', response.text)
    
    print('all done')
