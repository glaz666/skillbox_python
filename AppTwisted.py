from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineOnlyReceiver


class Handler(LineOnlyReceiver):
    factory: 'Server'
    login: str

    def lineReceived(self, line: bytes):
        message = line.decode()

        if self.login is not None:
            message = f"<{self.login}>: {message}"
            self.broadCastButMe(message)
        else:
            message = line.decode()
            if message.startswith("login: "):
                _login = message.replace("login: ", "")
                if _login in self.factory.clients:
                    self.sendLine(f"{_login} is taken".encode())
                    self.transport.loseConnection()
                else:
                    self.login = _login
                    print(f"new login: {self.login}")
                    self.sendHistory()

            else:
                self.sendLine("incorrect login. must be \"login: <name>\" ".encode())


    def broadCastButMe(self, message: str):
        for user in self.factory.clients:
            if user is not self:
                user.sendLine(message.encode())

        self.factory.history.append(message)
        if len(self.factory.history) > 10:
            self.factory.history.pop(0)


    def sendHistory(self):
        for msg in self.factory.history:
            self.sendLine(msg.encode())


    def connectionMade(self):
        self.login = None
        self.factory.clients.append(self)
        print(f'Connected clients: {len(self.factory.clients)}')


    def connectionLost(self, reason):
        self.factory.clients.remove(self)


class Server(ServerFactory):
    protocol = Handler
    clients: list
    history: list

    def __init__(self):
        self.clients = []
        self.history = []

    def startFactory(self):
        print("Starting...")


reactor.listenTCP(
    7410,
    Server()
)
reactor.run()
