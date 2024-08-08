#!/usr/bin/env python3

import asyncio
import functools
import logging
import sys
import time
import re
import scapy.all as scapy
import netfilterqueue
import threading

last_packet_time = {}
packet_lock = threading.Lock()

global pattern
pattern = re.compile(r'0c0101(..)')

class NFQueue3(object):
    def __init__(self, queue, cb, *cb_args, **cb_kwargs):
        self.logger = logging.getLogger('NFQueue3#{}'.format(queue))
        self.logger.info('Bind queue #{}'.format(queue))
        self._loop = asyncio.get_event_loop()
        self.queue = queue
        self.counter = 0
        self._nfqueue = netfilterqueue.NetfilterQueue()
        self.cb = cb
        self.cb_args = cb_args
        self.cb_kwargs = cb_kwargs
        self._nfqueue.bind(self.queue, self._nfcallback)
        self._nfqueue_fd = self._nfqueue.get_fd()
        cb2 = functools.partial(self._nfqueue.run, block=False)
        self._loop.add_reader(self._nfqueue_fd, cb2)

    def _nfcallback(self, pkt):
        pkt.retain()
        threading.Thread(target=self.handle_packet, args=(pkt,)).start()

    def handle_packet(self, pkt):
        global last_packet_time, pattern
        current_time = time.time()
        self.counter += 1

        data = pkt.get_payload()
        self.logger.debug('Received ({} bytes): {}'.format(len(data), data))
        
        pkt_scapy = scapy.IP(data)
        
        hex_str = data.hex()
        match = pattern.search(hex_str)
        
        if match:
            ue_value = int(match.group(1), 16)
            if ue_value == 2: #transformar em parâmetro
                ue_ip = pkt_scapy.src
                # target_delay é um número mágico
                target_delay = 8 * 1500 / 1e6 #transformar em parâmetro
                elapsed_time = current_time - last_packet_time.get(ue_ip, 0)
                with packet_lock:
                    if elapsed_time < target_delay:
                        delay = target_delay - elapsed_time
                        self.logger.info(f"Applying delay of {delay:.6f} seconds to packet from {ue_ip}")
                        time.sleep(delay)
                    last_packet_time[ue_ip] = time.time()
        
        pkt.accept()  # Aceitar pacotes imediatamente que não correspondem ao ue_value 2

    def set_callback(self, cb, *cb_args, **cb_kwargs):
        self.logger.info('Set callback to {}'.format(cb))
        self.cb = cb
        self.cb_args = cb_args
        self.cb_kwargs = cb_kwargs

    def terminate(self):
        self.logger.info('Unbind queue #{}: received {} pkts'.format(self.queue, self.counter))
        self._loop.remove_reader(self._nfqueue_fd)
        self._nfqueue.unbind()

if __name__ == '__main__':
    log = logging.getLogger('')
    format = logging.Formatter("%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    log.setLevel(logging.INFO)
    
    loop = asyncio.get_event_loop()
    queues = []
    
    try:
        for n in sys.argv[1:]:
            queues.append(NFQueue3(int(n), None))
        
        loop.run_forever()
    
    except KeyboardInterrupt:
        pass
    
    finally:
        for q in queues:
            q.terminate()
        
        loop.close()
