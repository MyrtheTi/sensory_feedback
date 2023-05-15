"""
 * @author Myrthe Tilleman
 * @email metill@utu.fi
 * @create date 2023-05-02 10:50:51
 * @desc Class to analyse the results of the subjective measures,
 plot the results, and calculate the statistics per user, session,
 block, and activity. Saves the results under /user_files/results/.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon


class AnalyseSubjectiveMeasures():
    def __init__(self, user='', activity='Ground level walking', session=1):
        self.user = user
        self.path = f'user_files/{self.user}/'

        self.activity = activity
        self.session = session
        self.num_blocks = 4
        self.max_sessions = 3

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
        plt.xlabel('')
        plt.xticks(np.arange(self.num_blocks), labels=[
            'Baseline', 'EMG before SF', 'EMG + SF', 'EMG after SF'])
        if self.activity == 'Ground level walking':
            title = 'Subjective measures during level ground walking'
        else:
            title = 'Subjective measures during ramp ascension'
        plt.title(title)
        plt.legend(loc='upper left', bbox_to_anchor=(1.04, 1))

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
                if p_values['Block'].iloc[index - 1] != row['Block']:
                    h = 0
                if len(p_values) > 0:
                    p_value = row['all_p']
                    if p_value < 0.05:
                        text = '*'
                        if p_value < 0.01:
                            text = '**'
                        elif p_value < 0.001:
                            text = '***'

                        x1 = row['Block'] - 1
                        x2 = row['Compare block'] - 1

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
            DataFrame or list: DataFrame when there is a statistical
            difference between blocks. Otherwise empty list.
        """
        all_data = pd.concat([self.confidence, self.nasa_tlx, self.pembs_lla],
                             ignore_index=True)

        x_all, p_all = self.friedman_test(all_data)

        if p_all <= 0.05:
            pass
        else:
            return []

        x_nasa, p_nasa = self.friedman_test(self.nasa_tlx)
        x_pembs, p_pembs = self.friedman_test(self.pembs_lla)

        friedman = pd.DataFrame({'all_chi': [x_all], 'all_p': [p_all],
                                 'NASA_chi': [x_nasa], 'NASA_p': [p_nasa],
                                 'pembs_chi': [x_pembs], 'pembs_p': [p_pembs]})
        friedman.to_csv(f'user_files/results/{self.user}_Subjective_measures_friedman_session_{self.session}_{self.activity}.csv', index=False)

        if p_nasa <= 0.05 or p_pembs < 0.05 or np.isnan(p_nasa):
            pass
        else:
            return []

        block_x, block_y = [], []
        all_w, all_p = [], []
        nasa_w, nasa_p = [], []
        pembs_w, pembs_p = [], []

        for block in range(1, self.num_blocks + 1):
            for compare_block in range(block + 1, self.num_blocks + 1):
                block_x.append(block)
                block_y.append(compare_block)

                try:
                    w, p = self.wilcoxon_test(
                        all_data, block, compare_block)
                except ValueError:
                    w, p = np.nan, np.nan
                all_w.append(w)
                all_p.append(p)

                try:
                    w, p = self.wilcoxon_test(
                        self.nasa_tlx, block, compare_block)
                except ValueError:
                    w, p = np.nan, np.nan
                nasa_w.append(w)
                nasa_p.append(p)

                try:
                    w, p = self.wilcoxon_test(
                        self.pembs_lla, block, compare_block)
                except ValueError:
                    w, p = np.nan, np.nan
                pembs_w.append(w)
                pembs_p.append(p)

        stats = pd.DataFrame({'Block': block_x, 'Compare block': block_y,
                              'all_w': all_w, 'all_p': all_p,
                              'NASA_w': nasa_w, 'NASA_p': nasa_p,
                              'pembs_w': pembs_w, 'pembs_p': pembs_p})
        stats.to_csv(f'user_files/results/{self.user}_Subjective_measures_wilcoxon_session_{self.session}_{self.activity}.csv', index=False)
        return stats

    def wilcoxon_test(self, data, block, compare_block):
        """ Performs the wilcoxon signed-rank test on the data from block
        against the compare block.

        Args:
            data (DataFrame): DataFrame with all data to test on.
            block (int): Block of first set of measures.
            compare_block (int): Block of second set of measures to compare
            first block against.

        Returns:
            float, float: statistic, and p-value of the wilcoxon test.
        """
        x = data.loc[(data['Block'] == block) & (
            data['Session'] == self.session) & (
            data['Activity'] == self.activity)]
        y = data.loc[(data['Block'] == compare_block) & (
                data['Session'] == self.session) & (
            data['Activity'] == self.activity)]
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
        blocks = data['Block'].unique().tolist()
        block_data = []
        for block in blocks:
            sample = data.loc[(data['Block'] == block) & (
                data['Session'] == self.session) & (
                data['Activity'] == self.activity)]
            if len(sample) > 0:
                block_data.append(sample['Answer'])

        if len(block_data) >= 3:
            chi, p = friedmanchisquare(*block_data)
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

            for session in range(1, self.max_sessions + 1):
                self.session = session
                for activity in ['Ground level walking', 'Ascending slope']:
                    self.activity = activity

                    if self.average_block(self.confidence
                                          )['Answer'].sum() == 0:
                        continue  # skip if no data
                    stats = self.calculate_stats()
                    self.plot_results(stats)


if __name__ == '__main__':
    users = ['U401', 'U412', 'U747']
    plot = AnalyseSubjectiveMeasures()
    plot.analyse_data(users)
