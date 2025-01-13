#!/usr/bin/env python3

import time
import datetime
import argparse
import signal
from lib.xAppBase import xAppBase

class MyXapp(xAppBase):
    def __init__(self, http_server_port, rmr_port):
        super(MyXapp, self).__init__('', http_server_port, rmr_port)
        pass

    def trigger_ho(self, e2_node):
        #current_time = datetime.datetime.now()
        #print("{} Send RIC Control Request to E2 node ID: {}".format(current_time.strftime("%H:%M:%S"), e2_node))
        if e2_node == 'gnbd_001_001_00019b_1':
            self.e2sm_rc.control_handover(e2_node, source_pci=1, target_pci=2)
        elif e2_node == 'gnbd_001_001_00019b_2':
            self.e2sm_rc.control_handover(e2_node, source_pci=2, target_pci=1)
        else:
            print("Fatal Error! unexpected e2_node.")
        time.sleep(5)

    # Mark the function as xApp start function using xAppBase.start_function decorator.
    # It is required to start the internal msg receive loop.
    @xAppBase.start_function
    def start(self):
        e2_node_list = ['gnbd_001_001_00019b_1', 'gnbd_001_001_00019b_2']
        switch_flag = False
        try:
            while self.running:
                user_input = input("Press Enter to handover users (or) q to quit: ")
                if user_input == "":
                    self.trigger_ho(e2_node_list[switch_flag])
                    switch_flag = not switch_flag
                else:
                    break
        except KeyboardInterrupt:
            pass
        signal.raise_signal(signal.SIGINT)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Frequency Agility xApp')
    parser.add_argument("--http_server_port", type=int, default=8091, help="HTTP server listen port")
    parser.add_argument("--rmr_port", type=int, default=4560, help="RMR port")
    #parser.add_argument("--e2_node_id", type=str, default='gnbd_001_001_00019b_1', help="E2 Node ID")
    parser.add_argument("--ran_func_id", type=int, default=2, help="E2SM RAN function ID")
    parser.add_argument("--kpm_report_style", type=int, default=4, help="KPM Report Style ID")
    parser.add_argument("--metrics", type=str, default='DRB.UEThpDl,DRB.UEThpUl', help="Metrics name as comma-separated string")


    args = parser.parse_args()
    ran_func_id = args.ran_func_id # TODO: get available E2 nodes from SubMgr, now the id has to be given.

    # Create MyXapp.
    myXapp = MyXapp(args.http_server_port, args.rmr_port)
    myXapp.e2sm_kpm.set_ran_func_id(ran_func_id)

    # Connect exit signals.
    signal.signal(signal.SIGQUIT, myXapp.signal_handler) # Ctrl+\
    signal.signal(signal.SIGTERM, myXapp.signal_handler)
    signal.signal(signal.SIGINT, myXapp.signal_handler) # Ctrl+c

    # Start xApp.
    myXapp.start()
