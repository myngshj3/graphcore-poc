
import socket

try:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 55580

    s.connect((host, port))
    print(s)
    while (True):
        try:
            # サーバ側へ送信するメッセージ
            your_input = input(">>> ")
            if len(your_input) > 0:
                s.send(your_input.encode("UTF-8"))
                # サーバーからのレスポンス
                while (True):
                    s.settimeout(3)
                    res = s.recv(4096)
                    print(res.decode())
                    if (len(res) == 0):
                        # 受信内容を出力
                        break

            else:
                continue
        except Exception as e:
            print(e)
            continue
except Exception as e:
    print(e)

