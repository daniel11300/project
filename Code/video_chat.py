import socket
import os
import time
import sys
import cv2
from threading import Thread
#from pydub import AudioSegment
import wave
import pyaudio
import argparse


class VideoChat(object):
    def __init__(self, args):
        self.FORMAT = pyaudio.paInt16
        self.QUIT = False
        self.QUIT2 = False
        self.QUIT3 = False
        self.fourcc = cv2.cv.CV_FOURCC(*'IYUV')
        self.CHANNELS = 2
        self.key = 'awesome'
        # how much read for seconed
        self.RATE = 44100
        # len of data that need to read
        self.CHUNK = 1024
        self.RECORD_SECONDS = 1000
        # instantiate PyAudio
        self.audio = pyaudio.PyAudio()
        if args.c:
            self.SERVER_IP = args.c
            self.__call_client()
        elif args.s:
            self.__call_server()

    def __call_client(self):
        print "Starting Client Mode"
        Thread(target=self.client_audio_send).start()
        Thread(target=self.client_audio_request).start()
        Thread(target=self.client_video_request).start()
        Thread(target=self.client_video_send).start()
        Thread(target=self.client_control1).start()
        Thread(target=self.client_control2).start()

    def __call_server(self):
        print "Starting Server Mode"
        Thread(target=self.server_audio_request).start()
        Thread(target=self.server_audio_send).start()
        Thread(target=self.server_video_request).start()
        Thread(target=self.server_video_send).start()
        Thread(target=self.server_control1).start()
        Thread(target=self.server_control2).start()

    def _create_TCP_server(self, PORT):
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen(1)
        client_socket, client_address = server_socket.accept()
        return (client_socket, server_socket)

    def _create_UDP_server(self, PORT):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', PORT))
        return server_socket

    def _file_manager(self, File_Name):
        if os.path.exists(File_Name):
            os.remove(File_Name)

    def _create_wav_file(self, File_Name):
        waveFile = wave.open(File_Name, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        return waveFile

    def _video_request(self, File_Name, data):
        decoded = self.xor_crypt_string(data, self.key, False, True)
        f = open(File_Name, 'wb')
        f.write(decoded)
        f.close()
        cv2.waitKey(100)
        img = cv2.imread(File_Name, 1)
        cv2.imshow('image', img)
        return img

    def _video_send(self, File_Name, cap):
        ret, frame = cap.read()
        n_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow('window-name', n_frame)  # imshow show the picture
        cv2.imwrite(File_Name, n_frame)  # iw saves the picture
        f = open(File_Name, "rb")
        l = f.read(1000000)
        f.close()
        return n_frame, l

    def server_control1(self):
        (client_socket_control1,
         server_socket_control1) = self._create_TCP_server(4568)
        while self.QUIT is False:
            time.sleep(.01)
        try:
            client_socket_control1.send('exit')
        except:
            pass
        client_socket_control1.close()
        server_socket_control1.close()
        print 'shabat'
        while self.QUIT2 is False or self.QUIT3 is False:
            time.sleep(.01)
        sound1 = AudioSegment.from_file(r"d:\daniel\client.wav")
        sound2 = AudioSegment.from_file(r"d:\daniel\server.wav")
        combined = sound1.overlay(sound2)
        self._file_manager(r"d:\daniel\chat_audio.wav")
        combined.export(r"d:\daniel\chat_audio.wav", format='wav')
        exit()

    def server_control2(self):
        (client_socket_control2,
         server_socket_control2) = self._create_TCP_server(4569)
        try:
            data = client_socket_control2.recv(1024)
            if data == 'exit':
                self.QUIT = True
        except:
            pass
        client_socket_control2.close()
        server_socket_control2.close()
        exit()

    def server_video_request(self):
        server_socket_video_request = self._create_UDP_server(3626)
        out = cv2.VideoWriter(r"d:\daniel\client_video.avi",
                              self.fourcc, 4, (320, 240))
        while self.QUIT is False:
            data, client_address_video_request = server_socket_video_request.recvfrom(1000000)
            # TODO: figure out working with StringIO (not with files)
            img = self._video_request(r'd:\pic1.jpg', data)
            out.write(img)
        print "server_socket_video_request.close"
        out.release()
        server_socket_video_request.close()

    def server_video_send(self):
        server_socket_video_send = self._create_UDP_server(9321)
        data, client_address_video_send = server_socket_video_send.recvfrom(30000)
        cap = cv2.VideoCapture(0)
        out = cv2.VideoWriter(r"d:\daniel\server_video.avi",
                              self.fourcc, 4, (320, 240))
        while cap.isOpened() and self.QUIT is False:
            n_frame, l = self._video_send(r"d:\frame1.jpg", cap)
            out.write(n_frame)
            try:
                encoded = self.xor_crypt_string(l, self.key, True, False)
                server_socket_video_send.sendto(encoded,
                                                client_address_video_send)
            except:
                pass
            if cv2.waitKey(100) & 0xFF == ord('q'):
                print "server_video_send() got Q"
                self.QUIT = True
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print "server_socket_video_send.close"
        try:
            server_socket_video_send.close()
        except:
            pass

    def server_audio_request(self):
        server_socket_audio_request = self._create_UDP_server(2544)
        # open stream
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, output=True)
        self._file_manager(r"d:\daniel\client.wav")
        waveFile = self._create_wav_file(r"d:\daniel\client.wav")
        while self.QUIT is False:
            data, client_address_audio_request = server_socket_audio_request.recvfrom(1000000)
            if data == 'finish' or data == '':
                a = 0
            else:
                waveFile.writeframes(data)
                try:
                    stream.write(data)
                except:
                    pass
        stream.stop_stream()
        print "server_socket_audio_request.close"
        server_socket_audio_request.close()
        waveFile.close()
        self.QUIT2 = True

    def server_audio_send(self):
        server_socket_audio_send = self._create_UDP_server(9652)
        data, client_address_audio_send = server_socket_audio_send.recvfrom(30000)
        # start Recording
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, input=True,
                                 frames_per_buffer=self.CHUNK)
        print "recording..."
        self._file_manager(r"d:\daniel\server.wav")
        waveFile = self._create_wav_file(r"d:\daniel\server.wav")
        while self.QUIT is False:
            for i in range(0,
                           int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                if self.QUIT is True:
                    break
                try:
                    data = stream.read(self.CHUNK)
                    waveFile.writeframes(data)
                    server_socket_audio_send.sendto(data,
                                                    client_address_audio_send)
                except Exception, e:
                    break
            print "finished recording"
            try:
                server_socket_audio_send.sendto('finish',
                                                client_address_audio_send)
            except:
                pass
        # stop Recording
        stream.stop_stream()
        stream.close()
        print "server_socket_audio_send.close"
        server_socket_audio_send.close()
        waveFile.close()
        self.QUIT3 = True

    @staticmethod
    def xor_crypt_string(data, key='awesomepassword',
                         encode=False, decode=False):
        from itertools import izip, cycle
        import base64
        if decode:
            try:
                data = base64.decodestring(data)
            except:
                print 'ht'
        xored = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in izip(data,
                                                                cycle(key)))
        if encode:
            return base64.encodestring(xored).strip()
        return xored

    # --------------------------------------------------------CLIENT-------------------------------------------------------------------
    def _create_TCP_client(self, PORT):
        client_socket = socket.socket()
        client_socket.connect((self.SERVER_IP, PORT))
        return client_socket

    def client_control1(self):
        client_socket_control1 = self._create_TCP_client(4569)
        while self.QUIT is False:
            pass
        try:
            client_socket_control1.send('exit')
        except:
            pass
        client_socket_control1.close()
        exit()

    def client_control2(self):
        client_socket_control2 = self._create_TCP_client(4568)
        try:
            data = client_socket_control2.recv(1024)
            if data == 'exit':
                self.QUIT = True
        except:
            pass
        client_socket_control2.close()
        exit()

    def client_video_send(self):
        my_socket_video_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cap = cv2.VideoCapture(0)
        while cap.isOpened() and self.QUIT is False:
            n_frame, l = self._video_send(r"d:\frame1.jpg", cap)
            try:
                encoded = self.xor_crypt_string(l, self.key, True, False)
                my_socket_video_send.sendto(encoded, (self.SERVER_IP, 3626))
            except:
                pass
            if cv2.waitKey(100) & 0xFF == ord('q'):
                self.QUIT = True
        cap.release()
        cv2.destroyAllWindows()
        print "my_socket_video_send.close"
        my_socket_video_send.close()

    def client_video_request(self):
        my_socket_video_request = socket.socket(socket.AF_INET,
                                                socket.SOCK_DGRAM)
        my_socket_video_request.sendto("give me stream",
                                       (self.SERVER_IP, 9321))
        while self.QUIT is False:
            try:
                data, remote_address = my_socket_video_request.recvfrom(3000000)
                img = self._video_request(r'd:\pic1.jpg', data)
            except:
                pass
        print "my_socket_video_request.close"
        my_socket_video_request.close()

    def client_audio_send(self):
        my_socket_audio_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # start Recording
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, input=True,
                                 frames_per_buffer=self.CHUNK)
        print "recording..."
        while self.QUIT is False:
            for i in range(0,
                           int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                try:
                    data = stream.read(self.CHUNK)
                    my_socket_audio_send.sendto(data, (self.SERVER_IP, 2544))
                except:
                    pass
            print "finished recording"
            my_socket_audio_send.sendto('finish', (self.SERVER_IP, 2544))
        # stop Recording
        stream.stop_stream()
        stream.close()
        self.audio.terminate()
        print "my_socket_audio_send.close"
        my_socket_audio_send.close()

    def client_audio_request(self):
        my_socket_audio_request = socket.socket(socket.AF_INET,
                                                socket.SOCK_DGRAM)
        my_socket_audio_request.sendto("give me stream",
                                       (self.SERVER_IP, 9652))
        # open stream
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                 rate=self.RATE, output=True)
        while self.QUIT is False:
            try:
                data, remote_address = my_socket_audio_request.recvfrom(3000000)
                if data == 'finish' or data == '':
                    a = 0
                else:
                    stream.write(data)
            except:
                pass
        stream.stop_stream()
        stream.close()
        # close PyAudio
        try:
            self.audio.terminate()
        except:
            pass
        finally:
            print "my_socket_audio_request.close"
            my_socket_audio_request.close()


def parse_args():
    print "Starting Arg Parser"
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", action="store_true", default=False,
                        help="Server Mode")
    parser.add_argument("-c", default=False, help="Client Mode")
    args = parser.parse_args()
    print "server:%s, client:%s" % (args.s, args.c)
    return args


def main():
    args = parse_args()
    if not args:
        return 1
    # conf_dict = {'args': args}
    VideoChat(args)
    return 0

if __name__ == "__main__":
    print "Starting"
    exit_code = main()
    print "End"
    sys.exit(exit_code)
