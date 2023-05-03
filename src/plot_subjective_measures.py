"""
 * @author Myrthe Tilleman
 * @email metill@utu.fi
 * @create date 2023-05-02 10:50:51
 * @desc Class to plot the subjective measures of a user per block.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class PlotSubjectiveMeasures():
    def __init__(self, user) -> None:
        self.user = user
        self.path = f'user_files/{user}/'
        self.num_blocks = 4

        self.load_confidence()
        self.load_NASA_TLX()
        self.load_PEmbS_LLA()

        self.plot()

    def load_confidence(self):
        """ Loads excel file with confidence scores and saves it in DataFrame.
        """
        file_name = f'{self.user}_Confidence.xlsx'
        data = pd.read_excel(self.path + file_name)
        self.confidence = self.average_block(data)

    def load_NASA_TLX(self):
        """ Loads excel file with workload scores and saves it in DataFrame.
        """
        file_name = f'{self.user}_NASA_TLX.xlsx'
        data = pd.read_excel(self.path + file_name, sheet_name=1)
        self.nasa_tlx = self.average_block(data)

    def load_PEmbS_LLA(self):
        """ Loads excel file with embodiment scores and saves it in DataFrame.
        """
        file_name = f'{self.user}_PEmbS-LLA.xlsx'
        data = pd.read_excel(self.path + file_name, sheet_name=1)
        self.pembs_lla = self.average_block(data)
        self.pembs_lla['Answer'] = (self.pembs_lla['Answer'] + 3) / 6 * 10

    def average_block(self, data):
        """ Calculates the average score for each block.

        Args:
            data (DataFrame): DataFrame with scores for subjective measures.

        Returns:
            DataFrame: DataFrame with average scores for each block.
        """
        average_score = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks,
            'Block': np.arange(1, self.num_blocks + 1),
            'Answer': [np.nan] * self.num_blocks})

        for block in range(1, self.num_blocks + 1):
            block_data = data[data['Block'] == block]
            score = block_data['Answer'].mean()
            average_score.loc[[block - 1], ['Answer']] = score

        print(average_score)
        return average_score

    def plot(self):
        """ Plots all subjective measures per block in one bar plot.
        Rescales all scores to a range from 0 to 10.
        """
        all_data = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks,
            'Block': np.arange(1, self.num_blocks + 1),
            'Confidence': self.confidence['Answer'],
            'Workload': self.nasa_tlx['Answer'] / 10,
            'Embodiment': self.pembs_lla['Answer']})
        print(all_data[['Confidence', 'Workload', 'Embodiment']].pct_change(
            periods=2))

        all_data.plot.bar(x='Block', rot=0)
        plt.ylabel('Score; low (0) to high (10)')
        plt.ylim(0, 10)
        plt.title('Subjective measures throughout one session')
        plt.show()


if __name__ == '__main__':
    user = 'U401'
    plot = PlotSubjectiveMeasures(user)
