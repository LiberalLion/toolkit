#Albert Sanchez Lafuente 2/4/2019, Pineda de Mar, Spain
#https://github.com/albertsl/
#Structure of the template mostly based on the Appendix B of the book Hands-on Machine Learning with Scikit-Learn and TensorFlow by Aurelien Geron (https://amzn.to/2WIfsmk)
#Big thank you to Uxue Lazcano (https://github.com/uxuelazkano) for code on model comparison
#Load packages
from catboost import CatBoostRegressor
from catboost import CatBoostClassifier
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
sns.set()
import numba

#Check versions
import platform
print("Operating system:", platform.system(), platform.release())
import sys
print("Python version:", sys.version)
print("Numpy version:", np.version.version)
print("Pandas version:", pd.__version__)
print("Seaborn version:", sns.__version__)
print("Numba version:", numba.__version__)

#Load data
df = pd.read_csv('file.csv')
#If data is too big, take a sample of it
df = pd.read_csv('file.csv', nrows=50000)
#Load mat file
from scipy.io import loadmat
data = loadmat('file.mat')
#Reduce dataframe memory usage
def reduce_mem_usage(df):
	""" iterate through all the columns of a dataframe and modify the data type
		to reduce memory usage.        
	"""
	start_mem = df.memory_usage().sum() / 1024**2
	print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))
	
	for col in df.columns:
		col_type = df[col].dtype
		
		if col_type != object:
			c_min = df[col].min()
			c_max = df[col].max()
			if str(col_type)[:3] == 'int':
				if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
					df[col] = df[col].astype(np.int8)
				elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
					df[col] = df[col].astype(np.int16)
				elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
					df[col] = df[col].astype(np.int32)
				elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
					df[col] = df[col].astype(np.int64)  
			else:
				if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
					df[col] = df[col].astype(np.float16)
				elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
					df[col] = df[col].astype(np.float32)
				else:
					df[col] = df[col].astype(np.float64)
		else:
			df[col] = df[col].astype('category')

	end_mem = df.memory_usage().sum() / 1024**2
	print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
	print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
	
	return df
#Sometimes it changes some values in the dataframe, let's check it doesnt' change anything
df_test = pd.DataFrame()
df_opt = reduce_mem_usage(df)
for col in df:
    df_test[col] = df[col] - df_opt[col]
#Mean, max and min for all columns should be 0
df_test.describe().loc['mean']
df_test.describe().loc['max']
df_test.describe().loc['min']

#Improve execution speed of your code by adding these decorators:
@numba.jit
def f(x):
	return x
@numba.njit #The nopython=True option requires that the function be fully compiled (so that the Python interpreter calls are completely removed), otherwise an exception is raised.  These exceptions usually indicate places in the function that need to be modified in order to achieve better-than-Python performance.  We strongly recommend always using nopython=True.
def f(x):
	return x

#Styling pandas DataFrame visualization https://pbpython.com/styling-pandas.html
#https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html
# more info on string formatting: https://mkaz.blog/code/python-string-format-cookbook/
format_dict = {'price': '${0:,.2f}', 'date': '{:%m-%Y}', 'pct_of_total': '{:.2%}'}
#Format the numbers
df.head().style.format(format_dict).hide_index()
#Highlight max and min
df.head().style.format(format_dict).hide_index().highlight_max(color='lightgreen').highlight_min(color='#cd4f39')
#Colour gradient in the background
df.head().style.format(format_dict).background_gradient(subset=['sum'], cmap='BuGn'))
#Bars indicating number size
df.head().style.format(format_dict).hide_index().bar(color='#FFA07A', vmin=100_000, subset=['sum'], align='zero').bar(color='lightgreen', vmin=0, subset=['pct_of_total'], align='zero').set_caption('2018 Sales Performance'))

#Visualize data
df.head()
df.describe()
df.info()
df.columns
#For a categorical dataset we want to see how many instances of each category there are
df['categorical_var'].value_counts()
#Automated data visualization
from pandas_profiling import ProfileReport
prof = ProfileReport(df)
prof.to_file(outputfile='output.html')

#Check for missing data
total_null = df.isna().sum().sort_values(ascending=False)
percent = 100*(df.isna().sum()/df.isna().count()).sort_values(ascending=False)
missing_data = pd.concat([total_null, percent], axis=1, keys=['Total', 'Percent'])
#Generate new features with missing data
nanf = ['1']
for feature in nanf:
    df[feature + '_nan'] = df[nanf].isna()
#Also look for infinite data, recommended to check it also after feature engineering
df.replace(np.inf,0,inplace=True)
df.replace(-np.inf,0,inplace=True)

