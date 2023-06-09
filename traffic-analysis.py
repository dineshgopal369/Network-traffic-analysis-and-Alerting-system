from flask import Flask, jsonify,request, render_template
from scapy.all import *
import pybloom_live
import mariadb
import datetime
import os
import ssl
from email.message import EmailMessage
import smtplib
import logging
from tabulate import tabulate
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter_packets', methods=['POST'])
def filter_packets_route():
    # read request data
    #data = request.get_json()
    pcap_file = request.files['pcap_file']
    # add or remove necessary values in the ip_list,port_list,protocols_list
    ip_list = ["208.82.236.129", "192.168.3.131", "72.13.214.147","192.168.3.132","208.82.236.130","72.13.236.158","209.92.237.131","192.168.5.12","210.82.43.12","72.18.125.67"]
    port_list = [80,443,8080,23]
    protocols_list=["Ethernet"," BitTorrent","JXTA"," Jabber","Telnet","Tcp"]

    # filter packets
    filtered_packets = filter_packets(pcap_file, ip_list, port_list, protocols_list)
    unique_packets = list(set(filtered_packets))
    # insert packets to database
    p=insert_packets_to_database(unique_packets)
    print(p)
    return p

def filter_packets(pcap_file, ip_list, port_list,protocols_list):
    try:
        #bloom filter for IP filtering
        bf = pybloom_live.BloomFilter(capacity=10000, error_rate=0.001)
        # add the IPs in the list to the bloom filter
        for ip in ip_list:
            bf.add(ip)
        # List for storing filtered packets
        filtered_packets = []
        # iterate over the packets in the pcap file
        port_set = set(port_list)
        for packet in rdpcap(pcap_file):
            # filter packets based on IP or port
            if packet.haslayer(IP):
                try:
                    # filter packets based on IP or port
                    if packet.haslayer(IP):
                        if packet[IP].src in bf or packet[IP].dst in bf:
                            filtered_packets.append(extract_packet_info(packet))
                        elif packet.haslayer(TCP) and (packet[TCP].sport in port_set or packet[TCP].dport in port_set):
                            filtered_packets.append(extract_packet_info(packet))
                        elif packet.haslayer(UDP) and (packet[UDP].sport in port_set or packet[UDP].dport in port_set):
                            filtered_packets.append(extract_packet_info(packet))
                        elif any(packet.haslayer(protocol) for protocol in protocols_list):
                            filtered_packets.append(extract_packet_info(packet))
                        elif len(packet) >=1518:
                            filtered_packets.append(extract_packet_info(packet))
                except Exception as e:
                    logging.error("Error extracting packet information: %s", e)
                    logging.debug(traceback.format_exc())
        return list(set(filtered_packets))
    except Exception as e:
        logging.error("An error occurred while filtering packets: %s", e)
        logging.debug(traceback.format_exc())
        return []

def extract_packet_info(packet):
    try:
        # extracting the required information from the packets
        port_to_protocol = {21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3', 123: 'NTP', 143: 'IMAP', 161: 'SNMP', 443: 'HTTPS', 465: 'SMTPS', 587: 'SMTP', 993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL', 1521: 'Oracle', 2049: 'NFS', 3128: 'Squid', 3306: 'MySQL', 5432: 'PostgreSQL', 5900: 'VNC', 6000: 'X11', 6379: 'Redis', 7001: 'MongoDB', 8080: 'HTTP-Proxy', 8081: 'HTTP-Proxy', 8090: 'HTTP-Proxy', 8443: 'HTTPS', 8888: 'HTTP-Proxy'}
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        trans_layer = "TCP" if packet.haslayer(TCP) else "UDP" if packet.haslayer(UDP) else "None"
        src_port = packet[TCP].sport if trans_layer == "TCP" else packet[UDP].sport if trans_layer == "UDP" else None
        dst_port = packet[TCP].dport if trans_layer == "TCP" else packet[UDP].dport if trans_layer == "UDP" else None
        protocol = port_to_protocol.get(src_port) or port_to_protocol.get(dst_port) or "Unknown"
        packet_len=len(packet)
        #timestamp = packet.time
        date = packet.time
        dt = datetime.datetime.fromtimestamp(int(date))
        # Convert the datetime object to a string in the desired format
        timestamp = str(dt.strftime('%Y-%m-%d %H:%M:%S'))
        return (src_ip, dst_ip,trans_layer,src_port, dst_port,protocol,timestamp,packet_len)
    except Exception as e:
        logging.error("Error extracting packet information: %s", e)
        logging.debug(traceback.format_exc())
        return None

