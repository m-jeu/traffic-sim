import trafficsim
import mesa.batchrunner
import numpy as np
import matplotlib.pyplot as plt

max_vel = 5

fixed_params = {
    "max_velocity": max_vel,
    "p_brake": 0,
    "width": 100
}

params = [
    {
        "density": d,
    }
    for d in np.arange(.01, 1, 0.01)
]

br = mesa.batchrunner.FixedBatchRunner(trafficsim.World,
                                       parameters_list=params,
                                       fixed_parameters=fixed_params,
                                       model_reporters=
                                       {
                                           "Average velocity": lambda m: m.data_collector.get_model_vars_dataframe()[
                                               "Average velocity"]
                                       },
                                       max_steps=10
                                       )
br.run_all()
df = br.get_model_vars_dataframe()
df = df["Average velocity"].apply(lambda run: run.iloc[max_vel:]).mean(axis=1)
plt.plot(df)

fixed_params = {
    "max_velocity": max_vel,
    "p_brake": .05,
    "width": 100
}
br = mesa.batchrunner.FixedBatchRunner(trafficsim.World,
                                       parameters_list=params,
                                       fixed_parameters=fixed_params,
                                       model_reporters=
                                       {
                                           "Average velocity": lambda m: m.data_collector.get_model_vars_dataframe()[
                                               "Average velocity"]
                                       },
                                       max_steps=100
                                       )

br.run_all()
df = br.get_model_vars_dataframe()
df = df["Average velocity"].apply(lambda run: run.iloc[max_vel:]).mean(axis=1)
plt.plot(df)
plt.show()