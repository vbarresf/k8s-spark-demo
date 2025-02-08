import pyspark
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.types import *
from pyspark.sql import Row,SQLContext
from prophet import Prophet

from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt
from datetime import date
import pickle
import pathlib
import logging


conf = SparkConf()

spark = pyspark.sql.SparkSession.builder.appName('trainModelv3').config("spark.jars", "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar").getOrCreate()
sc = spark.sparkContext

spark = SQLContext(sc)

train_schema = StructType([
  StructField('date', DateType()),
  StructField('store', IntegerType()),
  StructField('item', IntegerType()),
  StructField('sales', IntegerType())
  ])

# read from GCS PATH
train = spark.read.csv(
  'gs://sdg-demo-train/dataset/train.csv', 
  header=True, 
  schema=train_schema
  )
  

train.createOrReplaceTempView('train')


sql_statement = '''
  SELECT
    CAST(date as date) as ds,
    sales as y
  FROM train
  WHERE store=1 AND item=1
  ORDER BY ds
  '''

history_pd = spark.sql(sql_statement).toPandas()

history_pd = history_pd.dropna()


logging.getLogger('py4j').setLevel(logging.ERROR)

model = Prophet(
  interval_width=0.95,
  growth='linear',
  daily_seasonality=False,
  weekly_seasonality=True,
  yearly_seasonality=True,
  seasonality_mode='multiplicative'
  )

model.fit(history_pd)

future_pd = model.make_future_dataframe(
  periods=90, 
  freq='d', 
  include_history=True
  )

forecast_pd = model.predict(future_pd)


actuals_pd = history_pd[ history_pd['ds'] < date(2018, 1, 1) ]['y']
predicted_pd = forecast_pd[ forecast_pd['ds'].dt.date < date(2018, 1, 1) ]['yhat']

mae = mean_absolute_error(actuals_pd, predicted_pd)
mse = mean_squared_error(actuals_pd, predicted_pd)
rmse = sqrt(mse)

print( '\n'.join(['MAE: {0}', 'MSE: {1}', 'RMSE: {2}']).format(mae, mse, rmse) )


# Change the model path to GCS
modelPath = "gs://sdg-demo-train/model"

pathlib.Path(modelPath).mkdir(parents=True, exist_ok=True)


pkl_path = modelPath+ "/Prophet.pkl"
with open(pkl_path, "wb") as f:
    pickle.dump(model, f)

forecast_pd.to_pickle(modelPath+"/forecast.pkl")
print("*** Data Saved ***")