#Check for duplicated data
df.duplicated().value_counts()
df['duplicated'] = df.duplicated() #Create a new feature

#Fill missing data or drop columns/rows
df.fillna()
df.drop('column_full_of_nans')
df.dropna(how='any', inplace=True)

#Fix Skewed features
numeric_feats = all_data.dtypes[all_data.dtypes != "object"].index
# Check the skew of all numerical features
skewed_feats = all_data[numeric_feats].apply(lambda x: skew(x.dropna())).sort_values(ascending=False)
skewness = pd.DataFrame({'Skew' :skewed_feats})
#Box Cox Transformation of (highly) skewed features. We use the scipy function boxcox1p which computes the Box-Cox transformation of 1+x
#Note that setting λ=0 is equivalent to log1p used above for the target variable.
from scipy.special import boxcox1p
skewed_features = skewness.index
lambd = 0.15
for feat in skewed_features:
    all_data[feat] = boxcox1p(all_data[feat], lambd)

#Exploratory Data Analysis (EDA)
sns.pairplot(df)
sns.distplot(df['column'])
sns.countplot(df['column'])

#Feature understanding - see how the variable affects the target variable
from featexp import get_univariate_plots
# Plots drawn for all features if nothing is passed in feature_list parameter.
get_univariate_plots(data=data_train, target_col='target', features_list=['DAYS_BIRTH'], bins=10)
get_univariate_plots(data=data_train, target_col='target', data_test=data_test, features_list=['DAYS_EMPLOYED'])
from featexp import get_trend_stats
stats = get_trend_stats(data=data_train, target_col='target', data_test=data_test)

#Unsupervised Feature selection before training a model
from sklearn.feature_selection import SelectKBest
bestfeatures = SelectKBest(score_func=chi2, k='all')
fit = bestfeatures.fit(X,Y)

dfscores = pd.DataFrame(fit.scores_)
dfcolumns = pd.DataFrame(df.columns)

featureScores = pd.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns

print(featureScores.nlargest(5,'Score'))

#Fix or remove outliers
sns.boxplot(df['feature1'])
sns.boxplot(df['feature2'])
plt.scatter('var1', 'y') #Do this for all variables against y

def replace_outlier(df, column, value, threshold, direction='max'): #value could be the mean
        if direction == 'max':
            df[column] = df[column].apply(lambda x: value if x > threshold else x)
            for item in df[df[column] > threshold].index:
                df.loc[item, (column+'_nan')] = 1
        elif direction == 'min':
            df[column] = df[column].apply(lambda x: value if x < threshold else x)
            for item in df[df[column] < threshold].index:
                df.loc[item, (column+'_nan')] = 1

#Outlier detection with Isolation Forest
from sklearn.ensemble import IsolationForest
anomalies_ratio = 0.009
isolation_forest = IsolationForest(n_estimators=100, max_samples=256, contamination=anomalies_ratio, behaviour='new', random_state=101)
isolation_forest.fit(df)
outliers = isolation_forest.predict(df)
outliers = [1 if x == -1 else 0 for x in outliers]
df['Outlier'] = outliers

#Outlier detection with Mahalanobis Distance
def is_pos_def(A):
	if np.allclose(A, A.T):
		try:
			np.linalg.cholesky(A)
			return True
		except np.linalg.LinAlgError:
			return False
	else:
		return False

def cov_matrix(data):
	covariance_matrix = np.cov(data, rowvar=False)
	if is_pos_def(covariance_matrix):
		inv_covariance_matrix = np.linalg.inv(covariance_matrix)
		if is_pos_def(inv_covariance_matrix):
			return covariance_matrix, inv_covariance_matrix
		else:
			print('Error: Inverse Covariance Matrix is not positive definite')
	else:
		print('Error: Covariance Matrix is not positive definite')

def mahalanobis_distance(inv_covariance_matrix, data):
		normalized = data - data.mean(axis=0)
		md = []
		for i in range(len(normalized)):
			md.append(np.sqrt(normalized[i].dot(inv_covariance_matrix).dot(normalized[i])))
		return md

#Mahalanobis Distance should follow X2 distribution, let's visualize it:
sns.distplot(np.square(dist), bins=10, kde=False)

def mahalanobis_distance_threshold(dist, k=2): #k=3 for a higher threshold
	return np.mean(dist)*k

#Visualize the Mahalanobis distance to check if the threshold is reasonable
sns.distplot(dist, bins=10, kde=True)

