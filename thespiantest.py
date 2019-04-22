from thespian.actors import *

class Hello(Actor):
    def receiveMessage(self, msg, sender):
        self.send(sender, 'Hello, World!')
        
if __name__ == "__main__":
    hello = ActorSystem().createActor(Hello)
    print(ActorSystem().ask(hello,'hi',1))
    ActorSystem().tell(hello,ActorExitRequest())
    ActorSystem().systemAddress()