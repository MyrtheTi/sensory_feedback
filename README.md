# Sensory feedback for EMG control

Author: Myrthe Tilleman, contact through email: [mtillerman@ossur.com](mailto:mtillerman@ossur.com) or [metill@utu.fi](mailto:metill@utu.fi).

This repository contains all the code for my Master Thesis in Human Neuroscience.
This project is a collaboration of the University of Turku and Össur, Iceland.
The goal of this project is to provide sensory feedback to persons with a leg amputation and EMG controlled prosthetic devices.
This work contributes towards bidirectional prosthetics.
The thesis paper can be found through the library of the University of Turku.

## Materials

For this project, I used a standard laptop (Lenovo ThinkPad P53s),
a microprocessor
([Seeed Studio XIAO nRF52840 Sense, Seeed Technology Co., Ltd, China](https://www.seeedstudio.com/Seeed-XIAO-BLE-Sense-nRF52840-p-5253.html)),
seven 9mm vibrators (307-103, Precision Microdrives Limited, United Kingdom),
and the prosthetic intent control system (PICS) designed by Össur to collect, amplify, and preprocess EMG data.

## Requirements

All code on the laptop is written in Python 3.10.8 and the following libraries and their versions are used in this project:

- Numpy 1.23.5
- Pandas 1.5.2
- Matplotlib 3.6.2
- scikit-learn 1.2.1
- mpl_point_clicker 0.3.1
- mpl-interactions 0.22.1
- openpyxl 3.0.10
- tikzplotlib 0.10.1

The code on the microprocessor is written in CircuitPython 8.0.5, with the following libraries installed:

- asyncio 0.5.19
- adafruit_ticks 1.0.9

CircuitPython can be installed by following the
[Adafruit tutorial](https://learn.adafruit.com/welcome-to-circuitpython).
Libraries can be added manually from the [library bundles](https://circuitpython.org/libraries)
or using [circup](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/overview) 1.2.1.

## Files on the microprocessor

In order to write code on the microprocessor,
connect the laptop to the microprocessor through a data USB-cable.

The following files are uploaded to the microprocessor:

- [activate_vibration_motor.py](src/activate_vibration_motors.py)
- [preprocessing.py](src/preprocessing.py)
- [read_uart.py](src/read_uart.py)
- [utils.py](src/utils.py)
- [booty.py](src/booty.py)

Any file can be run directly by copying the code to `code.py`.
The main file for the online feedback is [run.py](src/run.py) and this is run from `code.py`.
The other files are run from the laptop.

## Changing write access

For some files, the microprocessor needs write access to save data in files.
This access can be given to the microprocessor by changing the file name of
[booty.py](src/booty.py) to `boot.py`.
Then, a hard reset is required to take this change into effect.
The microprocessor can be reset by unplugging and reinserting the USB cable.
To give the write access back to the USB, change the name back by writing the following lines in the REPL:

```python
import os
os.rename('/boot.py', '/booty.py') 
```

Then reset the microprocessor.
Write access is necessary to successfully run the following files in `code.py` on the microprocessor:

- [stimulation_calibration](src/stimulation_calibration.py)
- [stimulation_validation](src/stimulation_validation.py)

## Calibrating the system

Before the actual calibration, make sure a folder exists for the user under
[user_files](/user_files/) both on the laptop and the microprocessor.
Then, create a folder with the current date for the corresponding user in the format year_month_day.

### EMG calibration

For the EMG recording, don the custom made liner and socket correctly and connect to the PICS through the Össur Toolbox.
Record about 10 to 12 seconds of rest activity and save this log in `rest.csv`.
Then ask the user to contract their extensor muscle 3 times for a few seconds with rest in between.
Save this log in `extend.csv`.
Repeat this process for the flexor muscle and save the file in `flex.csv`.

Before running the EMG_calibration, make sure all files are saved in the folder that corresponds to the user and the date.
Then run [EMG_calibration.py](src/EMG_calibration.py) on laptop to create rest_activity and mvc files.
Finally, copy these files to the correct folder on the microprocessor.

### Feedback calibration

First, a file needs to be created with the vibration duration for each level.
When a standard vibration duration is used, this file can be copied from other users.
Otherwise, it can be created by running [stimulation_calibration](src/stimulation_calibration.py)
on the microprocessor.
When using this method, make sure the microprocessor has write permissions,
see [changing write access](#changing-write-access).

For familiarisation of the motors run [activate_vibration_motors.py](src/activate_vibration_motors.py)
in `code.py` to loop through motors with set vibration strength in the previous step.
When the vibrations are too strong or too weak,
the duration can be adapted and the familiarisation can be repeated until the user is comfortable with the vibrations strength.

Then, a reinforcement learning and a validation session is performed.
For these sessions, [stimulation_validation](src/stimulation_validation.py) is used.
Before running this code, make sure the microprocessor has write permissions.
For these session, ask the user to report back which level was activated.
During the familiarisation session, confirm the correct level with the user.
During the validation session,
the user is given a forced-choice and write the user's predicted level in the REPL.

The validation accuracy is printed at the end of the session.
If accuracy is high enough, the user is ready for online feedback, otherwise, repeat the process.
For a more detailed view of the results,
a confusion matrix can be plotted with [plot_results.py](src/plot_results.py)
on the laptop when the files with the true and predicted labels have been copied to the laptop.

## Using the online system

To use the online system, [run.py](src/run.py) is copied to `code.py`.
Make sure the right user and date is used in the input and that all calibration files exist.
Then, the system can be disconnected from the laptop and used until the battery runs out.