def mahalanobis_distance_detect_outliers(dist, k=2):
	threshold = mahalanobis_distance_threshold(dist, k)
	outliers = []
	for i in range(len(dist)):
		if dist[i] >= threshold:
			outliers.append(i) #index of the outlier
	return np.array(outliers)

md = mahalanobis_distance_detect_outliers(mahalanobis_distance(cov_matrix(df)[1], df), k=2)
#Flag outliers with Mahalanobis Distance
threshold = mahalanobis_distance_threshold(mahalanobis_distance(cov_matrix(df)[1], df), k=2)
outlier = pd.DataFrame({'Mahalanobis distance': md, 'Threshold':threshold})
outlier['Outlier'] = outlier[outlier['Mahalanobis distance'] > outlier['Threshold']]
df['Outlier'] = outlier['Outlier']

#Correlation analysis
sns.heatmap(df.corr(), annot=True, fmt='.2f')
correlations = df.corr(method='pearson').abs().unstack().sort_values(kind="quicksort").reset_index()
correlations = correlations[correlations['level_0'] != correlations['level_1']]

#Colinearity
from statsmodels.stats.outliers_influence import variance_inflation_factor    
def calculate_vif_(X, thresh=5.0):
    variables = list(range(X.shape[1]))
    dropped = True
    while dropped:
        dropped = False
        vif = [variance_inflation_factor(X.iloc[:, variables].values, ix)
               for ix in range(X.iloc[:, variables].shape[1])]

        maxloc = vif.index(max(vif))
        if max(vif) > thresh:
            print('vif ' + vif + ' dropping \'' + X.iloc[:, variables].columns[maxloc] +
                  '\' at index: ' + str(maxloc))
            del variables[maxloc]
            dropped = True

    print('Remaining variables:')
    print(X.columns[variables])
    return X.iloc[:, variables]

#Encode categorical variables
#Encoding for target variable (categorical variable)
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['categorical_var'] = le.fit_transform(df['categorical_var'])

#One hot encoding for categorical information
#Use sklearn's OneHotEncoder for categories encoded as possitive real numbers
from sklearn.preprocessing import OneHotEncoder
enc = OneHotEncoder()
df['var_to_encode'] = enc.fit_transform(df['var_to_encode'])
#Use pandas get_dummies for categories encoded as strings
pd.get_dummies(df, columns=['col1','col2'])

#OrdinalEncoding for categories which have an order (example: low/medium/high)
map_dict = {'low': 0, 'medium': 1, 'high': 2}
df['var_oe'] = df['var'].apply(lambda x: map_dict[x])
#We can also do it with sklearn's LabelEncoder
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['var_oe'] = le.fit_transform(df['var'])

#BinaryEncoder when we have many categories in one variable it means creating many columns with OHE. With Binary encoding we can do so with many less columns by using binary numbers. Use only when there is a high cardinality in the categorical variable.
from category_encoders.binary import BinaryEncoder
be = BinaryEncoder(cols = ['var'])
df = be.fit_transform(df)

#HashingEncoder
from category_encoders.hashing import HashingEncoder
he = HashingEncoder(cols = ['var'])
df = he.fit_transform(df)

#Feature selection: Drop attributes that provide no useful information for the task

#Feature engineering. Create new features by transforming the data
#Discretize continuous features
#Decompose features (categorical, date/time, etc.)
#Add promising transformations of features (e.g., log(x), sqrt(x), x^2, etc.)
#Aggregate features into promising new features (x*y)
#For speed/movement data, add vectorial features. Try many different combinations
df['position_norm'] = df['position_X'] ** 2 + df['position_Y'] ** 2 + df['position_Z'] ** 2
df['position_module'] = df['position_norm'] ** 0.5
df['position_norm_X'] = df['position_X'] / df['position_module']
df['position_norm_Y'] = df['position_Y'] / df['position_module']
df['position_norm_Z'] = df['position_Z'] / df['position_module']
df['position_over_velocity'] = df['position_module'] / df['velocity_module']
#For time series data: Discretize the data by different samples.
from astropy.stats import median_absolute_deviation
from statsmodels.robust.scale import mad
from scipy.stats import kurtosis
from scipy.stats import skew

def CPT5(x):
	den = len(x)*np.exp(np.std(x))
	return sum(np.exp(x))/den

def SSC(x):
	x = np.array(x)
	x = np.append(x[-1], x)
	x = np.append(x, x[1])
	xn = x[1:len(x)-1]
	xn_i2 = x[2:len(x)]    #xn+1
	xn_i1 = x[0:len(x)-2]  #xn-1
	ans = np.heaviside((xn-xn_i1)*(xn-xn_i2), 0)
	return sum(ans[1:])

