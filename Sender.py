import sys
import getopt
import random

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.debug = debug

    # Main sending loop.
    def start(self):
      # add things here
        no_reads_after = False
        first_time = True
        read_size = 1024
        window = []
        curr_sequence_number = 0
        timeout = 0.5
        #create syn packet and send it
        random_sequence_number = random.randint(1, 100)
        syn_packet = self.make_packet('syn', random_sequence_number, '')
        self.send(syn_packet)
        #print "hello"
        #receive ack for syn packet, pass in timeout value?
        ack_packet = self.receive(timeout)
        while ack_packet is None:
            self.send(syn_packet)
            ack_packet = self.receive(timeout)
        if ack_packet is not None:
            if Checksum.validate_checksum(ack_packet):
                #print "here"
                ack_packet_split = self.split_packet(ack_packet)
                #print "here2"
                #print ack_packet_split
                #print random_sequence_number + 1
                # var = ack_packet_split[0] is 'ack' and int(ack_packet_split[1]) is random_sequence_number + 1
                # #print var
                #print var
                #print var2
                ##print var and var2
                #print ack_packet_split[0]
                if (str(ack_packet_split[0]) == 'ack') and (int(ack_packet_split[1]) is (random_sequence_number + 1)):
                    #print "here3"
                    curr_sequence_number = int(ack_packet_split[1])
                    # create window
                    for i in range(7):
                        read_result = self.infile.read(read_size)
                        if read_result == '':
                            #print "empty string"
                            break
                        packet = self.make_packet('dat', curr_sequence_number + i, read_result)
                        window.append(packet)
                    # send initial window
                    for i in window:
                        self.send(i)

                    while True:
                        #print "here"
                        
                        ack_packet = self.receive(timeout)

                        # advance window
                        if ack_packet is not None:
                            if Checksum.validate_checksum(ack_packet):
                                ack_packet_split = self.split_packet(ack_packet)
                                #print "over here"
                                #print ack_packet_split
                                #print int(self.split_packet(window[0])[1]) + 1
                                #print int(ack_packet_split[1]) == (int(self.split_packet(window[0])[1]) + 1)
                                window_advance_amount = int(ack_packet_split[1]) - int(self.split_packet(window[0])[1])
                                # if message type is ack and ACK sequence number is (sequence number of first entry of window + 1)
                                
                                if ack_packet_split[0] == 'ack': 
                                    if window_advance_amount > 0 and not no_reads_after:#int(ack_packet_split[1]) == (int(self.split_packet(window[0])[1]) + 1):
                                        #print "inside here"
                                        while window_advance_amount > 0 :
                                            read_result = self.infile.read(read_size)
                                            if read_result == '':
                                                #no reads after
                                                no_reads_after = True
                                                break
                                            packet = self.make_packet('dat', int(self.split_packet(window[-1])[1]) + 1, read_result)
                                            del window[0]
                                            window.append(packet)
                                            self.send(packet)
                                            window_advance_amount -= 1

                                    else:
                                        #if ACK sequence number is (last window item sequence number + 1)
                                        if int(ack_packet_split[1]) == (int(self.split_packet(window[-1])[1]) + 1) and no_reads_after:
                                            break
                        else:
                            # resend window there is a timeout
                            for i in window:
                                self.send(i)
                    # send fin
                    #print "fin"

                    # terminate connection
                    fin_packet = self.make_packet('fin', int(self.split_packet(window[-1])[1]) + 1, '')
                    self.send(fin_packet)
                    ack_packet = self.receive(timeout)
                    if ack_packet is not None:
                        if Checksum.validate_checksum(ack_packet):
                            ack_packet_split = self.split_packet(ack_packet)
                            if ack_packet_split[0] == 'ack' and int(ack_packet_split[1]) == int(self.split_packet(window[-1])[1]) + 2:
                                pass
                                #print "crap"
        # else:
        #     # resend syn if there is a timeout
        #     print "syn dropped"
    

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest,port,filename,debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
