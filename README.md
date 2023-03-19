# Network-Traffic-analysis-and-Alerting-system

This project is an implementation of a network traffic analysis and alerting system using Python and Scapy library. The system filters network packets based on specific IP addresses, ports, and protocols, and saves the relevant packets in a database. It also alerts the system administrator via email if certain conditions are met, such as if a ip is found in a pool of blacklisted ip's or a specific port number or a specific protocol or large packet size is detected.

# Requirements

To use this system, you will need the following:

   Python 3.6 or higher
   Scapy
   Pybloom_live
   Mariadb
   os
   ssl
   Email
   Smtplib
   Logging
   Tabulate

You can install the required packages using pip:

    pip install scapy pybloom_live mariadb email os ssl smtplib logging tabulate

# Usage

To use this system, follow these steps:

  Clone or download the project from GitHub.
     
     $ git clone https://github.com/dineshgopal369/Network-traffic-analysis-and-Alerting-system

  Open a terminal window and navigate to the project directory.
     
     $ cd Network-traffic-analysis-and-Alerting-system
     
  Run the traffic_analysis.py script using the command

     $ python traffic-analysis.py
     

