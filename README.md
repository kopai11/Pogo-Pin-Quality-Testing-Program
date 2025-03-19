###Project Description

##Project Overview

This project involves developing an automated system for collecting and analyzing pin resistance data using an Arduino-based measurement setup and a Python GUI application. 
The system is designed to test electrical contact resistance, log data, and visualize resistance trends in real-time.

#Arduino-Based Data Collection

Uses an Arduino microcontroller to Collect Resistance values of the compress pin on each stage of compression.
Use Cool-Muscle motor(Cm2) to compress the pin as the desired distance.
Collects data from the Hioki resistance meter and transmits it via serial communication.
Use a micro SD card to collect raw data for future analysis. The data will be collected and saved into SD card according to sensor detection of motor movement and will reset the looping by Home-Position sensor.
Outputs measured resistance values in a structured format (e.g., CSV or text file).


#Graphical User Interface (GUI) for Data Visualization

Built using Python with Tkinter for user interaction.
Provides options to configure test parameters, select data sources, and manage categories.
Implements real-time data visualization using Matplotlib to plot resistance trends.
Supports live monitoring by detecting file updates and refreshing plots dynamically.

#Data Processing and Analysis

Organizes resistance values into different categories based on predefined percentage levels.
Allows users to filter and analyze specific data ranges.
Displays test count trends with adjustable window sizes.

#Live data transmitting from arduino to PC

Use Coolterm software to get live data
