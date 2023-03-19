# Network-Traffic-analysis-and-Alerting-system

This project is an implementation of a network traffic analysis and alerting system using Python and Scapy library. The system filters network packets based on specific IP addresses, ports, and protocols, and saves the relevant packets in a database. It also alerts the system administrator via email if certain conditions are met, such as if a ip is found in a pool of blacklisted ip's or a specific port number or a specific protocol or large packet size is detected.

# Requirements

To use this system, you will need the following:

  Python 3.6 or higher
  Scapy
  Pybloom_live
  Mariadb
  Email
  Smtplib
  Logging
  Tabulate

You can install the required packages using pip:

    pip install scapy pybloom_live mariadb email smtplib logging tabulate

# Usage

To use this system, follow these steps:

     Clone or download the project from GitHub.
     $ git clone https://github.com/dineshgopal369/Network-traffic-analysis-and-Alerting-system

     Open a terminal window and navigate to the project directory.
     $ cd Network-traffic-analysis-and-Alerting-system

     Run the traffic_analysis.py script using the command python traffic_analysis.py. This script will read the network traffic from a PCAP file and filter      packets based on specific IP addresses, ports, and protocols. The filtered packets will then be extracted and saved to a database.

    The system will send an email alert to the specified recipient if any of the following conditions are met:
          A packet with its source or destination ip in the pool of blacklisted ip's.
          A packet with a port number specified in the port_list variable is detected.
          A packet with a protocol specified in the protocol_list variable is detected.
          A packet with a size greater than or equal to 1518 bytes is detected.