def wave_length(x):
	x = np.array(x)
	x = np.append(x[-1], x)
	x = np.append(x, x[1])
	xn = x[1:len(x)-1]
	xn_i2 = x[2:len(x)]    #xn+1
	return sum(abs(xn_i2-xn))

def norm_entropy(x):
	tresh = 3
	return sum(np.power(abs(x), tresh))

def SRAV(x):
	SRA = sum(np.sqrt(abs(x)))
	return np.power(SRA/len(x), 2)

def mean_abs(x):
	return sum(abs(x))/len(x)

def zero_crossing(x):
	x = np.array(x)
	x = np.append(x[-1], x)
	x = np.append(x, x[1])
	xn = x[1:len(x)-1]
	xn_i2 = x[2:len(x)]    #xn+1
	return sum(np.heaviside(-xn*xn_i2, 0))

df_tmp = pd.DataFrame()
for column in tqdm(df.columns):
	df_tmp[column + '_mean'] = df.groupby(['series_id'])[column].mean()
	df_tmp[column + '_median'] = df.groupby(['series_id'])[column].median()
	df_tmp[column + '_max'] = df.groupby(['series_id'])[column].max()
	df_tmp[column + '_min'] = df.groupby(['series_id'])[column].min()
	df_tmp[column + '_std'] = df.groupby(['series_id'])[column].std()
	df_tmp[column + '_range'] = df_tmp[column + '_max'] - df_tmp[column + '_min']
	df_tmp[column + '_max_over_Min'] = df_tmp[column + '_max'] / df_tmp[column + '_min']
	df_tmp[column + 'median_abs_dev'] = df.groupby(['series_id'])[column].mad()
	df_tmp[column + '_mean_abs_chg'] = df.groupby(['series_id'])[column].apply(lambda x: np.mean(np.abs(np.diff(x))))
	df_tmp[column + '_mean_change_of_abs_change'] = df.groupby('series_id')[column].apply(lambda x: np.mean(np.diff(np.abs(np.diff(x)))))
	df_tmp[column + '_abs_max'] = df.groupby(['series_id'])[column].apply(lambda x: np.max(np.abs(x)))
	df_tmp[column + '_abs_min'] = df.groupby(['series_id'])[column].apply(lambda x: np.min(np.abs(x)))
	df_tmp[column + '_abs_avg'] = (df_tmp[column + '_abs_min'] + df_tmp[column + '_abs_max'])/2
	df_tmp[column + '_abs_mean'] = df.groupby('series_id')[column].apply(lambda x: np.mean(np.abs(x)))
	df_tmp[column + '_abs_std'] = df.groupby('series_id')[column].apply(lambda x: np.std(np.abs(x)))
	df_tmp[column + '_abs_range'] = df_tmp[column + '_abs_max'] - df_tmp[column + '_abs_min']
	df_tmp[column + '_skew'] = df.groupby(['series_id'])[column].skew()
	df_tmp[column + '_q25'] = df.groupby(['series_id'])[column].quantile(0.25)
	df_tmp[column + '_q75'] = df.groupby(['series_id'])[column].quantile(0.75)
	df_tmp[column + '_q95'] = df.groupby(['series_id'])[column].quantile(0.95)
	df_tmp[column + '_iqr'] = df_tmp[column + '_q75'] - df_tmp[column + '_q25']
	df_tmp[column + '_CPT5'] = df.groupby(['series_id'])[column].apply(CPT5)
	df_tmp[column + '_SSC'] = df.groupby(['series_id'])[column].apply(SSC)
	df_tmp[column + '_wave_lenght'] = df.groupby(['series_id'])[column].apply(wave_length)
	df_tmp[column + '_norm_entropy'] = df.groupby(['series_id'])[column].apply(norm_entropy)
	df_tmp[column + '_SRAV'] = df.groupby(['series_id'])[column].apply(SRAV)
	df_tmp[column + '_kurtosis'] = df.groupby(['series_id'])[column].apply(kurtosis)
	df_tmp[column + '_zero_crossing'] = df.groupby(['series_id'])[column].apply(zero_crossing)
	df_tmp[column +  '_unq'] = df[column].round(3).nunique()
	try:
		df_tmp[column + '_freq'] = df[column].value_counts().idxmax()
	except:
		df_tmp[column + '_freq'] = 0
	df_tmp[column + '_max_freq'] = df[df[column] == df[column].max()].shape[0]
	df_tmp[column + '_min_freq'] = df[df[column] == df[column].min()].shape[0]
	df_tmp[column + '_pos_freq'] = df[df[column] >= 0].shape[0]
	df_tmp[column + '_neg_freq'] = df[df[column] < 0].shape[0]
	df_tmp[column + '_nzeros'] = (df[column]==0).sum(axis=0)
