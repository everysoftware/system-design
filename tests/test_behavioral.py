from patterns.behavioral.command import Bank, Account
from patterns.behavioral.cor import LeaveRequest, Manager, Director, TeamLead
from patterns.behavioral.interpreter import Subtract, Number, Add
from patterns.behavioral.iterator import NameCollection
from patterns.behavioral.mediator import ChatRoom, Participant
from patterns.behavioral.memento import Object, Caretaker
from patterns.behavioral.observer import (
    TemperatureSensor,
    AirConditioner,
    Heater,
)
from patterns.behavioral.retry import retry
from patterns.behavioral.servant import Circle, Square, Mover
from patterns.behavioral.session import CloudClient
from patterns.behavioral.state import (
    ATM,
    NoCard,
    HasCard,
    RIGHT_PIN,
    CorrectPin,
)
from patterns.behavioral.strategy import (
    Product,
    Order,
    RegularShipping,
    OrderService,
)
from patterns.behavioral.template_method import Tea, Coffee
from patterns.behavioral.visitor import Car, Bike, MaintenanceVisitor


def test_command() -> None:
    bank = Bank()

    account1 = Account("Marcus Aurelius")
    bank.operation(account1, 1000)
    bank.operation(account1, -50)

    account2 = Account("Antoninus Pius")
    bank.operation(account2, 500)
    bank.operation(account2, -100)
    bank.operation(account2, 150)

    assert account1.balance == 950
    assert account2.balance == 550

    bank.undo(3)
    assert account1.balance == 950
    assert account2.balance == 0

    bank.undo(2)
    assert account1.balance == 0
    assert account2.balance == 0


def test_interpreter() -> None:
    expression = Subtract(Number(10), Add(Number(5), Number(3)))
    assert expression.interpret() == 2


def test_iterator() -> None:
    names = NameCollection()
    names.add_name("Alice")
    names.add_name("Bob")
    names.add_name("Charlie")

    # list(names) = [name for name in names]
    assert list(names) == ["Alice", "Bob", "Charlie"]


def test_retry() -> None:
    attempt = 0

    @retry(ConnectionError, attempts=2, delay=0.001)
    def unstable_operation() -> str:
        nonlocal attempt
        attempt += 1
        if attempt < 2:
            raise ConnectionError("Temporary connection error.")
        return "Operation successful!"

    assert unstable_operation() == "Operation successful!"


def test_state() -> None:
    atm = ATM(500)

    assert isinstance(atm.get_state(), NoCard)
    assert atm.get_cash() == 500

    # Insert card, transition to HasCard state
    response = atm.insert_card()
    assert response == "Card inserted."
    assert isinstance(atm.get_state(), HasCard)

    # Attempt to request cash without entering the PIN
    response = atm.request_cash(100)
    assert response == "Enter PIN first."
    assert isinstance(atm.get_state(), HasCard)

    # Enter incorrect PIN, return to NoCard state
    response = atm.enter_pin(1111)  # Incorrect PIN
    assert response == "Incorrect PIN."
    assert isinstance(atm.get_state(), NoCard)

    # Insert card again, transition to HasCard state
    atm.insert_card()
    assert isinstance(atm.get_state(), HasCard)

    # Enter correct PIN, transition to CorrectPin state
    response = atm.enter_pin(RIGHT_PIN)
    assert response == "Correct PIN."
    assert isinstance(atm.get_state(), CorrectPin)

    # Attempt to insert the card again after entering the PIN
    response = atm.insert_card()
    assert response == "Card already inserted."
    assert isinstance(atm.get_state(), CorrectPin)

    # Re-enter PIN after successful authorization
    response = atm.enter_pin(RIGHT_PIN)
    assert response == "PIN already entered."
    assert isinstance(atm.get_state(), CorrectPin)

    # Successfully request cash in CorrectPin state, transition to NoCard
    response = atm.request_cash(100)
    assert response == "100 cash received."
    assert atm.get_cash() == 400
    assert isinstance(atm.get_state(), NoCard)

    # Attempt to request cash without a card after completing a transaction
    response = atm.request_cash(100)
    assert response == "Insert card first."
    assert isinstance(atm.get_state(), NoCard)

    # Check insufficient funds
    atm.insert_card()
    atm.enter_pin(RIGHT_PIN)
    response = atm.request_cash(600)  # Request more than available cash
    assert response == "Not enough cash."
    assert atm.get_cash() == 400  # Balance should remain unchanged
    assert isinstance(atm.get_state(), NoCard)

    # Insert card again after being denied cash due to insufficient funds
    response = atm.insert_card()
    assert response == "Card inserted."
    assert isinstance(atm.get_state(), HasCard)


def test_strategy() -> None:
    order = Order([Product(price=10, quantity=2), Product(price=20)])
    shipping = RegularShipping()
    service = OrderService()
    # 10 * 2 + 20 + 10
    assert service.calculate_total(order, shipping) == 50


def test_template_method() -> None:
    tea = Tea()
    tea.prepare_beverage()

    coffee = Coffee()
    coffee.prepare_beverage()


def test_servant() -> None:
    circle = Circle(5, 5)
    square = Square(10, 10)
    mover = Mover()

    mover.move(circle, 3, 4)
    assert circle.x == 8
    assert circle.y == 9

    mover.move(square, -2, 5)
    assert square.x == 8
    assert square.y == 15


def test_session() -> None:
    with CloudClient("username", "password") as session:
        session.upload("file1.txt")
        assert "file1.txt" in session.uploaded_files
    assert not session.is_authenticated


def test_visitor() -> None:
    car = Car(1000)
    bike = Bike(True)
    visitor = MaintenanceVisitor()
    assert car.accept(visitor) == 200
    assert bike.accept(visitor) == 60


def test_cor() -> None:
    leave_request = LeaveRequest(30)
    # Make chain: TeamLead -> Manager -> Director
    director = Director()
    manager = Manager(director)
    team_lead = TeamLead(manager)
    response = team_lead.approve(leave_request)

    assert response.reviewer_position == "Director"
    assert response.approved


def test_mediator() -> None:
    chatroom = ChatRoom()
    user1 = Participant("Alice", chatroom)
    user2 = Participant("Bob", chatroom)
    user3 = Participant("Charlie", chatroom)

    user1.send("Hello everyone!")
    assert user1.sent == "Hello everyone!"
    assert user2.received == "Hello everyone!"
    assert user3.received == "Hello everyone!"

    user2.send("Hi Alice!")
    assert user2.sent == "Hi Alice!"
    assert user1.received == "Hi Alice!"
    assert user3.received == "Hi Alice!"

    user3.send("Hey all!")
    assert user3.sent == "Hey all!"
    assert user1.received == "Hey all!"
    assert user2.received == "Hey all!"


def test_memento() -> None:
    originator = Object("Initial state")
    caretaker = Caretaker()

    memento1 = originator.save()
    caretaker.add(memento1)
    originator.set_state("New state")
    assert originator.get_state() == "New state"

    memento2 = originator.save()
    caretaker.add(memento2)
    originator.restore(caretaker.get(0))
    assert originator.get_state() == "Initial state"

    originator.restore(caretaker.get(1))
    assert originator.get_state() == "New state"


def test_observer() -> None:
    sensor = TemperatureSensor()
    ac = AirConditioner()
    heater = Heater()

    sensor.attach(ac)
    sensor.attach(heater)

    sensor.set_temperature(22)
    assert ac.temperature == 22
    assert heater.temperature == 22
    sensor.set_temperature(18)
    assert ac.temperature == 18
    assert heater.temperature == 18
