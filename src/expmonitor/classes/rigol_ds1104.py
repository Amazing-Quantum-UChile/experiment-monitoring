#!/usr/bin/env python
# -*- mode:Python; coding: utf-8 -*-

# ----------------------------------
# Created on the Thu Mar 05 2026 by Victor
#
# Copyright (c) 2026 - AmazingQuantum@UChile
# ----------------------------------
#
'''
Content of rigol_ds1104.py

Please document your code ;-).

'''

import socket

# On tente de se glisser par la porte dérobée (Port 5555)
def sneak_peek():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0) # Timeout très court
        s.connect(("172.17.55.119", 5555))
        s.sendall(b"*IDN?\n")
        print("Réponse :", s.recv(1024).decode())
        s.close()
    except:
        print("Accès refusé : Le PC Windows bloque tout.")

sneak_peek()