df = df_tmp.copy()
#Create a new column from conditions on other columns
df['column_y'] = df[(df['column_x1'] | 'column_x2') & 'column_x3']
df['column_y'] = df['column_y'].apply(bool)
df['column_y'] = df['column_y'].apply(int)
#Create a new True/False column according to the first letter on another column.
lEI = [0] * df.shape[0]

for i, row in df.iterrows():
	try:
		l = df['room_list'].iloc[i].split(', ')
	except:
		#When the given row is empty
		l = []
	for element in l:
		if element[0] == 'E' or element[0] == 'I':
			lEI[i] = 1

df['EI'] = pd.Series(lEI)

#Scaling features
#Standard Scaler: The StandardScaler assumes your data is normally distributed within each feature and will scale them such that the distribution is now centred around 0, with a standard deviation of 1.
#If data is not normally distributed, this is not the best scaler to use.
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(df)
df_norm = pd.DataFrame(scaler.transform(df), columns=df.columns)
#MinMax Scaler: Shrinks the range such that the range is now between 0 and 1 (or -1 to 1 if there are negative values).
#This scaler works better for cases in which the standard scaler might not work so well. If the distribution is not Gaussian or the standard deviation is very small, the min-max scaler works better.
#it is sensitive to outliers, so if there are outliers in the data, you might want to consider the Robust Scaler below.
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler.fit(df)
df_norm = pd.DataFrame(scaler.transform(df), columns=df.columns)
#Robust Scaler: Uses a similar method to the Min-Max scaler but it instead uses the interquartile range, rather than the min-max, so that it is robust to outliers.
#This means it is using less data for scaling so it’s more suitable when there are outliers in the data.RobustScaler
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
scaler.fit(df)
df_norm = pd.DataFrame(scaler.transform(df), columns=df.columns)
#Normalizer: The normalizer scales each value by dividing it by its magnitude in n-dimensional space for n number of features.
from sklearn.preprocessing import Normalizer
scaler = RobustScaler()
scaler.fit(df)
df_norm = pd.DataFrame(scaler.transform(df), columns=df.columns)

#Apply all the same transformations to the test set

#Define Validation method
#Train and validation set split
from sklearn.model_selection import train_test_split
X = df.drop('target_var', axis=1)
y = df['column to predict']
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size = 0.4, stratify = y.values, random_state = 101)
#Cross validation
from sklearn.model_selection import cross_val_score
cross_val_score(model, X, y, cv=5)
#StratifiedKFold
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, random_state=101)
for train_index, val_index in skf.split(X, y):
	X_train, X_val = X[train_index], X[val_index]
	y_train, y_val = y[train_index], y[val_index]


#Train many quick and dirty models from different categories(e.g., linear, naive Bayes, SVM, Random Forests, neural net, etc.) using standard parameters.
#########
# Linear Regression
#########
from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit(X_train,y_train)

#Linear model interpretation
lr.intercept_
lr.coef_

#Use model to predict
y_pred = lr.predict(X_val)

#Evaluate accuracy of the model
plt.scatter(y_val, y_pred) #should have the shape of a line for good predictions
sns.distplot(y_val - y_pred) #should be a normal distribution centered at 0
acc_lr = round(lr.score(X_val, y_val) * 100, 2)

#########
# Logistic Regression
#########
from sklearn.linear_model import LogisticRegression
logmodel = LogisticRegression()
logmodel.fit(X_train,y_train)

#Use model to predict
y_pred = logmodel.predict(X_val)

#Evaluate accuracy of the model
acc_log = round(logmodel.score(X_val, y_val) * 100, 2)

#########
# KNN
#########
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors = 5)
knn.fit(X_train, y_train)

#Use model to predict
y_pred = knn.predict(X_val)

#Evaluate accuracy of the model
acc_knn = round(knn.score(X_val, y_val) * 100, 2)

#########
# Decision Tree
#########
from sklearn.tree import DecisionTreeClassifier
dtree = DecisionTreeClassifier()
dtree.fit(X_train, y_train)

#Use model to predict
y_pred = dtree.predict(X_val)

#Evaluate accuracy of the model
acc_dtree = round(dtree.score(X_val, y_val) * 100, 2)

#########
# Random Forest
#########
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(n_estimators=200, random_state=101, n_jobs=-1, verbose=3)
rfc.fit(X_train, y_train)

