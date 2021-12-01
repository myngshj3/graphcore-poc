
import socket
import select
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 接続待ちするサーバのホスト名とポート番号を指定
host = "127.0.0.1"
port = 55580
argument = (host, port)
sock.bind(argument)
# 5 ユーザまで接続を許可
sock.listen(5)
clients = []

# 接続済みクライアントは読み込みおよび書き込みを繰り返す
def loop_handler(connection, address):
    while True:
        try:
            #クライアント側から受信する
            res = connection.recv(4096)
            if len(res) == 0:
                print("connection seems to be shutdown")
                break
            for value in clients:
                if value[1][0] == address[0] and value[1][1] == address[1] :
                    print("クライアント{}:{}から{}というメッセージを受信完了".format(value[1][0], value[1][1], res))
                else:
                    value[0].send("クライアント{}:{}から{}を受信".format(value[1][0], value[1][1], res.decode()).encode("UTF-8"))
                    pass
        except Exception as e:
            print(e)
            break


while True:
    try:
        # 接続要求を受信
        conn, addr = sock.accept()

    except KeyboardInterrupt:
        sock.close()
        exit()
        break
    # アドレス確認
    print("[アクセス元アドレス]=>{}".format(addr[0]))
    print("[アクセス元ポート]=>{}".format(addr[1]))
    print("\r\n")
    # 待受中にアクセスしてきたクライアントを追加
    clients.append((conn, addr))
    # スレッド作成
    thread = threading.Thread(target=loop_handler, args=(conn, addr), daemon=True)
    # スレッドスタート
    thread.start()