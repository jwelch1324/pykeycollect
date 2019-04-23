from thespian.actors import Actor, ActorSystem, ActorExitRequest


class Hello(Actor):
    def receiveMessage(self, msg, sender):
        if isinstance(msg, dict):
            print(msg.keys())
        self.send(sender, 'Hello, World!')


if __name__ == "__main__":
    hello = ActorSystem().createActor(Hello)
    print(ActorSystem().ask(hello, 'hi', 1))
    print(ActorSystem().ask(hello,{'key1':'value1','key2':'vv2'}))
    ActorSystem().tell(hello, ActorExitRequest())
    ActorSystem().systemAddress()