def insert_packets_to_database(filtered_packets):
    try:
        # create a connection to the database
        with mariadb.connect(
            user="xxxxxxx",
            password="xxxxxxx",
            host="127.0.0.1",
            port=3306,
            database="packet_analysis_db"
        ) as connection:
            # create a cursor for executing database queries
            with connection.cursor() as cursor:
                # use a prepared statement for efficient insertion
                insert_query = "INSERT INTO packet_data(src_ip,dst_ip,trans_layer,src_port,dst_port,protocol,timestamp,packet_len) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                # check if there are any records in the table
                cursor.execute("SELECT COUNT(*) FROM packet_data")
                result = cursor.fetchone()
                if result[0] == 0:
                    # if the database is empty, insert all packets without checking for duplicates
                    cursor.executemany(insert_query, filtered_packets)
                    connection.commit()
                else:
                    # if the database is not empty, insert packets in batches
                    batch_size = 1000
                    for i in range(0, len(filtered_packets), batch_size):
                        batch = filtered_packets[i:i+batch_size]
                        values = []
                        for packet in batch:
                            # check if each packet already exists in the database before adding to batch
                            select_query = "SELECT * FROM packet_data WHERE src_ip=%s AND dst_ip=%s AND trans_layer=%s AND src_port=%s AND dst_port=%s AND protocol=%s AND timestamp=%s AND packet_len=%s"
                            cursor.execute(select_query, packet)
                            if cursor.fetchone() is None:
                                values.append(packet)
                        # insert batch of unique packets into the database
                    if values:
                        cursor.executemany(insert_query, values)
                        connection.commit()
                            # execute the query to get packet statistics
                        query = """
                            SELECT 
                                src_ip,
                                COUNT(*) AS num_occurrences,
                                COUNT(DISTINCT dst_ip) AS num_distinct_dst_ips,
                                COUNT(DISTINCT dst_port) AS num_distinct_dst_ports,
                                COUNT(DISTINCT protocol) AS num_distinct_protocols,
                                SUM(CASE WHEN packet_len > 1518 THEN 1 ELSE 0 END) AS num_packets_gt_1518
                            FROM packet_data
                            GROUP BY src_ip
                            ORDER BY num_occurrences DESC;

                        """
                        cursor.execute(query)
                        results = cursor.fetchall()

                        # format the query results as a table for the email alert
                        table_headers = ["Source IP", "Occurrences", "Distinct Dest IPs", "Distinct Protocols", "Max Packet Length"]
                        table_rows = []
                        for result in results:
                            table_rows.append([result[0], result[1], result[2], result[3], result[4]])
                        alert_text = "<h1>Packet Analysis Results:</h1>"
                        alert_text += f"<div style='background-color: #f2f2f2;padding: 20px;border-radius: 10px;'>"
                        alert_text += tabulate(table_rows, headers=table_headers, tablefmt='html')
                        alert_text += "</div>"

                        
                        # send the email alert
                        message = EmailMessage()
                        message['Subject'] = 'Packet Analysis Alert'
                        message['From'] = 'xxxxxxxxxx@gmail.com'
                        message['To'] = 'xxxxxxxxxx@gmail.com'
                        #message.set_content(alert_text)
                        message.set_content("This email requires an HTML-capable email client", subtype='html')
                        message.add_alternative(alert_text, subtype='html')
                        context=ssl.create_default_context()
                        smtp_server = 'smtp.gmail.com'
                        smtp_port = 465
                        smtp_username = 'xxxxxxxxxx3@gmail.com'
                        smtp_password = 'xxxxxxxxxxxx'

                        with smtplib.SMTP_SSL(smtp_server, smtp_port,context=context) as server:
                            server.login(smtp_username, smtp_password)
                            #server.sendmail(message['From'], message['To'], message.as_string())
                            server.send_message(message)
                        print("Alert sent!")
            print(alert_text)
            return alert_text
    except mariadb.Error as e:
        logging.error(f"Error connecting to database: {e}")
        raise
    except Exception as e:
        logging.error(f"Error sending email alert: {e}")
        raise


if __name__ == '__main__':
    app.run()
