import socket


class Traceroute:
    def __init__(self, dst, hops=30):
        self.dst = dst
        self.hops = hops
        self.ttl = 1
        self.port = 33435

    def run(self):
        try:
            dst_ip = socket.gethostbyname(self.dst)
        except socket.error as e:
            raise IOError(f'Unable to resolve {self.dst}: {e}')

        while True:
            receiver = self.create_receiver()
            sender = self.create_sender()
            sender.sendto(b'', (self.dst, self.port))

            addr = None
            try:
                data, addr = receiver.recvfrom(1024)
            except socket.error as e:
                raise IOError(f'Socket error: {e}')
            finally:
                receiver.close()
                sender.close()

            if addr:
                print(f'{self.ttl} {addr[0]}')
            else:
                print(f'{self.ttl} *')

            self.ttl += 1
            if addr[0] == dst_ip or self.ttl > self.hops:
                break

    def create_receiver(self):
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.getprotobyname('icmp'))
        s.settimeout(30)
        try:
            s.bind(('', self.port))
        except socket.error as e:
            raise IOError(f'Unable to bind receiver socket: {e}')

        return s

    def create_sender(self):
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.getprotobyname('udp'))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, self.ttl)

        return s


def main(dst):
    t = Traceroute(dst)
    t.run()


if __name__ == "__main__":
    main("google.com")
