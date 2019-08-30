# VyacheslavTr
# My Version 1
# 30.08.19


from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory, connectionDone


class Client(LineOnlyReceiver):

    delimiter = "\n".encode()

    
    factory: 'Server'  # указание фабрики для обработки подключений

    # информация о клиенте
    ip: str
    login: str = None

    def connectionMade(self):
        
        # Обработчик нового клиента

        # - записать IP
        # - внести в список клиентов
        # - отправить сообщение приветствия
        

        self.ip = self.transport.getPeer().host  # записываем IP адрес клиента
        self.factory.clients.append(self)  # добавляем в список клиентов фабрики

        self.sendLine("[Server] - Welcome to the chat!".encode())  # отправляем сообщение клиенту

        print(f"[Server] - Client {self.ip} connected")  # отображаем сообщение в консоли сервера

    def connectionLost(self, reason=connectionDone):
        
        # Обработчик закрытия соединения

        # - удалить из списка клиентов
        # - вывести сообщение в чат об отключении


        self.factory.clients.remove(self)  # удаляем клиента из списка в фабрике

        print(f"[Server] - Client {self.ip} disconnected")  # выводим уведомление в консоли сервера

    def lineReceived(self, line: bytes):
        
        # Обработчик нового сообщения от клиента

        # - зарегистрировать, если это первый вход, уведомить чат
        # - переслать сообщение в чат, если уже зарегистрирован
        

        message = line.decode()  # раскодируем полученное сообщение в строку

        # если логин еще не зарегистрирован
        if self.login is None:
            if message.startswith("login:"):  # проверяем, чтобы в начале шел login:
                user_login = message.replace("login:", "")  # вырезаем часть после :

                # проверка существования логина
                for user in self.factory.clients:
                    if user_login == user.login:
                        error = f"[Server] - Login {user_login} already exists!"

                        self.sendLine(error.encode())
                        
                        # В интерфейсе можно не прерывать подключение, 
                        # а просто повторно написать "login:значение" в текстовом поле
                        
                        # self.transport.loseConnection()
                        return

                self.login = user_login

                # отправка 10-ти сообщений новому клиенту
                self.send_history()

                notification = f"[Server] - New user: {self.login}"  # формируем уведомление о новом клиенте
                self.factory.notify_all_users(notification)  # отсылаем всем в чат
            else:
                self.sendLine("[Server] - Invalid login".encode())  # шлем уведомление, если в сообщении ошибка
        # если логин уже есть и это следующее сообщение
        else:
            format_message = f"{self.login}: {message}"  # форматируем сообщение от имени клиента

            # сохранять сообщения в список
            self.factory.messages.append(format_message)

            # отсылаем всем в чат и в консоль сервера
            self.factory.notify_all_users(format_message)
            print(format_message)

    def send_history(self):
        # Отправка новому клиенту последних 10-ти сообщений
        last_messages = self.factory.messages[-10:]

        for message in last_messages:
            self.sendLine(message.encode())


class Server(ServerFactory):
    # Класс для управления сервером

    clients: list  # список клиентов
    messages: list
    protocol = Client  # протокол обработки клиента

    def __init__(self):
        
        # Старт сервера

        # - инициализация списка клиентов
        # - вывод уведомления в консоль
        

        self.clients = []  # создаем пустой список клиентов
        self.messages = []

        print("[Server] - Server started - OK")  # уведомление в консоль сервера

    def startFactory(self):
        # Запуск прослушивания клиентов (уведомление в консоль)

        print("[Server] - Start listening ...")  # уведомление в консоль сервера

    def notify_all_users(self, message: str):
    
        # Отправка сообщения всем клиентам чата
        # :param message: Текст сообщения
        

        data = message.encode()  # закодируем текст в двоичное представление

        # отправим всем подключенным клиентам
        for user in self.clients:
            user.sendLine(data)


if __name__ == '__main__':
    # параметры прослушивания
    reactor.listenTCP(
        7410,
        Server()
    )

    # запускаем реактор
    reactor.run()
