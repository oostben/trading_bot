from abc import ABC, abstractmethod
from typing import List
import random

class SModel(ABC):
    """
    The Strategy interface declares operations common to all supported versions
    of some algorithm.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """

    @abstractmethod
    def train(self):
        pass
    
    @abstractmethod
    def predict(self, data:List):
        pass

    def shuffle_data(self):
        c = list(zip(self.x_train,self.y_train))
        random.shuffle(c)
        x, y = zip(*c)
        self.x_train = list(x)
        self.y_train = list(y)

    @abstractmethod
    def get_val_y(self):
        pass
class IModel():
    """
    The model context defines the interface of interest to clients.
    """

    def __init__(self, model_strategy: SModel) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._model = model_strategy

    @property
    def model(self) -> SModel:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """

        return self._model

    @model.setter
    def strategy(self, model_strategy: SModel) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._model = model_strategy

    def train(self) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        self._model.train()

    def predict(self,data) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """
        return self._model.predict(data)

    def set_data(self, x_train, y_train, x_validation=None, y_validation=None):
        self._model.set_data(x_train, y_train, x_validation, y_validation)

    def get_val_y(self):
        return self._model.get_val_y()

