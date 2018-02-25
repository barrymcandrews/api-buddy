from time import sleep

from pinance import Pinance

symbols = ["AAPL", "FDX", "MSFT", "AMZN", "GIS"]

while True:
    beginning_up = "<message type=\"scroll\" color=\"#00ff00\">"
    beginning_down = "<message type=\"scroll\" color=\"#ff0000\">"
    end = "</message>"
    ups = ""
    downs = ""
    for i in range(len(symbols)):
        stock = Pinance(symbols[i])
        stock.get_quotes()
        if stock.quotes_data['regularMarketChangePercent'] >= 0:
            ups += (stock.quotes_data['symbol'] + " - " + str(stock.quotes_data['postMarketPrice']) + " " + str(
                "{0:.2f}".format(stock.quotes_data['regularMarketChangePercent'])) + "% ↑   ")
        else:
            downs += (stock.quotes_data['symbol'] + " - " + str(stock.quotes_data['postMarketPrice']) + " " + str(
                "{0:.2f}".format(stock.quotes_data['regularMarketChangePercent'])) + "% ↓   ")

    if ups != "":
        file = open("/tmp/led-source-news", 'w')
        file.write(beginning_up + ups + end)
        file.close()
        print(ups)
        sleep(60)

    if downs != "":
        file = open("/tmp/led-source-news", 'w')
        file.write(beginning_down + downs + end)
        file.close()
        print(downs)
        sleep(60)