from sklearn.ensemble import RandomForestRegressor
rfr = RandomForestRegressor(n_estimators=200, random_state=101, n_jobs=-1, verbose=3)
rfr.fit(X_train, y_train)

#Use model to predict
y_pred = rfr.predict(X_val)

#Evaluate accuracy of the model
acc_rf = round(rfr.score(X_val, y_val) * 100, 2)

#Evaluate feature importance
importances = rfr.feature_importances_
std = np.std([importances for tree in rfr.estimators_], axis=0)
indices = np.argsort(importances)[::-1]

feature_importances = pd.DataFrame(rfr.feature_importances_, index = X_train.columns, columns=['importance']).sort_values('importance', ascending=False)
feature_importances.sort_values('importance', ascending=False)

plt.figure()
plt.title("Feature importances")
plt.bar(range(X_train.shape[1]), importances[indices], yerr=std[indices], align="center")
plt.xticks(range(X_train.shape[1]), indices)
plt.xlim([-1, X_train.shape[1]])
plt.show()

#########
# lightGBM (LGBM)
#########
import lightgbm as lgb
#create dataset for lightgbm
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_val, y_val, reference=lgb_train)

#specify your configurations as a dict
params = {
	'boosting_type': 'gbdt',
	'objective': 'regression',
	'metric': {'l2', 'l1'},
	'num_leaves': 31,
	'learning_rate': 0.05,
	'feature_fraction': 0.9,
	'bagging_fraction': 0.8,
	'bagging_freq': 5,
	'verbose': 0
}

#train
gbm = lgb.train(params, lgb_train, num_boost_round=20, valid_sets=lgb_eval, early_stopping_rounds=5)

#save model to file
gbm.save_model('model.txt')

#predict
y_pred = gbm.predict(X_val, num_iteration=gbm.best_iteration)

#########
# XGBoost
#########
import xgboost as xgb

params = {'objective': 'multi:softmax',  #Specify multiclass classification
		'num_class': 9,  #Number of possible output classes
		'tree_method': 'hist',  #Use gpu_hist for GPU accelerated algorithm.
		'eta': 0.1,
		'max_depth': 6,
		'silent': 1,
		'gamma': 0,
		'eval_metric': "merror",
		'min_child_weight': 3,
		'max_delta_step': 1,
		'subsample': 0.9,
		'colsample_bytree': 0.4,
		'colsample_bylevel': 0.6,
		'colsample_bynode': 0.5,
		'lambda': 0,
		'alpha': 0,
		'seed': 0}

xgtrain = xgb.DMatrix(X_train, label=y_train)
xgval = xgb.DMatrix(X_val, label=y_val)
xgtest = xgb.DMatrix(X_test)

num_rounds = 500
gpu_res = {}  #Store accuracy result
#Train model
xgbst = xgb.train(params, xgtrain, num_rounds, evals=[
			(xgval, 'test')], evals_result=gpu_res)

y_pred = xgbst.predict(xgtest)

#Simplified code
model = xgb.XGBClassifier(random_state=1,learning_rate=0.01)
model.fit(x_train, y_train)
model.score(x_test,y_test)
#Regression
model=xgb.XGBRegressor()
model.fit(x_train, y_train)
model.score(x_test,y_test)

#########
# AdaBoost
#########
from sklearn.ensemble import AdaBoostClassifier
model = AdaBoostClassifier(random_state=101)
model.fit(X_train, y_train)
model.score(X_val,y_val)
#Regression
from sklearn.ensemble import AdaBoostRegressor
model = AdaBoostRegressor(random_state=101)
model.fit(X_train, y_train)
model.score(X_val, y_val)

#########
# CatBoost
#########
#CatBoost algorithm works great for data with lots of categorical variables. You should not perform one-hot encoding for categorical variables before applying this model.
model = CatBoostClassifier()
categorical_features_indices = np.where(df.dtypes != np.float)[0]
model.fit(X_train, y_train, cat_features=categorical_features_indices, eval_set=(X_val, y_val))
model.score(X_val, y_val)
#Regression
model = CatBoostRegressor()
categorical_features_indices = np.where(df.dtypes != np.float)[0]
model.fit(x_train, y_train,cat_features=categorical_features_indices,eval_set=(X_val, y_val))
model.score(X_val, y_val)


#########
# Support Vector Machine (SVM)
#########
from sklearn.svm import SVC
model = SVC()
model.fit(X_train, y_train)

#Use model to predict
y_pred = model.predict(X_val)

#Evaluate accuracy of the model
acc_svm = round(model.score(X_val, y_val) * 100, 2)

