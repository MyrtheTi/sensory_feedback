"""
 * @author Myrthe Tilleman
 * @email metill@utu.fi
 * @create date 2023-05-02 10:50:51
 * @desc Class to analyse the results of the subjective measures,
 plot the results, and calculate the statistics per user, session,
 block, and activity. Saves the results under /user_files/results/.
"""

from math import factorial

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon


class AnalyseSubjectiveMeasures():
    def __init__(self, user='', activity='Ground level walking', session=1):
        self.user = user
        self.path = f'user_files/{self.user}/'

        self.activity = activity
        self.activities = ['Ground level walking', 'Ascending slope']
        self.session = session
        self.num_blocks = 4
        self.max_sessions = 3
        self.elements = 2

    def calculate_max_combinations(self, number):
        """ Calculate the number of maximum combinations, this is the maximum
        number of statistical tests performed and used for a Bonferroni
        correction of the alpha value.

        Args:
            number (int): Number of elements of which all possible combinations
            when the number of self.elements are taken.
        """
        self.max_combinations = int(factorial(number) / (
            factorial(self.elements) * factorial(number - self.elements)))

    def load_confidence(self):
        """ Loads excel file with confidence scores and saves it in DataFrame.
        """
        file_name = f'{self.user}_Confidence.xlsx'
        self.confidence = pd.read_excel(self.path + file_name)
        self.confidence.dropna(inplace=True, subset=['Answer'])

    def load_NASA_TLX(self):
        """ Loads excel file with workload scores and saves it in DataFrame.
        self.nasa_tlx is used for statistical analysis,
        and self.avg_nasa_tlx for plotting.
        """
        file_name = f'{self.user}_NASA_TLX.xlsx'
        self.nasa_tlx = pd.read_excel(self.path + file_name, sheet_name=0)
        self.nasa_tlx['Answer'] = 10 - (self.nasa_tlx['Answer'] / 10)
        self.nasa_tlx.dropna(inplace=True, subset=['Answer'])

    def load_PEmbS_LLA(self):
        """ Loads excel file with embodiment scores and saves it in DataFrame.
        self.pembs_lla is used for statistical analysis,
        and self.avg_pembs_lla for plotting.
        """
        file_name = f'{self.user}_PEmbS-LLA.xlsx'
        self.pembs_lla = pd.read_excel(self.path + file_name, sheet_name=0)
        self.pembs_lla['Answer'] = (self.pembs_lla['Answer'] + 3) / 6 * 10
        self.pembs_lla.dropna(inplace=True, subset=['Answer'])

    def average_block(self, data):
        """ Calculates the average score for each block, for the set activity
        and session.

        Args:
            data (DataFrame): DataFrame with scores for subjective measures.

        Returns:
            DataFrame: DataFrame with average scores for each block.
        """
        average_score = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks,
            'Block': np.arange(1, self.num_blocks + 1),
            'Answer': [np.nan] * self.num_blocks,
            'Standard deviation': [np.nan] * self.num_blocks})

        for block in range(1, self.num_blocks + 1):
            block_data = data[(
                data['Block'] == block) & (
                data['Session'] == self.session) & (
                data['Activity'] == self.activity)]
            score = block_data['Answer'].mean()
            std = block_data['Answer'].std()
            average_score.loc[[block - 1], ['Answer']] = score
            average_score.loc[[block - 1], ['Standard deviation']] = std

        average_score.fillna(0, inplace=True)
        return average_score

    def plot_results(self, p_values=[]):
        """ Plots all subjective measures per block in one bar plot.
        Rescales all scores to a range from 0 to 10. Plots horizontal
        bars with asterisks to indicate statistical difference.

        Args:
            p_values (DataFrame): DataFrame with p_values of statistical
            difference between blocks. Defaults to [].
        """
        avg_confidence = self.average_block(self.confidence)
        avg_nasa = self.average_block(self.nasa_tlx)
        avg_pembs = self.average_block(self.pembs_lla)

        all_data = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks,
            'Block': np.arange(1, self.num_blocks + 1),
            'Confidence': avg_confidence['Answer'],
            'Ease of use': avg_nasa['Answer'],
            'Embodiment': avg_pembs['Answer']})

        standard_dev = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks,
            'Block': np.arange(1, self.num_blocks + 1),
            'Confidence': avg_confidence['Standard deviation'],
            'Ease of use': avg_nasa['Standard deviation'],
            'Embodiment': avg_pembs['Standard deviation']})

        if all_data['Confidence'].sum() == 0:
            return  # nothing to plot

        all_data.plot.bar(
            x='Block', rot=0, yerr=standard_dev[
                ['Confidence', 'Ease of use', 'Embodiment']].to_numpy().T)
        plt.ylabel('Score; low (0) to high (10)')
        plt.yticks(np.arange(11))
        plt.ylim(0, 12.5)
        # plt.text(1.95, 9, '+')  # plus mark for outlier
        plt.xlabel('')
        plt.xticks(np.arange(self.num_blocks), labels=[
            'Baseline', 'EMG before SF', 'EMG + SF', 'EMG after SF'])
        if self.activity == 'Ground level walking':
            title = 'Subjective measures during level ground walking'
        else:
            title = 'Subjective measures during ramp ascension'
        plt.title(title)
        plt.legend(bbox_to_anchor=(0, -0.05), loc="upper left",
                   ncol=3)
        above_y = 0.2
        y_max_values = []
        for index, row in all_data.iterrows():
            # plot horizontal line above bars
            x1, x2 = row['Block'] - 1.3, row['Block'] - 0.7
            y = row + standard_dev.iloc[index]
            y_max = y[['Confidence', 'Ease of use', 'Embodiment']
                      ].max().max() + above_y
            y_max_values.append(y_max + above_y)
            if y_max == 0.2:
                continue
            plt.plot([x1, x1, x2, x2],
                     [y_max, y_max + above_y, y_max + above_y, y_max],
                     lw=1., c='black')

        h = 0
        if len(p_values) > 0:
            # plot horizontal lines that indicate significant differences
            for index, row in p_values.iterrows():
                if p_values['Condition_1'].iloc[index - 1] != row['Condition_1']:
                    h = 0
                if len(p_values) > 0:
                    p_value = row['all_p']
                    if p_value < (0.05 / self.max_combinations):
                        # bonferroni correction
                        text = '*'
                        # if p_value < 0.01:
                        #     text = '**'
                        if p_value < 0.001:
                            text = '**'

                        x1 = row['Condition_1'] - 1
                        x2 = row['Condition_2'] - 1

                        # statistical annotation
                        h += 0.6
                        y1, y2 = y_max_values[int(x1)], y_max_values[int(x2)]
                        y = max(y1, y2) + h
                        plt.plot([x1, x1, x2, x2],
                                 [y, y + above_y, y + above_y, y],
                                 lw=1., c='black')
                        plt.text((x1 + x2) * .5, y+above_y, text, ha='center',
                                 va='bottom', c='black')

        plt.savefig(
            f'user_files/results/{self.user}_Subjective_measures_session_{self.session}_{self.activity}.pdf',
            bbox_inches="tight")

    def calculate_stats(self):
        """ Performs the statistical analysis between all combinations of
        blocks. Saves the results to a csv file.

        Returns:
            list : contains the results of the friedman tests.
            DataFrame: DataFrame with statistical difference between blocks,
            otherwise empty.
        """
        all_data = pd.concat([self.confidence, self.nasa_tlx, self.pembs_lla],
                             ignore_index=True)

        x_all, p_all = self.friedman_test(all_data)

        x_nasa, p_nasa = self.friedman_test(self.nasa_tlx)
        x_pembs, p_pembs = self.friedman_test(self.pembs_lla)

        if self.compare_sessions:
            condition = self.block
        else:
            condition = self.session

        friedman = [self.activity, condition, x_all, p_all,
                    x_nasa, p_nasa, x_pembs, p_pembs]

        if p_nasa <= 0.05 or p_pembs < 0.05 or np.isnan(p_nasa):
            return friedman, self.wilcoxon_compare_sample(all_data)
        else:
            return friedman, pd.DataFrame()

    def wilcoxon_compare_sample(self, all_data):
        """ Prepares the data for the wilcoxon test to compare within session
        and between sessions. After the statistical tests, the results are
        saved in a DataFrame.

        Args:
            all_data (DataFrame): Contains all data of the subjective measures.

        Returns:
            DataFrame: Results of the test used for indicating significant
            differences in plot.
        """
        x, y = [], []
        all_w, all_p = [], []
        nasa_w, nasa_p = [], []
        pembs_w, pembs_p = [], []

        if self.compare_sessions:
            sample_range = all_data['Session'].unique().tolist()
            compare = 'Block'
            condition = self.block
        else:
            sample_range = all_data['Block'].unique().tolist()
            compare = 'Session'
            condition = self.session

        for condition_1 in sample_range:
            for condition_2 in sample_range[condition_1:]:
                x.append(condition_1)
                y.append(condition_2)

                try:
                    w, p = self.wilcoxon_test(
                        all_data, condition_1, condition_2)
                except ValueError:
                    w, p = np.nan, np.nan
                all_w.append(w)
                all_p.append(p)

                try:
                    w, p = self.wilcoxon_test(
                        self.nasa_tlx, condition_1, condition_2)
                except ValueError:
                    w, p = np.nan, np.nan
                nasa_w.append(w)
                nasa_p.append(p)

                try:
                    w, p = self.wilcoxon_test(
                        self.pembs_lla, condition_1, condition_2)
                except ValueError:
                    w, p = np.nan, np.nan
                pembs_w.append(w)
                pembs_p.append(p)

        stats = pd.DataFrame({
            'Activity': [self.activity] * self.max_combinations,
            compare: [condition] * self.max_combinations,
            'Condition_1': x, 'Condition_2': y,
            'all_w': all_w, 'all_p': all_p,
            'NASA_w': nasa_w, 'NASA_p': nasa_p,
            'pembs_w': pembs_w, 'pembs_p': pembs_p})

        return stats

    def wilcoxon_test(self, data, condition_1, condition_2):
        """ Performs the wilcoxon signed-rank test on the data from block
        against the compare block.

        Args:
            data (DataFrame): DataFrame with all data to test on.
            condition_1 (int): Block or session of first set of measures.
            condition_2 (int): Block or session of second set of measures to
            compare first block against.

        Returns:
            float, float: statistic, and p-value of the wilcoxon test.
        """
        if self.compare_sessions:
            self.session = condition_1
        else:
            self.block = condition_1

        x = self.select_sample(data)

        if self.compare_sessions:
            self.session = condition_2
        else:
            self.block = condition_2
        y = self.select_sample(data)

        w, p = wilcoxon(x['Answer'], y['Answer'], mode='exact')
        return w, p

    def friedman_test(self, data):
        """ Performs the friedman test on the groups.

        Args:
            data (DataFrame): DataFrame to test difference between blocks.

        Returns:
            float, float: statistic, and p-value result from the statistical
            test, otherwise np.nan, np.nan.
        """
        compare_data = []

        if self.compare_sessions:
            sessions = data['Session'].unique().tolist()
            for session in sessions:
                self.session = session
                sample = self.select_sample(data)
                if len(sample) > 0:
                    compare_data.append(sample['Answer'])
        else:
            blocks = data['Block'].unique().tolist()
            for block in blocks:
                self.block = block
                sample = self.select_sample(data)
                if len(sample) > 0:
                    compare_data.append(sample['Answer'])

        if len(compare_data) >= 3:
            chi, p = friedmanchisquare(*compare_data)
        else:
            chi, p = np.nan, np.nan
        return chi, p

    def analyse_data(self, users):
        """ Loops through user list to load the data for each user.
        Then analyses the data per session and activity. Plots the results
        and calculate the statistics. Then saves the results.

        Args:
            users (list): List of user IDs as string
        """
        for user in users:
            self.user = user
            self.path = f'user_files/{user}/'
            self.load_confidence()
            self.load_NASA_TLX()
            self.load_PEmbS_LLA()

            friedman_within_session_file = f'user_files/results/{self.user}_Subjective_measures_friedman_within_session.csv'
            friedman_within_session_list = []
            friedman_between_session_file = f'user_files/results/{self.user}_Subjective_measures_friedman_between_session.csv'
            friedman_between_session_list = []

            wilcoxon_within_session_file = f'user_files/results/{self.user}_Subjective_measures_wilcoxon_within_session.csv'
            wilcoxon_within_session_df = pd.DataFrame()
            wilcoxon_between_session_file = f'user_files/results/{self.user}_Subjective_measures_wilcoxon_between_session.csv'
            wilcoxon_between_session_df = pd.DataFrame()

            for activity in self.activities:
                self.activity = activity

                # test within sessions
                self.compare_sessions = False
                self.calculate_max_combinations(self.num_blocks)

                for session in range(1, self.max_sessions + 1):
                    self.session = session

                    if self.average_block(self.confidence
                                          )['Answer'].sum() == 0:
                        continue  # skip if no data
                    friedman, wilcoxon_stats = self.calculate_stats()
                    friedman_within_session_list.append(friedman)
                    if wilcoxon_within_session_df.empty:
                        wilcoxon_within_session_df = wilcoxon_stats
                    else:
                        wilcoxon_within_session_df = pd.concat([
                            wilcoxon_within_session_df, wilcoxon_stats],
                            ignore_index=True)
                    self.plot_results(wilcoxon_stats)

                # compare sessions
                self.compare_sessions = True
                self.calculate_max_combinations(self.max_sessions)
                for block in range(1, self.num_blocks + 1):
                    self.block = block

                    if self.average_block(self.confidence
                                          )['Answer'].sum() == 0:
                        continue  # skip if no data
                    friedman, wilcoxon_stats = self.calculate_stats()
                    friedman_between_session_list.append(friedman)
                    if wilcoxon_between_session_df.empty:
                        wilcoxon_between_session_df = wilcoxon_stats
                    else:
                        wilcoxon_between_session_df = pd.concat([
                            wilcoxon_between_session_df, wilcoxon_stats],
                            ignore_index=True)

            # save all in csv files
            friedman_within_session_df = pd.DataFrame(
                friedman_within_session_list,
                columns=['Activity', 'Session', 'all_chi', 'all_p',
                         'NASA_chi', 'NASA_p', 'pembs_chi', 'pembs_p'])
            if not friedman_within_session_df.empty:  # save when not empty
                friedman_within_session_df.to_csv(
                    friedman_within_session_file, index=False)
            if not wilcoxon_within_session_df.empty:
                wilcoxon_within_session_df.to_csv(
                    wilcoxon_within_session_file, index=False)

            friedman_between_session_df = pd.DataFrame(
                friedman_between_session_list,
                columns=['Activity', 'Block', 'all_chi', 'all_p',
                         'NASA_chi', 'NASA_p', 'pembs_chi', 'pembs_p'])
            if not friedman_between_session_df.empty:
                friedman_between_session_df.to_csv(
                    friedman_between_session_file, index=False)
            if not wilcoxon_between_session_df.empty:
                wilcoxon_between_session_df.to_csv(
                    wilcoxon_between_session_file, index=False)

    def select_sample(self, data):
        """ Select a sample of the data based on the defined parameters.

        Args:
            data (DataFrame): DF from which to select a specific portion.

        Returns:
            DataFrame : Selected data of the defined block, session, and
            activity.
        """
        sample = data.loc[(data['Block'] == self.block) & (
            data['Session'] == self.session) & (
            data['Activity'] == self.activity)]
        return sample


if __name__ == '__main__':
    users = ['U401', 'U412', 'U747']
    plot = AnalyseSubjectiveMeasures()
    plot.analyse_data(users)
