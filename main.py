import tkinter as tk
import logging

from binance_futures import BinanceFuturesClient
from root_component import Root

from lstm_predictor import LSTMPredictorApp

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)




if __name__ == '__main__':

    binance = BinanceFuturesClient("5e7d1385e687bcc1271ffe07ffc9dc295c50d6d400ae85a1e270b08a9c91118d","473a3584d4af60fd093aaf5922dee984ece5e35a7f436ed71fff517c9cfac8d5")
    root = Root(binance)
    app = LSTMPredictorApp()
    
    root.mainloop()
    app.mainloop()




