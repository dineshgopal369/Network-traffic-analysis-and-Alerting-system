# Network-Traffic-analysis-and-Alerting-system

This project is to filter network packets from a pcap file using certain criteria such as IP addresses, ports, and protocols, extract relevant information from the filtered packets such as source IP, destination IP, timestamp, packet length, etc., and store this information in a MySQL database for further analysis. The project uses Scapy library for packet manipulation, pybloom_live library for IP filtering using a bloom filter, and Flask to deploy the project.

