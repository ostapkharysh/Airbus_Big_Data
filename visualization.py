import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt




class Views:
    def __init__(self, config, df, results_df):    
        self.cfg = config
        self.df = df
        self.results_df=results_df
        self.correlation()
        self.toPandas()

    def toPandas(self):
        self.df_Pandas_25 = self.df.sample(False, 0.1, 42).toPandas()
        self.Results_DF = pd.DataFrame(self.results_df)
        

    def correlation(self):
        corr_matrix = self.df.select([x[0] for x in self.df.dtypes if 'int' in x])
        corr_matrix.show(5)
        [(c[0], self.df.corr("ArrDelay", c[0])) for c in corr_matrix.dtypes]

    def correlation_matrix(self):
        fig, ax = plt.subplots(figsize=(11,9))         # Sample figsize in inches
        sns.heatmap(self.df_Pandas_25.corr(), annot = True, ax=ax,cbar_kws={"shrink": .5},  vmax = 1, vmin = -1, center = 0, cmap='coolwarm', linewidth =.5, linecolor ='black', square = True)
        plt.show()
        #plt.show(block=False)



    def scatterPlot(self):
        features = ['TaxiOut','DepDelay']#, 'TaxiOut', 'HotIndOrigDest', 'Speed', 'HotCRSCatDepTime', 'HotCRSCatArrTime', 'HotDepTime']
        for feature in features:
            sns.regplot(x=self.df_Pandas_25["ArrDelay"], y=self.df_Pandas_25[feature])
            plt.show()

    #comparing R2 per each model 
    def BarChart_R2(self):

        fig, axes = plt.subplots(1, 4, figsize=(15, 5), sharey=True) 

        sns.barplot(ax=axes[0], x=self.Results_DF.name, y=self.Results_DF.R2LR)
        axes[0].set_title('Linear Regression')
        axes[0].set(xlabel='Variables', ylabel='R2')


        sns.barplot(ax=axes[1], x=self.Results_DF.name, y=self.Results_DF.R2RF)
        axes[1].set_title('Random Forest')
        axes[1].set(xlabel='Variables',ylabel='R2')


        sns.barplot(ax=axes[2], x=self.Results_DF.name, y=self.Results_DF.R2DT)
        axes[2].set_title('Decision Tree Regression')
        axes[2].set(xlabel='Variables',ylabel='R2')

        sns.barplot(ax=axes[3], x=self.Results_DF.name, y=self.Results_DF.R2GBR)
        axes[3].set_title('Gradient Booster Tree Regression')
        axes[3].set(xlabel='Variables',ylabel='R2')

        plt.show()


    #comparing MAE per each model 
    def BarChart_MAE(self):

        fig, axes = plt.subplots(1, 4, figsize=(15, 5), sharey=True)

        sns.barplot(ax=axes[0], x=self.Results_DF.name, y=self.Results_DF.maeLR)
        axes[0].set_title('Linear Regression')
        axes[0].set(xlabel='Variables', ylabel='MAE')


        sns.barplot(ax=axes[1], x=self.Results_DF.name, y=self.Results_DF.maeRF)
        axes[1].set_title('Random Forest')
        axes[1].set(xlabel='Variables',ylabel='MAE')


        sns.barplot(ax=axes[2], x=self.Results_DF.name, y=self.Results_DF.maeDT)
        axes[2].set_title('Decision Tree Regression')
        axes[2].set(xlabel='Variables',ylabel='MAE')

        sns.barplot(ax=axes[3], x=self.Results_DF.name, y=self.Results_DF.maeGBR)
        axes[3].set_title('Gradient Booster Tree Regression')
        axes[3].set(xlabel='Variables',ylabel='MAE')


        plt.show()
    

    #comparing RMSE per each model 
    def BarChart_RMSE(self):

        fig, axes = plt.subplots(1, 4, figsize=(15, 5), sharey=True)

        sns.barplot(ax=axes[0], x=self.Results_DF.name, y=self.Results_DF.rmseLR)
        axes[0].set_title('Linear Regression')
        axes[0].set(xlabel='Variables', ylabel='RMSE')


        sns.barplot(ax=axes[1], x=self.Results_DF.name, y=self.Results_DF.rmseRF)
        axes[1].set_title('Random Forest')
        axes[1].set(xlabel='Variables',ylabel='RMSE')


        sns.barplot(ax=axes[2], x=self.Results_DF.name, y=self.Results_DF.rmseDT)
        axes[2].set_title('Decision Tree Regression')
        axes[2].set(xlabel='Variables',ylabel='RMSE')

        sns.barplot(ax=axes[3], x=self.Results_DF.name, y=self.Results_DF.rmseGBR)
        axes[3].set_title('Gradient Booster Tree Regression')
        axes[3].set(xlabel='Variables',ylabel='RMSE')

        plt.show()