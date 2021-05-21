from system_constants import *
from betting_agents import *
from race_simulator import Simulator
from ex_ante_odds_generator import *
from exchange import Exchange
from message_protocols import *
from session_stats import *


#### TESTS ####
# 1-> empty creation
# 2-> Adding to orderbook
# 3 -> Best odd after addition
# 3 -> Match function -> order larger than market, order less than market, order equal to market
# 4 -> Settle up


def test_initialised_empty(exchange):
    for orderbook in exchange.compOrderbooks:
        assert orderbook.backs.numOfOrders == 0
        assert orderbook.lays.numOfOrders == 0


def test_adding_order(exchange):
    agentId = 1
    competitor = 0
    odds = 2.5
    stake = 12
    orderId = 0
    orderTime = time.time()
    order = Order(exchange.id, agentId, competitor, 'Back', odds, stake, orderId, orderTime)
    exchange.addOrder(order)

    for orderbook in exchange.compOrderbooks:
        if orderbook.competitorId == competitor:
            assert orderbook.backs.bestOdds == 2.5
            assert orderbook.backs.numOfOrders == 1
            assert orderbook.backs.market[odds][0] == 12
            bestOrder = orderbook.backs.market[odds][1]
            timeOfOrder = bestOrder[0][0]
            agent = bestOrder[0][2]
            id = bestOrder[0][3]
            assert timeOfOrder == orderTime
            assert agent == agentId
            assert id == orderId
        else:
            assert orderbook.backs.numOfOrders == 0
            assert orderbook.lays.numOfOrders == 0


def test_odds_update(exchange):
    agentId = 4
    competitor = 0
    odds = 2.3
    stake = 10
    orderId = 1
    orderTime = time.time()
    order = Order(exchange.id, agentId, competitor, 'Back', odds, stake, orderId, orderTime)
    exchange.addOrder(order)

    for orderbook in exchange.compOrderbooks:
        if orderbook.competitorId == competitor:
            assert orderbook.backs.bestOdds == 2.3
            assert orderbook.backs.numOfOrders == 2
            assert orderbook.backs.market[odds][0] == 10
            bestOrder = orderbook.backs.market[odds][1]
            timeOfOrder = bestOrder[0][0]
            agent = bestOrder[0][2]
            id = bestOrder[0][3]
            assert timeOfOrder == orderTime
            assert agent == agentId
            assert id == orderId
        else:
            assert orderbook.backs.numOfOrders == 0
            assert orderbook.lays.numOfOrders == 0


def test_matching_engine(exchange):
    agentId = 2
    competitor = 0
    odds = 2.4
    stake = 10
    orderId = 1
    orderTime = time.time()
    order = Order(exchange.id, agentId, competitor, 'Lay', odds, stake, orderId, orderTime)
    exchange.processOrder(orderTime, order)

    for orderbook in exchange.compOrderbooks:
        if orderbook.competitorId == competitor:
            assert orderbook.backs.bestOdds == 2.5
            assert orderbook.backs.numOfOrders == 1
            assert orderbook.backs.market[orderbook.backs.bestOdds][0] == 12
        else:
            assert orderbook.backs.numOfOrders == 0
            assert orderbook.lays.numOfOrders == 0


def test_tape_recording(exchange):
    agentId = 2
    competitor = 0
    odds = 3
    stake = 4
    orderId = 3
    orderTime = time.time()
    order = Order(exchange.id, agentId, competitor, 'Lay', odds, stake, orderId, orderTime)
    exchange.processOrder(orderTime, order)


    for orderbook in exchange.compOrderbooks:
        tapeitems = orderbook.tape

        if orderbook.competitorId == competitor:
            assert len(tapeitems) == 2
            assert tapeitems[0]['backer'] == 4
            assert orderbook.backs.bestOdds == 2.5
            assert orderbook.backs.numOfOrders == 1
            assert orderbook.backs.market[orderbook.backs.bestOdds][0] == 8
        else:
            assert len(tapeitems) == 0
            assert orderbook.backs.numOfOrders == 0
            assert orderbook.lays.numOfOrders == 0


def run_tests():
    # Create set-up
    exchange = Exchange(0, NUM_OF_COMPETITORS)

    test_initialised_empty(exchange)
    print("Testing addition of order...")
    test_adding_order(exchange)

    print("Testing update of best odds...")
    test_odds_update(exchange)

    print("Testing matching engine...")
    test_matching_engine(exchange)

    print("Testing tape recording...")
    test_tape_recording(exchange)


if __name__ == "__main__":
    run_tests()
    print("/////////////////")
    print("All Tests Passed!")
    print("/////////////////")
