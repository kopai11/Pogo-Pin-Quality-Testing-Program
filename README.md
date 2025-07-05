##Project Overview

This project presents a comprehensive automated system designed for evaluating the resistance of contact pins during controlled mechanical compression. The solution is developed for R&D use, where both electrical performance and mechanical durability need to be studied under customizable test conditions.
The system architecture consists of three main components:
 1.Cool Muscle CM2 Motor,
 2.Arduino-based control unit, and
 3.Python-based desktop application.

The Cool Muscle motor is configured and controlled via CoolWorks Lite software to execute precise pin compression sequences. Once the motor reaches specific compression heights, it sends a signal to the Arduino, which then coordinates all measurement and logging tasks within the system.
The Arduino microcontroller functions as the central logic controller and performs the following actions in response to signals from the motor:
 - Trigger the Hioki resistance meter to collect accurate resistance values at defined compression points.
 - Allow current to pass through the contact pin using a relay-controlled circuit, enabling resistance testing under real electrical load conditions. The current level is user-defined and adjustable to meet R&D requirements.
 - Log all resistance data to a micro SD card in structured formats (CSV or TXT) for traceability and future analysis.
 - Monitor sensors such as compression detection and home-position switches to manage repeatable test cycles and ensure reliable operation.
 - Coordinate all functions in a unified electrical circuit where motor control, current passage, and resistance testing operate seamlessly without interfering with each other.
All measured and logged data is also transmitted to a Python-based desktop application for real-time monitoring, data visualization, and session management, ensuring a smooth and user-friendly testing workflow.

On the software side, a Python GUI application (built with Tkinter, PySerial, and Matplotlib) allows users to configure test conditions, monitor live data, and visualize resistance trends in real time. Key features include:
 - Real-time plotting of resistance values.
 - Categorization of data based on percentage thresholds.
 - Session management with automatic/manual saving.
 - Data filtering and analysis tools.
 - Compatibility with serial live monitoring tools like CoolTerm(link: https://freeware.the-meiers.org/)
This integrated system enables consistent, repeatable, and traceable testing of contact pins under both mechanical stress and electrical load. It bridges hardware precision with software flexibility, supporting both automated data acquisition and advanced visualization for technical analysis and decision-making in R&D environments.

