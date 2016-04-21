import pandas as pd
import numpy as np
from scipy.stats import norm

from eemeter.location import _load_zipcode_to_lat_lng_index
from eemeter.location import _load_zipcode_to_station_index

from collections import OrderedDict
from collections import defaultdict
from warnings import warn

REAL_OR_INTEGER_VALUED_COLUMNS_HEATING = [
    'n_days_in_season_range',
    'n_days_in_season',
    'n_days_both_heating_and_cooling',
    'n_days_insufficient_data',

    'seasonal_savings_dailyavgHDD',
    'seasonal_savings_deltaT',
    'seasonal_savings_hourlyavgHDD',

    'seasonal_avoided_runtime_dailyavgHDD',
    'seasonal_avoided_runtime_deltaT',
    'seasonal_avoided_runtime_hourlyavgHDD',

    'total_auxiliary_heating_runtime',
    'total_emergency_heating_runtime',
    'total_heating_runtime',

    'actual_daily_runtime',
    'actual_seasonal_runtime',

    'baseline_comfort_temperature',

    'baseline_daily_runtime_dailyavgHDD',
    'baseline_daily_runtime_deltaT',
    'baseline_daily_runtime_hourlyavgHDD',

    'baseline_seasonal_runtime_dailyavgHDD',
    'baseline_seasonal_runtime_deltaT',
    'baseline_seasonal_runtime_hourlyavgHDD',

    'mean_demand_dailyavgHDD',
    'mean_demand_deltaT',
    'mean_demand_hourlyavgHDD',

    'mean_demand_baseline_dailyavgHDD',
    'mean_demand_baseline_deltaT',
    'mean_demand_baseline_hourlyavgHDD',

    'rhu_00F_to_05F',
    'rhu_05F_to_10F',
    'rhu_10F_to_15F',
    'rhu_15F_to_20F',
    'rhu_20F_to_25F',
    'rhu_25F_to_30F',
    'rhu_30F_to_35F',
    'rhu_35F_to_40F',
    'rhu_40F_to_45F',
    'rhu_45F_to_50F',
    'rhu_50F_to_55F',
    'rhu_55F_to_60F',

    'slope_deltaT',
    'alpha_est_dailyavgHDD',
    'alpha_est_hourlyavgHDD',

    'intercept_deltaT',
    'deltaT_base_est_dailyavgHDD',
    'deltaT_base_est_hourlyavgHDD',

    'mean_sq_err_dailyavgHDD',
    'mean_sq_err_deltaT',
    'mean_sq_err_hourlyavgHDD',

    'root_mean_sq_err_dailyavgHDD',
    'root_mean_sq_err_deltaT',
    'root_mean_sq_err_hourlyavgHDD',

    'cv_root_mean_sq_err_dailyavgHDD',
    'cv_root_mean_sq_err_deltaT',
    'cv_root_mean_sq_err_hourlyavgHDD',

    'mean_abs_err_dailyavgHDD',
    'mean_abs_err_deltaT',
    'mean_abs_err_hourlyavgHDD',

    'mean_abs_pct_err_dailyavgHDD',
    'mean_abs_pct_err_deltaT',
    'mean_abs_pct_err_hourlyavgHDD',
]

