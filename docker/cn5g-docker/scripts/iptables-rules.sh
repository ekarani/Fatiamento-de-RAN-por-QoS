#!/bin/bash

iptables -I FORWARD -p udp --dport 2152 -j NFQUEUE --queue-num 0 
iptables -I FORWARD -p tcp --dport 2152 -j NFQUEUE --queue-num 0 
iptables -I INPUT -p udp --dport 2152 -j NFQUEUE --queue-num 0 
iptables -I INPUT -p tcp --dport 2152 -j NFQUEUE --queue-num 0
iptables -I OUTPUT -p udp --dport 2152 -j NFQUEUE --queue-num 0 
iptables -I OUTPUT -p tcp --dport 2152 -j NFQUEUE --queue-num 0
