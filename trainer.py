
from pyspark.sql.functions import abs
from pyspark.ml import Pipeline
from pyspark.ml.feature import MinMaxScaler, VectorAssembler
from pyspark.ml.regression import LinearRegression, GBTRegressor, RandomForestRegressor, DecisionTreeRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator



class Trainer:
    """
    This class represents execution interface for the statistical models,
    along with cross-validation tuning, testing and evaluation. There testing results of each
    algorithm are captured here.
    """

    def __init__(self, config, spark, sc, cleaned_data):
        """

        Imports the Spark, Spark Config, Spark Context to use in value transformation, tuning,
        and final results testing.

        """
        self.cfg = config
        self.spark = spark
        self.sc = sc
        self.df = cleaned_data.df
        self.X = cleaned_data.X
        self.oneHot = cleaned_data.oneHot
        self.varIdxer = cleaned_data.varIdxer
        self.bucketizer = cleaned_data.bucketizer


        """ Splitting the dataset based on the user input """
        if self.cfg.dataset_size == 0:
            self.train, self.test = self.df.randomSplit(
                [self.cfg.split_size_train / 100, (100 - self.cfg.split_size_train) / 100])
        else:
            """ Limiting the amount of variables used for the training and testing """
            print("Training set : ", int(self.cfg.dataset_size * (self.cfg.split_size_train / 100)))
            print("Testing set : ", int(self.cfg.dataset_size * ((100 - self.cfg.split_size_train) / 100)))
            self.train, self.test = self.df.randomSplit([.5, 0.1], seed=1234)
            self.train = self.train.limit(int(self.cfg.dataset_size * (self.cfg.split_size_train / 100)))
            self.test = self.test.limit(int(self.cfg.dataset_size * ((100 - self.cfg.split_size_train) / 100)))

        results_LR = []
        results_RF = []
        results_DT = []
        results_GBR = []
        results_all = []

        self.Visualize_Results = []

        if self.cfg.model == 'linear_regression':
            """
            Runs the Linear Regression model, and records the results
            """

            for features in self.X:
                self.R2LR, self.maeLR, self.rmseLR = self.linear_regression_train(features)

                features['R2LR'] = self.R2LR
                features['maeLR'] = self.maeLR
                features['rmseLR'] = self.rmseLR
                results_LR.append(features)

            for x in results_LR:
                self.Visualize_Results.append(x)
                print(x)

        elif self.cfg.model == 'gradient_boosted_tree_regression':
            """
            Runs the Gradient-boosted Tree Regression model and records the results
            """

            for features in self.X:
                self.R2GBR, self.maeGBR, self.rmseGBR = self.gradient_boosted_tree_regression(features)
                features['R2GBR'] = self.R2GBR
                features['maeGBR'] = self.maeGBR
                features['rmseGBR'] = self.rmseGBR
                results_GBR.append(features)

            for x in results_GBR:
                self.Visualize_Results.append(x)
                print(x)

        elif self.cfg.model == 'random_forest':
            """
            Runs the Random Forest model and records the results
            """
            for features in self.X:

                self.R2RF, self.maeRF, self.rmseRF = self.random_forest_train(features)
                features['R2RF'] = self.R2RF
                features['maeRF'] = self.maeRF
                features['rmseRF'] = self.rmseRF
                results_RF.append(features)

            for x in results_RF:
                self.Visualize_Results.append(x)
                print(x)

        elif self.cfg.model == 'decision_tree_regression':
            """
            Runs the Decision Tree Regression model and records the results
            """

            for features in self.X:
                self.R2DT, self.maeDT, self.rmseDT = self.decision_tree_regression_train(features)
                features['R2DT'] = self.R2DT
                features['maeDT'] = self.maeDT
                features['rmseDT'] = self.rmseDT
                results_DT.append(features)

            for x in results_DT:
                self.Visualize_Results.append(x)
                print(x)

        elif self.cfg.model == 'all':
            """
            Based on the user selection model runs all the models defined in this class 
            """
            for features in self.X:
                self.R2LR, self.maeLR, self.rmseLR = self.linear_regression_train(features)
                self.R2RF, self.maeRF, self.rmseRF = self.random_forest_train(features)
                self.R2DT, self.maeDT, self.rmseDT = self.decision_tree_regression_train(features)
                self.R2GBR, self.maeGBR, self.rmseGBR = self.gradient_boosted_tree_regression(features)

                features['R2LR'] = self.R2LR
                features['maeLR'] = self.maeLR
                features['rmseLR'] = self.rmseLR

                features['R2RF'] = self.R2RF
                features['maeRF'] = self.maeRF
                features['rmseRF'] = self.rmseRF

                features['R2DT'] = self.R2DT
                features['maeDT'] = self.maeDT
                features['rmseDT'] = self.rmseDT

                features['R2GBR'] = self.R2GBR
                features['maeGBR'] = self.maeGBR
                features['rmseGBR'] = self.rmseGBR

                results_all.append(features)

            for x in results_all:
                self.Visualize_Results.append(x)
                print(x)


            print('\n Linear Regression R2 : {R2LR}\t'
                  '\n Random Forest R2 : {R2RF}\t'
                  '\n Decision Tree Regression R2  : {R2DT}\t'
                  '\n Gradient Booster Tree Regression R2  : {R2GBR}\t'.format(
                R2RF=self.R2RF,
                R2LR=self.R2LR,
                R2DT=self.R2DT,
                R2GBR=self.R2GBR))
        else:
            print("nothing was selected")

    def metrics(self, predictions):
        """
        Evaluates the results of the model

        """
        x = ((predictions['ArrDelay'] - predictions['prediction']) / predictions['ArrDelay']) * 100
        predictions = predictions.withColumn('Accuracy', abs(x))

        rmse_evaluator = RegressionEvaluator(
            labelCol="ArrDelay",
            predictionCol="prediction",
            metricName="rmse")

        mae_evaluator = RegressionEvaluator(labelCol='ArrDelay',
                                            predictionCol="prediction",
                                            metricName="mae")

        R2_evaluator = RegressionEvaluator(predictionCol="prediction",
                                           labelCol="ArrDelay",
                                           metricName="r2")

        R2 = R2_evaluator.evaluate(predictions)
        mae = mae_evaluator.evaluate(predictions)
        rmse = rmse_evaluator.evaluate(predictions)

        print("Root Mean Squared Error (RMSE) on test data = %g" % rmse)
        print("Mean Absolute Error (MAE) on test data = %g" % mae)
        print("R Squared (R2) on test data = %g" % R2)

        return R2, mae, rmse

    def linear_regression_train(self, X):
        """
        Implements the Linear Regression model along with data preprocessing and transformation,
        using pipeline. Tunes the training model based on the cross-validation set based on RMSE.

        """

        assembler = VectorAssembler(
            inputCols=X['variables'],
            outputCol='features')

        scaler = MinMaxScaler(inputCol='features', outputCol='scaled')

        lin_reg = LinearRegression(featuresCol='scaled', labelCol='ArrDelay')

        pipeline = Pipeline(stages=[self.bucketizer, self.varIdxer, self.oneHot, assembler, scaler, lin_reg])

        linParamGrid = ParamGridBuilder() \
            .addGrid(lin_reg.regParam, [0.1, 0.01]) \
            .addGrid(lin_reg.fitIntercept, [False, True]) \
            .addGrid(lin_reg.elasticNetParam, [0.0, 1.0]) \
            .build()

        tvs = CrossValidator(estimator=pipeline, \
                             estimatorParamMaps=linParamGrid,
                             evaluator=RegressionEvaluator(labelCol="ArrDelay", metricName="rmse"), \
                             numFolds=3)
        # trainRatio=0.85)

        model = tvs.fit(self.train)
        predictions = model.transform(self.test)

        print("Linear Regression")
        print(X['variables'])

        R2, mae, rmse = self.metrics(predictions)

        return R2, mae, rmse

    def decision_tree_regression_train(self, X):
        """
        Implements the Decision Tree Regression model along with data preprocessing and transformation,
        using pipeline. Tunes the training model based on the cross-validation set based on RMSE.

        """

        assembler = VectorAssembler(inputCols=X['variables'],
                                    outputCol='features')

        scaler = MinMaxScaler(inputCol='features', outputCol='scaled')

        dt1 = DecisionTreeRegressor(featuresCol='scaled',
                                    labelCol='ArrDelay')

        pipeline = Pipeline(stages=[self.bucketizer, self.varIdxer, self.oneHot, assembler, scaler, dt1])

        dtparamGrid = (ParamGridBuilder()
                       .addGrid(dt1.maxDepth, [2, 5, 10])
                       # .addGrid(dt.maxDepth, [2, 5, 10])
                       .addGrid(dt1.maxBins, [5, 10, 30])
                       # .addGrid(dt1.numTrees, [5, 20, 50])
                       # .addGrid(dt.maxBins, [10, 20])
                       .build())

        dtcv = CrossValidator(estimator=pipeline,
                              estimatorParamMaps=dtparamGrid,
                              evaluator=RegressionEvaluator(labelCol="ArrDelay",
                                                            metricName="rmse"),
                              numFolds=3)

        model = dtcv.fit(self.train)
        predictions = model.transform(self.test)

        print("Decision Tree")
        print(X['variables'])
        R2, mae, rmse = self.metrics(predictions)

        return R2, mae, rmse

    def gradient_boosted_tree_regression(self, X):
        """
        Implements the Gradient-boosted Tree Regression model along with data preprocessing and transformation,
        using pipeline. Tunes the training model based on the cross-validation set based on RMSE.


        """

        assembler = VectorAssembler(inputCols=X['variables'],
                                    outputCol='features')

        scaler = MinMaxScaler(inputCol='features', outputCol='scaled')

        gbt = GBTRegressor(featuresCol='scaled',
                           labelCol="ArrDelay",
                           maxIter=10)
        pipeline = Pipeline(stages=[self.bucketizer, self.varIdxer, self.oneHot, assembler, scaler, gbt])


        # original
        TreeParamGrid = ParamGridBuilder() \
            .addGrid(gbt.maxDepth, [2, 5, 10]) \
            .addGrid(gbt.maxBins, [5, 10, 30]) \
            .build()

        tvs = CrossValidator(estimator=pipeline,
                             estimatorParamMaps=TreeParamGrid,  # remove if don't want to use ParamGridBuilder
                             evaluator=RegressionEvaluator(labelCol="ArrDelay",
                                                           metricName="rmse"),
                             numFolds=3)
        # trainRatio=0.85)

        model = tvs.fit(self.train)
        predictions = model.transform(self.test)

        print("Gradient boosted tree")
        print(X['variables'])
        R2, mae, rmse = self.metrics(predictions)

        return R2, mae, rmse

    def random_forest_train(self, X):
        """
        Implements the Random Forest Regression model along with data preprocessing and transformation,
        using pipeline. Tunes the training model based on the cross-validation set based on RMSE.

        """

        assembler = VectorAssembler(inputCols=X['variables'],
                                    outputCol='features')

        scaler = MinMaxScaler(inputCol='features', outputCol='scaled')

        rf = RandomForestRegressor(featuresCol='scaled',
                                   labelCol='ArrDelay')

        pipeline = Pipeline(stages=[self.bucketizer, self.varIdxer, self.oneHot, assembler, scaler, rf])

        rfparamGrid = (ParamGridBuilder()
                       # .addGrid(rf.maxDepth, [2, 5, 10, 20, 30])
                       .addGrid(rf.maxDepth, [2, 5, 10])
                       # .addGrid(rf.maxBins, [10, 20, 40, 80, 100])
                       .addGrid(rf.maxBins, [5, 10, 30])
                       # .addGrid(rf.numTrees, [5, 20, 50, 100, 500])
                       .addGrid(rf.numTrees, [5, 20, 50])
                       .build())

        # Create 3-fold CrossValidator
        rfcv = CrossValidator(estimator=pipeline,
                              estimatorParamMaps=rfparamGrid,
                              evaluator=RegressionEvaluator(labelCol="ArrDelay",
                                                            metricName="rmse"),
                              numFolds=3)

        model = rfcv.fit(self.train)
        predictions = model.transform(self.test)

        print("Random Forest")
        print(X['variables'])
        R2, mae, rmse = self.metrics(predictions)

        return R2, mae, rmse