REAL_OR_INTEGER_VALUED_COLUMNS_COOLING = [
    'n_days_in_season_range',
    'n_days_in_season',
    'n_days_both_heating_and_cooling',
    'n_days_insufficient_data',

    'seasonal_savings_dailyavgCDD',
    'seasonal_savings_deltaT',
    'seasonal_savings_hourlyavgCDD',

    'seasonal_avoided_runtime_dailyavgCDD',
    'seasonal_avoided_runtime_deltaT',
    'seasonal_avoided_runtime_hourlyavgCDD',

    'total_cooling_runtime',

    'actual_daily_runtime',
    'actual_seasonal_runtime',

    'baseline_comfort_temperature',

    'baseline_daily_runtime_dailyavgCDD',
    'baseline_daily_runtime_deltaT',
    'baseline_daily_runtime_hourlyavgCDD',

    'baseline_seasonal_runtime_dailyavgCDD',
    'baseline_seasonal_runtime_deltaT',
    'baseline_seasonal_runtime_hourlyavgCDD',

    'mean_demand_dailyavgCDD',
    'mean_demand_deltaT',
    'mean_demand_hourlyavgCDD',

    'mean_demand_baseline_dailyavgCDD',
    'mean_demand_baseline_deltaT',
    'mean_demand_baseline_hourlyavgCDD',

    'slope_deltaT',
    'alpha_est_dailyavgCDD',
    'alpha_est_hourlyavgCDD',

    'intercept_deltaT',
    'deltaT_base_est_dailyavgCDD',
    'deltaT_base_est_hourlyavgCDD',

    'mean_sq_err_dailyavgCDD',
    'mean_sq_err_deltaT',
    'mean_sq_err_hourlyavgCDD',

    'root_mean_sq_err_dailyavgCDD',
    'root_mean_sq_err_deltaT',
    'root_mean_sq_err_hourlyavgCDD',

    'cv_root_mean_sq_err_dailyavgCDD',
    'cv_root_mean_sq_err_deltaT',
    'cv_root_mean_sq_err_hourlyavgCDD',

    'mean_abs_err_dailyavgCDD',
    'mean_abs_err_deltaT',
    'mean_abs_err_hourlyavgCDD',

    'mean_abs_pct_err_dailyavgCDD',
    'mean_abs_pct_err_deltaT',
    'mean_abs_pct_err_hourlyavgCDD',
]

REAL_OR_INTEGER_VALUED_COLUMNS_ALL = [
    'n_days_in_season_range',
    'n_days_in_season',
    'n_days_both_heating_and_cooling',
    'n_days_insufficient_data',

    'seasonal_savings_dailyavgCDD',
    'seasonal_savings_dailyavgHDD',
    'seasonal_savings_deltaT',
    'seasonal_savings_hourlyavgCDD',
    'seasonal_savings_hourlyavgHDD',

    'seasonal_avoided_runtime_dailyavgCDD',
    'seasonal_avoided_runtime_dailyavgHDD',
    'seasonal_avoided_runtime_deltaT',
    'seasonal_avoided_runtime_hourlyavgCDD',
    'seasonal_avoided_runtime_hourlyavgHDD',

    'total_auxiliary_heating_runtime',
    'total_cooling_runtime',
    'total_emergency_heating_runtime',
    'total_heating_runtime',

    'actual_daily_runtime',
    'actual_seasonal_runtime',

    'baseline_comfort_temperature',

    'baseline_daily_runtime_dailyavgCDD',
    'baseline_daily_runtime_dailyavgHDD',
    'baseline_daily_runtime_deltaT',
    'baseline_daily_runtime_hourlyavgCDD',
    'baseline_daily_runtime_hourlyavgHDD',

    'baseline_seasonal_runtime_dailyavgCDD',
    'baseline_seasonal_runtime_dailyavgHDD',
    'baseline_seasonal_runtime_deltaT',
    'baseline_seasonal_runtime_hourlyavgCDD',
    'baseline_seasonal_runtime_hourlyavgHDD',

    'mean_demand_dailyavgCDD',
    'mean_demand_dailyavgHDD',
    'mean_demand_deltaT',
    'mean_demand_hourlyavgCDD',
    'mean_demand_hourlyavgHDD',

    'mean_demand_baseline_dailyavgCDD',
    'mean_demand_baseline_dailyavgHDD',
    'mean_demand_baseline_deltaT',
    'mean_demand_baseline_hourlyavgCDD',
    'mean_demand_baseline_hourlyavgHDD',

    'rhu_00F_to_05F',
    'rhu_05F_to_10F',
    'rhu_10F_to_15F',
    'rhu_15F_to_20F',
    'rhu_20F_to_25F',
    'rhu_25F_to_30F',
    'rhu_30F_to_35F',
    'rhu_35F_to_40F',
    'rhu_40F_to_45F',
    'rhu_45F_to_50F',
    'rhu_50F_to_55F',
    'rhu_55F_to_60F',

    'slope_deltaT',
    'alpha_est_dailyavgCDD',
    'alpha_est_dailyavgHDD',
    'alpha_est_hourlyavgCDD',
    'alpha_est_hourlyavgHDD',

    'intercept_deltaT',
    'deltaT_base_est_dailyavgCDD',
    'deltaT_base_est_dailyavgHDD',
    'deltaT_base_est_hourlyavgCDD',
    'deltaT_base_est_hourlyavgHDD',

    'mean_sq_err_dailyavgCDD',
    'mean_sq_err_dailyavgHDD',
    'mean_sq_err_deltaT',
    'mean_sq_err_hourlyavgCDD',
    'mean_sq_err_hourlyavgHDD',

    'root_mean_sq_err_dailyavgCDD',
    'root_mean_sq_err_dailyavgHDD',
    'root_mean_sq_err_deltaT',
    'root_mean_sq_err_hourlyavgCDD',
    'root_mean_sq_err_hourlyavgHDD',

    'cv_root_mean_sq_err_dailyavgCDD',
    'cv_root_mean_sq_err_dailyavgHDD',
    'cv_root_mean_sq_err_deltaT',
    'cv_root_mean_sq_err_hourlyavgCDD',
    'cv_root_mean_sq_err_hourlyavgHDD',

    'mean_abs_err_dailyavgCDD',
    'mean_abs_err_dailyavgHDD',
    'mean_abs_err_deltaT',
    'mean_abs_err_hourlyavgCDD',
    'mean_abs_err_hourlyavgHDD',

    'mean_abs_pct_err_dailyavgCDD',
    'mean_abs_pct_err_dailyavgHDD',
    'mean_abs_pct_err_deltaT',
    'mean_abs_pct_err_hourlyavgCDD',
    'mean_abs_pct_err_hourlyavgHDD',
]

