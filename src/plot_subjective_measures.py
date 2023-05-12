"""
 * @author Myrthe Tilleman
 * @email metill@utu.fi
 * @create date 2023-05-02 10:50:51
 * @desc Class to analyse the results of the subjective measures,
 plot the results, and calculate the statistics per user, session,
 block, and activity. Saves the results under /user_files/results/.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from scipy.stats import wilcoxon


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
        data = pd.read_excel(self.path + file_name)
        self.confidence = self.average_block(data)

    def load_NASA_TLX(self):
        """ Loads excel file with workload scores and saves it in DataFrame.
        self.nasa_tlx is used for statistical analysis,
        and self.avg_nasa_tlx for plotting.
        """
        file_name = f'{self.user}_NASA_TLX.xlsx'
        self.nasa_tlx = pd.read_excel(self.path + file_name, sheet_name=0)
        self.nasa_tlx['Answer'] = 10 - (self.nasa_tlx['Answer'] / 10)
        self.avg_nasa_tlx = self.average_block(self.nasa_tlx)

    def load_PEmbS_LLA(self):
        """ Loads excel file with embodiment scores and saves it in DataFrame.
        self.pembs_lla is used for statistical analysis,
        and self.avg_pembs_lla for plotting.
        """
        file_name = f'{self.user}_PEmbS-LLA.xlsx'
        self.pembs_lla = pd.read_excel(self.path + file_name, sheet_name=0)
        self.pembs_lla['Answer'] = (self.pembs_lla['Answer'] + 3) / 6 * 10
        self.avg_pembs_lla = self.average_block(self.pembs_lla)

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

    def plot_results(self):
        """ Plots all subjective measures per block in one bar plot.
        Rescales all scores to a range from 0 to 10.
        """
        all_data = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks,
            'Block': np.arange(1, self.num_blocks + 1),
            'Confidence': self.confidence['Answer'],
            'Ease of use': self.avg_nasa_tlx['Answer'],
            'Embodiment': self.avg_pembs_lla['Answer']})

        all_data.plot.bar(
            x='Block', rot=0, yerr=[
                self.confidence['Standard deviation'],
                self.avg_nasa_tlx['Standard deviation'],
                self.avg_pembs_lla['Standard deviation']])
        plt.ylabel('Score; low (0) to high (10)')
        plt.ylim(0, 10)
        plt.xlabel('')
        plt.xticks(np.arange(self.num_blocks), labels=[
            'Baseline', 'EMG before SF', 'EMG + SF', 'EMG after SF'])
        if self.activity == 'Ground level walking':
            title = 'Subjective measures during level ground walking'
        else:
            title = 'Subjective measures during ramp ascension'
        plt.title(title)
        plt.legend(loc='upper right')
        plt.savefig(
            f'user_files/results/{self.user}_Subjective_measures_session_{self.session}_{self.activity}.pdf')

    def calculate_stats(self):
        """ Performs the statistical analysis between all combinations of
        blocks. Saves the results to a csv file.
        """
        block_x, block_y = [], []
        nasa_w, nasa_p = [], []
        pembs_w, pembs_p = [], []
        for block in range(1, self.num_blocks + 1):
            for compare_block in range(block + 1, self.num_blocks + 1):
                block_x.append(block)
                block_y.append(compare_block)

                try:
                    w, p = self.wilcoxon_test(
                        self.nasa_tlx, block, compare_block)
                except ValueError:
                    w, p = np.nan, np.nan
                nasa_w.append(w)
                nasa_p.append(p)

                try:
                    w, p = self.wilcoxon_test(
                        self.nasa_tlx, block, compare_block)
                except ValueError:
                    w, p = np.nan, np.nan
                pembs_w.append(w)
                pembs_p.append(p)

        stats = pd.DataFrame({'Block': block_x, 'Compare block': block_y,
                              'NASA_w': nasa_w, 'NASA_p': nasa_p,
                              'pembs_w': pembs_w, 'pembs_p': pembs_p})
        stats.to_csv(f'user_files/results/{self.user}_Subjective_measures_stats_session_{self.session}_{self.activity}.csv', index=False)

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
        w, p = wilcoxon(x['Answer'], y['Answer'])
        return w, p

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
            for session in range(1, self.max_sessions + 1):
                self.session = session
                for activity in ['Ground level walking', 'Ascending slope']:
                    self.activity = activity
                    self.load_confidence()
                    if self.confidence['Answer'].sum() == 0:
                        # no data found for this session & activity
                        continue
                    self.load_NASA_TLX()
                    self.load_PEmbS_LLA()

                    self.plot_results()
                    self.calculate_stats()


if __name__ == '__main__':
    users = ['U401', 'U412', 'U747']
    plot = AnalyseSubjectiveMeasures()
    plot.analyse_data(users)
