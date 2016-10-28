# Author: Alexander Rymdeko-Harvey(@Killswitch-GUI)
# File: dns_struct.py 
# License: BSD 3-Clause
# Copyright (c) 2016, Alexander Rymdeko-Harvey 
# All rights reserved. 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met: 
#  * Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer. 
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution. 
#  * Neither the name of  nor the names of its contributors may be used to 
#    endorse or promote products derived from this software without specific 
#    prior written permission. 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

import struct
import binascii
import numpy

class dns_struct(object):
    """
    Base class for all class objects in the project,
    this will define the needed structure types and 
    ability to decode them.
    """

    # QR, Query/Response. 1 bit.
    QR = {  0 : 'QUERY',
            1 : 'RESPONSE'
    }

    # Opcode. 4 bits.
    OPCODE = {  0 : 'QUERY',
                1 : 'IQUERY',
                2 : 'STATUS',
                4 : 'NOTIFY',
                5 : 'UPDATE'
    }

    # AA, Authoritative Answer. 1 bit.
    #  Specifies that the responding name server is an authority for the domain name in question section. 
    #  Note that the contents of the answer section may have multiple owner names because of aliases. 
    #  This bit corresponds to the name which matches the query name, or the first owner name in the answer section.
    AA = {  0 : 'NOT AUTHORITATIVE',
            1 : 'AUTHORITATIVE'
    }

    # TC, Truncated. 1 bit.
    #  Indicates that only the first 512 bytes of the reply was returned.
    TC = {  0 : 'NOT TRUNCATED',
            1 : 'TRUNCATED'
    }

    # RD, Recursion Desired. 1 bit.
    #  May be set in a query and is copied into the response. 
    #  If set, the name server is directed to pursue the query recursively. 
    #  Recursive query support is optional.
    RD = {  0 : 'NOT DESIRED',
            1 : 'DESIRED'
    }

    # RA, Recursion Available. 1 bit.
    #  Indicat es if recursive query support is available in the name server.
    RA = {  0 : 'NOT AVAILABLE',
            1 : 'AVAILABLE'
    }

    # Z. 1 bit.
    Z = {} 

    # AD, Authenticated data. 1 bit.
    AD = {} 

    # CD, Checking Disabled. 1 bit.
    CD = {}

    # Rcode, Return code. 4 bits.
    RC = {  0 : 'NO ERROR',
            1 : 'FORMAT ERROR',
            2 : 'SERVER FAILURE',
            3 : 'NAME ERROR',
            4 : 'NOT IMPLEMENTED',
            5 : 'REFUSED',
            6 : 'YXDOMAIN',
            7 : 'YXRRSET',
            8 : 'NXRRSET',
            9 : 'NOTAUTH',
            10 : 'NOTZONE',
            16 : 'BADVERS',
            17 : 'BADKEY',
            18 : 'BADTIME',
            19 : 'BADMODE',
            20 : 'BADNAME', 
            21 : 'BADALG', 
            22 : 'BADTRUNC'
    } 

    _DNS_QUERY_SECTION_FORMAT = struct.Struct("!2H")

    def byte_to_binary(self, n):
        return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

    def hex_to_binary(self, h):
        return ''.join(self.byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

    def byte_to_hex( self, byteStr ):
        """
        Convert a byte string to it's hex string representation e.g. for output.
        http://code.activestate.com/recipes/510399-byte-to-hex-and-hex-to-byte-string-conversion/
        """
        
        # Uses list comprehension which is a fractionally faster implementation than
        # the alternative, more readable, implementation below
        #   
        #    hex = []
        #    for aChar in byteStr:
        #        hex.append( "%02X " % ord( aChar ) )
        #
        #    return ''.join( hex ).strip()        

        return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()

    def _unpack_dns_upper_codes(self, byte):
        byte = self.byte_to_hex(byte)
        data = self.hex_to_binary(byte)
        qr = data[0:1]
        opcode = data[1:5]
        aa = data[5:6]
        tc = data[6:7]
        rd = data[7:8]
        return {'qr' : qr, 'opcode' : opcode, 'aa' : aa, 'tc' : tc, 'rd' : rd}

    def _unpack_dns_lower_codes(self, byte):
        byte = self.byte_to_hex(byte)
        data = self.hex_to_binary(str(byte))
        ra = data[0:1]
        z = data[1:2]
        ad = data[2:3]
        cd = data[3:4]
        rc = data[4:8]
        return {'ra' : ra, 'z' : z, 'ad' : ad, 'cd' : cd, 'rc' : rc}

    def _upack_dns_codes(self, data):
        identification = struct.unpack('!H',data[8:10])[0]       # id. 16 bits.
        lower_byte = struct.unpack('!B',data[10:11])[0]          # lower byte for 8 bits to decode
        upper_byte = struct.unpack('!B',data[11:12])[0]          # upper byte for 8 bits to decode
        total_questions = struct.unpack('!H',data[12:14])[0]     # Total Questions. 16 bits, unsigned.
        total_answers_rr = struct.unpack('!H',data[14:16])[0]    # Total Answer RRs. 16 bits, unsigned.
        total_authority_rr = struct.unpack('!H',data[16:18])[0]  # Total Authority RRs. 16 bits, unsigned.
        total_additional_rr = struct.unpack('!H',data[18:20])[0] # Total Additional RRs. 16 bits, unsigned.
        temp_dns = {'identification':identification, 
                    'total_questions':total_questions, 
                    'total_answers_rr':total_answers_rr, 
                    'total_authority_rr':total_authority_rr,
                    'total_additional_rr':total_additional_rr}
        return temp_dns

    def _unpack_dns_rr(self, data, offset, arcount):
        """
        Unpakcs the dns resource record that is variable length.
        Using either the label method or pointer method.

        Takes:
        data = byte data from dns packet
        offset = int offset from query struc
        arcount = int specifying the number of resource records
        """
        # --------------------------------------------------------
        # |        | This name reflects the QNAME of the question  
        # |  Name  | i.e. any may take one of TWO formats.
        # |        | (label format defined for QNAME or pointer )
        # --------------------------------------------------------
        # |        | Unsigned 16 bit value. The resource record  
        # |  Type  | types - determines the content of the RDATA
        # |        | field.
        # --------------------------------------------------------
        # |        | Unsigned 16 bit value. The CLASS of resource 
        # | Class  | records being requested, for example, 
        # |        | Internet, CHAOS etc.
        # --------------------------------------------------------
        # |        | Unsigned 32 bit value. The time in seconds 
        # |   TTL  | that the record may be cached. A value of 0 
        # |        | indicates the record should not be cached.
        # --------------------------------------------------------
        # |        | Unsigned 16-bit value that defines the length 
        # |RDLENGTH| in bytes (octets) of the RDATA record.
        # |        |
        # --------------------------------------------------------
        # |        | Each (or rather most) resource record types 
        # |  RDATA | have a specific RDATA format which reflect 
        # |        | their resource record format.
        # --------------------------------------------------------
        answers = []
        offset_pointer = 0
        for _ in range(arcount):
            # set if we are using 
            name_pointer = self._check_dns_rr_pointer(data[offset:offset+1])
            if name_pointer:
                self._decode_rr_pointer(data, offset)
            else:
                # using label system
                print self._decode_rr_name_label(data,offset)


    def _decode_rr_name_label(self, message, offset):
        """
        decode a label format rr 
        """
        labels = []
        while True:
            length, = struct.unpack_from("!B", message, offset)
            offset += 1
            if length == 0:
                return labels, offset
            labels.append(*struct.unpack_from("!%ds" % length, message, offset))
            offset += length

    def _decode_rr_pointer(self, data, offset):
        """
        decode the pointer loction and parse
        the lable associated.
        takes:
        data = byte data
        offset = offset to start of pointer tag
        """ 
        # DNS Name type decode using bit type:
        # --------------------------------------------------------------------
        # | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |15
        # -------------------------
        # | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0  | 0  | 1  | 1  | 0  |0
        # --------------------------------------------------------------------
        # == 0x0c = 12 byte offset
        # 16 bit int that 2-15 bit locations are the offset from start 
        # of the dns packet
        octet = data[offset:offset+2]
        octet = self.byte_to_hex(octet)
        octet = self.hex_to_binary(str(octet))
        # calculate the offset in binary
        print octet
        #self.decode_labels(data, )

    def _check_dns_rr_pointer(self, byte):
        """
        check if byte is a pointer or lable type.
        takes:
        byte = a single byte of data to check 

        returns:
        bool = true or false
        """
        # DNS Name type decode using bit type:
        # -------------------------
        # | 0 | 1 | 2 | 3 | 4 etc..
        # -------------------------
        # | 1 | 1 | 0 | 0 | 0 etc..
        # -------------------------
        # if first two bits are set we are using a pointer type
        # for data compression 

        byte = self.byte_to_hex(byte)
        data = self.hex_to_binary(str(byte))
        if data[0:1] == 1 and data[1:2] == 1:
            return True
        else:
            return False


    def decode_labels(self, message, offset):
        labels = []

        while True:
            length, = struct.unpack_from("!B", message, offset)

            if (length & 0xC0) == 0xC0:
                pointer, = struct.unpack_from("!H", message, offset)
                offset += 2

                return labels + self.decode_labels(message, pointer & 0x3FFF), offset

            if (length & 0xC0) != 0x00:
                raise StandardError("unknown label encoding")

            offset += 1

            if length == 0:
                return labels, offset

            labels.append(*struct.unpack_from("!%ds" % length, message, offset))
            offset += length

    def decode_question_section(self, message, offset, qdcount):
        questions = []

        for _ in range(qdcount):
            qname, offset = self.decode_labels(message, offset)

            qtype, qclass = self._DNS_QUERY_SECTION_FORMAT.unpack_from(message, offset)
            offset += self._DNS_QUERY_SECTION_FORMAT.size

            question = {"domain_name": qname,
                        "query_type": qtype,
                        "query_class": qclass}

            questions.append(question)

        return questions, offset

    def unpack_udp(self, data):
        source_port = struct.unpack('!H',data[:2])[0]           # Source Port. 16 bits.
        destination_port = struct.unpack('!H',data[2:4])[0]     # Destination Port. 16 bits.
        length = struct.unpack('!H',data[4:6])[0]               # Destination Port. 16 bits.
        checksum = struct.unpack('!H',data[6:8])[0]             # Checksum. 16 bits.
        return {'src_port' : source_port, 'dst_port' : destination_port, 'length' : length, 'check_sum' : checksum}

    def unpack_dns(self, data):
        """
        Unpack dns byte data to a returned dict.
        Takes:
        data = the raw byte data from socket.

        returns:
        dns_dict = a full decoded dict of the dns packet struc.
        """
        # TODO: can you copy() from a function return data?
        lower_dict = self._unpack_dns_lower_codes(data[10:11])
        uper_dict = self._unpack_dns_upper_codes(data[11:12])
        dns_data = self._upack_dns_codes(data)
        dns_questions, question_offset = self.decode_question_section(data, 20, dns_data['total_questions'])
        if dns_data['total_answers_rr']:
            self._unpack_dns_rr(data, question_offset, dns_data['total_answers_rr'])
        # build the return data
        dns_dict = lower_dict.copy()
        dns_dict.update(uper_dict)
        dns_dict.update(dns_data)
        return dns_dict
        
        