# Just for reference, not used anywhere
IGNORED_COLUMNS = [
    'ct_identifier',
    'equipment_type',
    'season_name',
    'station',
    'zipcode',
]

class ZipcodeGroupSpec(object):
    """ Mapping from zipcodes to groups. Must supply either filepath or
    dictionary.

    Parameters
    ----------
    filepath : str, None
        Path to CSV file containing the columns "zipcode" and "group".
        Each row should map the zipcode column to a target group. E.g.::

            zipcode,group
            01234,group_a
            12345,group_a
            23456,group_a
            43210,groub_b
            54321,group_b
            65432,group_c

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    dictionary : dict, None
        Dictionary with zipcodes as keys and groups as values. E.g.::

            dictionary = {
                "01234": "group_a",
                "12345": "group_a",
                "23456": "group_a",
                "43210": "group_b",
                "54321": "group_b",
                "65432": "group_c",
            }

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    label : str
        Extra label identifying the grouping method, for use in cases in which
        there might be ambiguity.
    """

    def __init__(self, filepath=None, dictionary=None, label=None):
        if filepath is not None:
            self.spec = self._load_spec_csv(filepath)
        elif dictionary is not None:
            self.spec = dictionary
        else:
            message = "Please supply either filepath or dictionary."
            raise ValueError(message)

        self.label = label

    def _load_spec_csv(self, filepath):
        df = pd.read_csv(filepath,
                usecols=["zipcode", "group"],
                dtype={"zipcode":str, "group":str})
        return {row["zipcode"]: row["group"] for _,row in df.iterrows()}

    def iter_groups(self, df):
        """ Iterate over groups (in no particular order.)

        Parameters
        ----------
        df : pd.Dataframe
            Dataframe containing all output data from which to draw groupings.
        """

        # avoid adding extra column to input df
        df = df.copy()

        df["_group"] = pd.Series([self.spec.get(zipcode) for zipcode in df["zipcode"]])
        for group, grouped in df.groupby("_group"):
            group_name = group if self.label is None else "{}_{}".format(group, self.label)
            yield group_name, grouped

def combine_output_dataframes(dfs):
    """ Combines output dataframes. Useful when combining output from batches.

    Parameters
    ----------
    dfs : list of pd.DataFrame
        Output dataFrames to combine into one.

    Returns
    -------
    out : pd.DataFrame
        Dataframe with combined output metadata.

    """
    return pd.concat(dfs, ignore_index=True)