#########
# K-Means Clustering
#########
#Find parameter k: Elbow method
SSE = []
for k in range(1,10):
	kmeans = KMeans(n_clusters=k)
	kmeans.fit(df)
	SSE.append(kmeans.inertia_)

plt.plot(list(range(1,10)), SSE)

#Train model
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=K) #Choose K
kmeans.fit(df)

#Evaluate the model
kmeans.cluster_centers_
kmeans.labels_

#Measure and compare their performance
models = pd.DataFrame({
'Model': ['Linear Regression', 'Support Vector Machine', 'KNN', 'Logistic Regression', 
			'Random Forest'],
'Score': [acc_lr, acc_svm, acc_knn, acc_log, 
			acc_rf]})
models.sort_values(by='Score', ascending=False)

#Evaluate how each model is working
plt.scatter(y_val, y_pred) #should have the shape of a line for good predictions
sns.distplot(y_val - y_pred) #should be a normal distribution centered at 0

#Analyze the most significant variables for each algorithm.
#Analyze the types of errors the models make.
#What data would a human have used to avoid these errors?
#Have a quick round of feature selection and engineering.
#Have one or two more quick iterations of the five previous steps.
#Short-list the top three to five most promising models, preferring models that make different types of errors.
#Define Performance Metrics
#ROC AUC for classification tasks
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
roc_auc = roc_auc_score(y_val, model.predict(X_val))
fpr, tpr, thresholds = roc_curve(y_val, model.predict_proba(X_val)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Model (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.show()
#Confusion Matrix
from sklearn.metrics import confusion_matrix
confusion_matrix(y_val, y_pred)
#MAE, MSE, RMSE
from sklearn import metrics
metrics.mean_absolute_error(y_val, y_pred)
metrics.mean_squared_error(y_val, y_pred)
np.sqrt(metrics.mean_squared_error(y_val, y_pred))
#Classification report
from sklearn.metrics import classification_report
print(classification_report(y_val,y_pred))

#Fine-tune the hyperparameters using cross-validation
#Treat your data transformation choices as hyperparameters, especially when you are not sure about them (e.g., should I replace missing values with zero or with the median value? Or just drop the rows?)
#Unless there are very few hyperparameter values to explore, prefer random search over grid search. If training is very long, you may prefer a Bayesian optimization approach
from sklearn.model_selection import GridSearchCV
param_grid = {'C':[0.1,1,10,100,1000], 'gamma':[1,0.1,0.01,0.001,0.0001]}
grid = GridSearchCV(model, param_grid, verbose = 3)
grid.fit(X_train, y_train)
grid.best_params_
grid.best_estimator_

#Try Ensemble methods. Combining your best models will often perform better than running them individually
#Max Voting
model1 = tree.DecisionTreeClassifier()
model2 = KNeighborsClassifier()
model3 = LogisticRegression()

model1.fit(x_train, y_train)
model2.fit(x_train, y_train)
model3.fit(x_train, y_train)

pred1=model1.predict(X_test)
pred2=model2.predict(X_test)
pred3=model3.predict(X_test)

final_pred = np.array([])
for i in range(len(X_test)):
    final_pred = np.append(final_pred, mode([pred1[i], pred2[i], pred3[i]]))

#We can also use VotingClassifier from sklearn
from sklearn.ensemble import VotingClassifier
model1 = LogisticRegression(random_state=1)
model2 = tree.DecisionTreeClassifier(random_state=1)
model = VotingClassifier(estimators=[('lr', model1), ('dt', model2)], voting='hard')
model.fit(x_train,y_train)
model.score(x_test,y_test)

#Averaging
finalpred=(pred1+pred2+pred3)/3

#Weighted Average
finalpred=(pred1*0.3+pred2*0.3+pred3*0.4)

#Stacking
from sklearn.model_selection import StratifiedKFold
def Stacking(model, train, y, test, n_fold):
   folds = StratifiedKFold(n_splits=n_fold, random_state=101)
   test_pred = np.empty((test.shape[0], 1), float)
   train_pred = np.empty((0, 1), float)
   for train_indices, val_indices in folds.split(train,y.values):
      X_train, X_val = train.iloc[train_indices], train.iloc[val_indices]
      y_train, y_val = y.iloc[train_indices], y.iloc[val_indices]

      model.fit(X_train, y_train)
      train_pred = np.append(train_pred, model.predict(X_val))
      test_pred = np.append(test_pred, model.predict(test))
    return test_pred.reshape(-1,1), train_pred

model1 = DecisionTreeClassifier(random_state=101)
test_pred1, train_pred1 = Stacking(model1, X_train, y_train, X_test, 10)
train_pred1 = pd.DataFrame(train_pred1)
test_pred1 = pd.DataFrame(test_pred1)

model2 = KNeighborsClassifier()
test_pred2, train_pred2 = Stacking(model2, X_train, y_train, X_test, 10)
train_pred2 = pd.DataFrame(train_pred2)
test_pred2 = pd.DataFrame(test_pred2)

df = pd.concat([train_pred1, train_pred2], axis=1)
df_test = pd.concat([test_pred1, test_pred2], axis=1)

model = LogisticRegression(random_state=101)
model.fit(df,y_train)
model.score(df_test, y_test)

#Blending
model1 = DecisionTreeClassifier()
model1.fit(X_train, y_train)
val_pred1 = pd.DataFrame(model1.predict(X_val))
test_pred1 = pd.DataFrame(model1.predict(X_test))

model2 = KNeighborsClassifier()
model2.fit(X_train,y_train)
val_pred2 = pd.DataFrame(model2.predict(X_val))
test_pred2 = pd.DataFrame(model2.predict(X_test))

df_val = pd.concat([X_val, val_pred1,val_pred2],axis=1)
df_test = pd.concat([X_test, test_pred1,test_pred2],axis=1)
model = LogisticRegression()
model.fit(df_val,y_val)
model.score(df_test,y_test)

#Bagging
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
ens = BaggingClassifier(DecisionTreeClassifier(random_state=101))
ens.fit(X_train, y_train)
ens.score(X_val,y_val)
#Regression
from sklearn.ensemble import BaggingRegressor
from sklearn.tree import DecisionTreeClassifier
ens = BaggingRegressor(DecisionTreeRegressor(random_state=101))
ens.fit(X_train, y_train)
ens.score(X_val,y_val)

#Once you are confident about your final model, measure its performance on the test set to estimate the generalization error

#Model interpretability
#Feature importance
import eli5
from eli5.sklearn import PermutationImportance

perm = PermutationImportance(model, random_state=101).fit(X_val, y_val)
eli5.show_weights(perm, feature_names = X_val.columns.tolist())

#Partial dependence plot
#New integration in sklearn, might not work with older versions
from sklearn.inspection import partial_dependence, plot_partial_dependence
partial_dependence(model, X_train, features=['feature', ('feat1', 'feat2')])
plot_partial_dependence(model, X_train, features=['feature', ('feat1', 'feat2')])
#With external module for legacy editions
from pdpbox import pdp, get_dataset, info_plots

#Create the data that we will plot
pdp_goals = pdp.pdp_isolate(model=model, dataset=X_val, model_features=X_val.columns, feature='Goals Scored')

#plot it
pdp.pdp_plot(pdp_goals, 'Goals Scored')
plt.show()

#Similar to previous PDP plot except we use pdp_interact instead of pdp_isolate and pdp_interact_plot instead of pdp_isolate_plot
features_to_plot = ['Goals Scored', 'Distance Covered (Kms)']
inter1  =  pdp.pdp_interact(model=model, dataset=X_val, model_features=X_val.columns, features=features_to_plot)

pdp.pdp_interact_plot(pdp_interact_out=inter1, feature_names=features_to_plot, plot_type='contour')
plt.show()

#SHAP Values: Understand how each feature affects every individual prediciton
import shap
data_for_prediction = X_val.iloc[row_num]
explainer = shap.TreeExplainer(model)  #Use DeepExplainer for Deep Learning models, KernelExplainer for all other models
shap_vals = explainer.shap_values(data_for_prediction)
shap.initjs()
shap.force_plot(explainer.expected_value[1], shap_vals[1], data_for_prediction)

#We can also do a SHAP plot of the whole dataset
shap_vals = explainer.shap_values(X_val)
shap.summary_plot(shap_vals[1], X_val)
#SHAP Dependence plot
shap.dependence_plot('feature_for_x', shap_vals[1], X_val, interaction_index="feature_for_color")

#Dimensionality reduction
#SVD: Find the percentage of variance explained by each principal component
#First scale the data
U, S, V = np.linalg.svd(df, full_matrices=False)
importance = S/S.sum()
varinace_explained = importance.cumsum()*100
#PCA: Decompose the data in a defined number of variables keeping the most variance possible.
from sklearn.decomposition import PCA
pca = PCA(n_components=2, svd_solver='full')
X_train_PCA = pca.fit_transform(X_train)
X_train_PCA = pd.DataFrame(X_train_PCA)
X_train_PCA.index = X_train.index

X_test_PCA = pca.transform(X_test)
X_test_PCA = pd.DataFrame(X_test_PCA)
X_test_PCA.index = X_test.index
