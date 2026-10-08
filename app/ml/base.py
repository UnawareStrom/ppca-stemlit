"""
Module 3: OOP's Using Python - Abstract Base Classes & Interfaces
Implements Abstract Base Classes (abc.ABC), Data Abstraction,
Encapsulation (Private & Protected attributes), and Property Decorators.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BasePredictor(ABC):
    """
    Abstract Base Class defining the contract for EduPulse ML Predictors.
    Demonstrates Abstraction and Interface design in Python.
    """

    def __init__(self, model_name: str = "BaseModel"):
        # Protected member (accessible to derived classes)
        self._model_name: str = model_name
        self._is_trained: bool = False
        
        # Private member (encapsulated with name-mangling)
        self.__engine_version: str = "2.1.0-TCET"

    @property
    def model_name(self) -> str:
        """Getter for protected member _model_name."""
        return self._model_name

    @property
    def engine_version(self) -> str:
        """Getter for private member __engine_version."""
        return self.__engine_version

    @property
    def is_trained(self) -> bool:
        """Getter for model training readiness."""
        return self._is_trained

    @is_trained.setter
    def is_trained(self, status: bool) -> None:
        """Setter demonstrating data validation inside property setter."""
        if not isinstance(status, bool):
            raise TypeError("Training status must be a boolean.")
        self._is_trained = status

    @abstractmethod
    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Abstract method that every concrete predictor subclass must implement.
        Must return prediction output dictionary.
        """
        pass

    @abstractmethod
    def explain(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Abstract method providing explainable AI feature contribution.
        """
        pass