def compute_summary_statistics(df, label, target_method="dailyavg",
        target_error_metric="CVRMSE", target_error_max_value=np.inf,
        statistical_power_confidence=.95, statistical_power_ratio=.05):
    """ Computes summary statistics for the output dataframe. Computes the
    following statistics for each real-valued or integer valued column in
    the output dataframe: mean, standard error of the mean, and deciles.

    Parameters
    ----------
    df : pd.DataFrame
        Output for which to compute summary statistics.
    label : str
        Name for this set of thermostat outputs.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-season inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : collections.OrderedDict
        An ordered dict containing the summary statistics. Column names are as
        follows, in which ### is a placeholder for the name of the column:

          - mean: ###_mean
          - standard error of the mean: ###_sem
          - 10th quantile: ###_10q
          - 20th quantile: ###_20q
          - 30th quantile: ###_30q
          - 40th quantile: ###_40q
          - 50th quantile: ###_50q
          - 60th quantile: ###_60q
          - 70th quantile: ###_70q
          - 80th quantile: ###_80q
          - 90th quantile: ###_90q
          - number of non-null seasons: ###_n

        The following general values are also output:

          - label: label
          - number of total seasons: n_total_seasons

    """

    if target_method not in ["dailyavg", "hourlyavg", "deltaT"]:
        message = 'Method not supported - please use one of "dailyavg",' \
                '"hourlyavg", or "deltaT"'
        raise ValueError(message)

    def _statistical_power_estimate(season_type_stats, season_type):

        if season_type == "heating":
            if target_method == "deltaT":
                method = target_method
            else:
                method = "{}HDD".format(target_method)

            stat_power_target_mean = "seasonal_savings_{}_mean".format(method)
            stat_power_target_sem = "seasonal_savings_{}_sem".format(method)
            stat_power_target_n = "seasonal_savings_{}_n".format(method)
        else:
            if target_method == "deltaT":
                method = target_method
            else:
                method = "{}CDD".format(target_method)

            stat_power_target_mean = "seasonal_savings_{}_mean".format(method)
            stat_power_target_sem = "seasonal_savings_{}_sem".format(method)
            stat_power_target_n = "seasonal_savings_{}_n".format(method)

        mean = season_type_stats[stat_power_target_mean]
        sem = season_type_stats[stat_power_target_sem]
        n = season_type_stats[stat_power_target_n]

        n_std_devs = norm.ppf(1 - (1 - statistical_power_confidence)/2)
        std = sem * (n**.5)
        target_interval = mean * statistical_power_ratio
        target_n = (std * n_std_devs / target_interval) ** 2.
        return target_n

    def _filter_rows(season_type_df, season_type):
        filtered_df_rows = []
        for i, row in season_type_df.iterrows():
            if _accept_row(row, season_type):
                filtered_df_rows.append(row)
        return pd.DataFrame(filtered_df_rows)

    def _accept_row(row, season_type):
        passes_validity_rules = _passes_validity_rules(row)
        has_physical_deltaT = _has_physical_deltaT(row, season_type)
        has_good_enough_fit = _has_good_enough_fit(row, season_type)
        return (
            passes_validity_rules
            and has_physical_deltaT
            and has_good_enough_fit
        )

    def _passes_validity_rules(row):
        try:
            pct_insufficient_data = row.n_days_insufficient_data / row.n_days_in_season_range
        except ZeroDivisionError:
            return False
        else:
            return pct_insufficient_data < 0.05

    def _has_physical_deltaT(row, season_type):
        if target_method == "deltaT":
            column = "intercept_deltaT"
        else:
            if season_type == "heating":
                column = "deltaT_base_est_{}HDD".format(target_method)
            else:
                column = "deltaT_base_est_{}CDD".format(target_method)

        return -10 <= row[column] <= 50

    def _has_good_enough_fit(row, season_type):
        if target_error_metric == "MSE":
            error_metric_prefix = "mean_sq_err"
        elif target_error_metric == "RMSE":
            error_metric_prefix = "root_mean_sq_err"
        elif target_error_metric == "CVRMSE":
            error_metric_prefix = "cv_root_mean_sq_err"
        elif target_error_metric == "MAE":
            error_metric_prefix = "mean_abs_err"
        elif target_error_metric == "MAPE":
            error_metric_prefix = "mean_abs_pct_err"
        else:
            message = (
                'Method {} not supported.'
                ' Use one of "MSE", "RMSE", "CVRMSE", "MAE", or "MAPE".'
            ).format(target_error_metric)
            raise ValueError(message)

        if target_method == "deltaT":
            method_suffix = "deltaT"
        else:
            if season_type == "cooling":
                method_suffix = "{}CDD".format(target_method)
            else:
                method_suffix = "{}HDD".format(target_method)

        column = "{}_{}".format(error_metric_prefix, method_suffix)

        return row[column] < target_error_max_value

    def _get_season_type_stats(season_type_df, season_type, season_type_columns):
        n_seasons_total = season_type_df.shape[0]

        filtered_season_type_df = _filter_rows(season_type_df, season_type)

        n_seasons_kept = filtered_season_type_df.shape[0]
        n_seasons_discarded = n_seasons_total - n_seasons_kept

        season_type_stats = OrderedDict()
        season_type_stats["label"] = "{}_{}".format(label, season_type)
        season_type_stats["n_seasons_total"] = n_seasons_total
        season_type_stats["n_seasons_kept"] = n_seasons_kept
        season_type_stats["n_seasons_discarded"] = n_seasons_discarded

        if n_seasons_total > 0:

            quantiles = [10, 20, 30, 40, 50, 60, 70, 80, 90]

            for column_name in season_type_columns:
                column = season_type_df[column_name].replace([np.inf, -np.inf], np.nan).dropna()

                # calculate quantiles
                season_type_stats["{}_mean".format(column_name)] = np.nanmean(column)
                season_type_stats["{}_sem".format(column_name)] = np.nanstd(column) / (column.count() ** .5)
                season_type_stats["{}_n".format(column_name)] = column.count()
                for quantile in quantiles:
                    season_type_stats["{}_q{}".format(column_name, quantile)] = column.quantile(quantile / 100.)

            season_type_stats["n_enough_statistical_power"] = \
                    _statistical_power_estimate(season_type_stats, season_type)

            return [season_type_stats]
        else:
            message = "Not enough data to compute summary_statistics for {} {}".format(label, season_type)
            warn(message)
            return []


    heating_df = df[["Heating" in name for name in df["season_name"]]]
    cooling_df = df[["Cooling" in name for name in df["season_name"]]]

    stats = _get_season_type_stats(heating_df, "heating", REAL_OR_INTEGER_VALUED_COLUMNS_HEATING)
    stats.extend(_get_season_type_stats(cooling_df, "cooling", REAL_OR_INTEGER_VALUED_COLUMNS_COOLING))

    return stats

