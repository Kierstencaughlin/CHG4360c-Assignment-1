import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator

class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):

        self.filepath=filepath

        self.ph_min=ph_lims[0]
        self.ph_max=ph_lims[1]

        self.temperature_min=temperature_lims[0]
        self.temperature_max=temperature_lims[1]

        self.df = pd.read_csv(filepath)

    def extract_batch(self, batch_id):

        mask_batch=self.df.loc[:,"batch_id"] == batch_id
        df_batch = self.df.loc[mask_batch,:]

        return df_batch

    def optimal_ph_mask(self, df_batch):

        ph=df_batch.loc[:,"pH"]
        mask_ph_min=ph>=self.ph_min
        mask_ph_max=ph<=self.ph_max

        mask_ph_optimal=mask_ph_min & mask_ph_max

        return mask_ph_optimal

    def optimal_temperature_mask(self, df_batch):

        temperature=df_batch.loc[:,"temperature_C"]
        mask_temperature_min = temperature >= self.temperature_min
        mask_temperature_max = temperature <= self.temperature_max

        mask_temperature_optimal = mask_temperature_min & mask_temperature_max

        return mask_temperature_optimal

    def get_n_batches(self):

        batch_ids = np.unique(self.df.loc[:, "batch_id"])
        n_batches = len(batch_ids)

        return n_batches

    def export_dashboard(self, batch_id, filepath):

       df_batch=self.extract_batch(batch_id)
       time = df_batch.loc[:, "time_h"]

       C_glucose = df_batch.loc[:, "C_glucose_g_L^-1"]
       C_biomass = df_batch.loc[:, "C_biomass_g_L^-1"]
       C_product = df_batch.loc[:, "C_product_g_L^-1"]

       temperature = df_batch.loc[:,"temperature_C"]
       ph=df_batch.loc[:,"pH"]
       DO=df_batch.loc[:,"DO_percent"]

       mask_temperature_optimal = self.optimal_temperature_mask(df_batch)
       mask_temperature_nonoptimal = ~mask_temperature_optimal

       mask_ph_optimal=self.optimal_ph_mask(df_batch)
       mask_ph_nonoptimal=~mask_ph_optimal

       fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 6), dpi=200, layout="constrained")

       kwargs_scatter = dict(s=20,linewidth=1)

       # Top left: Concentration vs. Time
       axes[0, 0].scatter(time,C_glucose,label="Glucose", color="tab:blue",marker="o",**kwargs_scatter)

       axes[0, 0].scatter(time,C_biomass,label="Biomass",color="tab:orange",marker="^",**kwargs_scatter)

       axes[0, 0].scatter(time,C_product,label="Product",color="tab:green",marker="d",**kwargs_scatter)

       axes[0, 0].set_ylabel("Concentration [g/L]")
       axes[0, 0].legend()


        # Top right: Temperature vs. Time
       axes[0, 1].scatter(time[mask_temperature_optimal],temperature[mask_temperature_optimal],label="Optimal",color="tab:green",marker="o",**kwargs_scatter)

       axes[0, 1].scatter(time[mask_temperature_nonoptimal],temperature[mask_temperature_nonoptimal],label="Non-optimal",color="tab:red",marker="x",**kwargs_scatter)

       axes[0, 1].set_ylabel("Temperature [C]")
       axes[0, 1].legend()

        # Bottom left: pH vs. Time
       axes[1, 0].scatter(time[mask_ph_optimal],ph[mask_ph_optimal],label="Optimal",color="tab:green",marker="o",**kwargs_scatter)

       axes[1, 0].scatter(time[mask_ph_nonoptimal],ph[mask_ph_nonoptimal],label="Non-optimal",color="tab:red",marker="x",**kwargs_scatter)

       axes[1, 0].set_ylabel("pH")
       axes[1, 0].legend()

        #Bottom right: Dissolved oxygen vs. Time
       axes[1, 1].scatter(time,DO,color="tab:blue",marker="o",**kwargs_scatter)
       axes[1, 1].set_ylabel("DO [%]")


       for ax in np.ravel(axes):
            ax.xaxis.set_major_locator(MultipleLocator(6))
            ax.set_xlabel("Time [h]")

       fig.savefig(filepath)
       plt.close(fig)

    def export_summary(self, filepath):
            summary_rows = []

            n_batches = self.get_n_batches()

            for batch_id in range(1, n_batches + 1):
                df_batch = self.extract_batch(batch_id)

                mask_ph = self.optimal_ph_mask(df_batch)
                mask_temperature = self.optimal_temperature_mask(df_batch)

                ph_optimal_percent = 100 * np.sum(mask_ph) / len(mask_ph)
                temperature_optimal_percent = (100 * np.sum(mask_temperature) / len(mask_temperature))

                ph_optimal_percent = round(ph_optimal_percent, 2)
                temperature_optimal_percent = round(temperature_optimal_percent, 2)

                C_product_final = df_batch.loc[df_batch.index[-1],"C_product_g_L^-1"]

                summary_row = {"batch_id": batch_id,"ph_optimal_percent": ph_optimal_percent,"temperature_optimal_percent": temperature_optimal_percent,"C_product_g_L^-1_final": C_product_final}

                summary_rows.append(summary_row)

            df_summary = pd.DataFrame(summary_rows)

            df_summary.to_csv(filepath, index=False)

