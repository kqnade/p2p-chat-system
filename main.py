import threading
import socket
import sys
import json
import time
import udp as pu
from config import seed


class Node:
    seed = seed
    peers = {}
    myid = ""
    udp_socket = {}

    def rece(self):
        while 1:
            data, addr = pu.recembase(self.udp_socket)
            action = json.loads(data)
            # print(action["type"])                     <=
            #     self.dispatch(action, addr)           <= 検証用
            # def dispatch(self, action,addr):          <=
            if action['type'] == 'newpeer':
                print("A new peer is coming")
                self.peers[action['data']] = addr
                # print(addr)
                pu.sendJS(self.udp_socket, addr, {
                    "type": 'peers',
                    "data": self.peers
                })

            if action['type'] == 'peers':
                print("Received a bunch of peers")
                self.peers.update(action['data'])
                # introduce yourself.
                pu.broadcastJS(self.udp_socket, {
                    "type": "introduce",
                    "data": self.myid
                }, self.peers)

            if action['type'] == 'introduce':
                print("Get a new friend.")
                self.peers[action['data']] = addr

            if action['type'] == 'input':
                print(action['data'])

            if action['type'] == 'exit':
                if self.myid == action['data']:
                    # スパム対策
                    time.sleep(0.5)
                    break
                    # self.udp_socket.close()　<= 検証用
                value, key = self.peers.pop(action['data'])
                print(action['data'] + " is left.")

    def startpeer(self):
        pu.sendJS(self.udp_socket, self.seed, {
            "type": "newpeer",
            "data": self.myid
        })

    def send(self):
        while 1:
            msg_input = input("$:")
            if msg_input == "exit":
                pu.broadcastJS(self.udp_socket, {
                    "type": "exit",
                    "data": self.myid
                }, self.peers)
                break
            if msg_input == "friends":
                print(self.peers)
                continue
            l = msg_input.split()
            if l[-1] in self.peers.keys():
                toA = self.peers[l[-1]]
                s = ' '.join(l[:-1])
                pu.sendJS(self.udp_socket, toA, {
                    "type": "input",
                    "data": s
                })
            else:
                pu.broadcastJS(self.udp_socket, {
                    "type": "input",
                    "data": msg_input
                }, self.peers)
                continue


def main():
    port = int(sys.argv[1])  # コマンドラインからポート番号を取得する
    fromA = ("127.0.0.1", port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((fromA[0], fromA[1]))
    peer = Node()
    peer.myid = sys.argv[2]
    peer.udp_socket = udp_socket
    # print(fromA, peer.myid)  <= 検証用
    peer.startpeer()
    t1 = threading.Thread(target=peer.rece, args=())
    t2 = threading.Thread(target=peer.send, args=())

    t1.start()
    t2.start()


if __name__ == '__main__':
    main()

# 使い方ガイド:
# python main.py 8891 id1
# python main.py 8892 id2
# python main.py 8893 id3