def compute_summary_statistics_by_zipcode_group(df,
        filepath=None, dictionary=None, group_spec=None,
        target_method="dailyavg", target_error_metric="CVRMSE",
        target_error_max_value=np.inf, statistical_power_confidence=.95,
        statistical_power_ratio=.05):
    """ Filepath to zipcode -> group mapping. Note that this mapping should
    include all zipcodes that may appear in the raw output file dataframe. Any
    zipcodes which do not appear in the mapping but do occur in the ouput data
    will be ignored. The mapping can, however, include zipcodes that do not
    appear in the raw output data.

    Parameters
    ----------
    filepath : str, None
        Path to CSV file containing the columns "zipcode" and "group".
        Each row should map the zipcode column to a target group. E.g.::

            zipcode,group
            01234,group_a
            12345,group_a
            23456,group_a
            43210,groub_b
            54321,group_b
            65432,group_c

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    dictionary : dict, None
        Dictionary with zipcodes as keys and groups as values. E.g.::

            dictionary = {
                "01234": "group_a",
                "12345": "group_a",
                "23456": "group_a",
                "43210": "group_b",
                "54321": "group_b",
                "65432": "group_c",
            }

        This creates the following grouping:

        - **group_a**: 01234,12345,23456
        - **group_b**: 43210,54321
        - **group_c**: 65432

    group_spec : ZipcodeGroupSpec object
        Initialized group spec object containing a zipcode -> group mapping.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-season inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : list of dict
        List of stats dictionaries computed by group.

    """
    if group_spec is not None:
        pass
    elif filepath is not None:
        group_spec = ZipcodeGroupSpec(filepath=filepath)
    elif dictionary is not None:
        group_spec = ZipcodeGroupSpec(dictionary=dictionary)
    else:
        message = "Please supply either the filepath of a CSV file, a" \
                "dictionary, or a ZipcodeGroupSpec object"
        raise ValueError(message)

    stats = []
    for label, group_df in group_spec.iter_groups(df):
        stats.extend(compute_summary_statistics(group_df, label,
                target_method=target_method,
                statistical_power_confidence=statistical_power_confidence,
                statistical_power_ratio=statistical_power_ratio))

    return stats

def compute_summary_statistics_by_zipcode(df, target_method="dailyavg",
        target_error_metric="CVRMSE", target_error_max_value=np.inf,
        statistical_power_confidence=.95, statistical_power_ratio=.05):
    """ Compute summary statistics for a particular dataframe by zipcode.

    Parameters
    ----------
    df : pd.Dataframe
        Contains combined (not yet grouped) output data for all thermostats in
        the sample.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-season inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : list of dict
        Summary statistics for the input dataframe grouped by USPS ZIP code.
    """
    # Map zipcodes to themselves.
    zipcode_dict = { z: z for z in _load_zipcode_to_lat_lng_index().keys()}
    group_spec = ZipcodeGroupSpec(dictionary=zipcode_dict)

    stats = compute_summary_statistics_by_zipcode_group(df, group_spec=group_spec,
            target_method=target_method,
            statistical_power_confidence=statistical_power_confidence,
            statistical_power_ratio=statistical_power_ratio)
    return stats

def compute_summary_statistics_by_weather_station(df, target_method="dailyavg",
        target_error_metric="CVRMSE", target_error_max_value=np.inf,
        statistical_power_confidence=.95, statistical_power_ratio=.05):
    """ Compute summary statistics for a particular dataframe by weather
    weather station used to find outdoor temperature data

    Parameters
    ----------
    df : pd.Dataframe
        Contains combined (not yet grouped) output data for all thermostats in
        the sample.
    target_method : {"dailyavg", "hourlyavg", "deltaT"}, default "dailyavg"
        Metric method by which samples will be filtered according to bad fits, and
        for which statistical power extrapolation is desired.
    target_error_metric : {"MSE", "RMSE", "CVRMSE", "MAE", "MAPE"}, default "CVRMSE"
        Error metric to use when determining thermostat-season inclusion in
        statistics output.
    target_error_max_value : float, default np.inf
        Maximum acceptable value for error metric defined by target_error_metric.
    statistical_power_confidence : float in range 0 to 1, default .95
        Confidence interval to use in estimated statistical power calculation.
    statistical_power_ratio : float in range 0 to 1, default .05
        Ratio of standard error to mean desired in statistical power calculation.

    Returns
    -------
    stats : list of dict
        Summary statistics for the input dataframe grouped by weather station
        used to find outdoor temperature data.
    """
    # Map zipcodes to stations. This is the same mapping used to match outdoor
    # temperature data.
    zipcode_dict = _load_zipcode_to_station_index()
    group_spec = ZipcodeGroupSpec(dictionary=zipcode_dict)

    stats = compute_summary_statistics_by_zipcode_group(df, group_spec=group_spec,
            target_method=target_method,
            statistical_power_confidence=statistical_power_confidence,
            statistical_power_ratio=statistical_power_ratio)
    return stats

def summary_statistics_to_csv(stats, filepath):
    """ Write metric statistics to CSV file.

    Parameters
    ----------
    stats : list of dict
        List of outputs from thermostat.stats.compute_summary_statistics()
    filepath : str
        Filepath at which to save the suppary statistics

    Returns
    -------
    df : pandas.DataFrame
        A pandas dataframe containing the output data.

    """
    quantiles = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    columns = [
        "label",
        "n_seasons_total",
        "n_seasons_kept",
        "n_seasons_discarded",
        "n_enough_statistical_power"
    ]
    for column_name in REAL_OR_INTEGER_VALUED_COLUMNS_ALL:
        columns.append("{}_mean".format(column_name))
        columns.append("{}_sem".format(column_name))
        columns.append("{}_n".format(column_name))
        for quantile in quantiles:
            columns.append("{}_q{}".format(column_name, quantile))

    stats_dataframe = pd.DataFrame(stats, columns=columns)
    stats_dataframe.to_csv(filepath, index=False, columns=columns)
    return stats_dataframe
