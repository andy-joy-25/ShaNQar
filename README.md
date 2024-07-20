# ShaNQar: Simulator of Network Quantique

ShaNQar (Simulator of Network Quantique) is a modular and customizable photonic quantum network simulator.

## Installation

Please ensure that you have a Python version of 3.10 or later installed in your computer. If you don't have it installed already, please download it from the [official Python website](https://www.python.org/downloads/).

After that is done, please clone this repo and install the necessary requirements by copy-pasting the following code in your terminal:
```
git clone https://github.com/andy-joy-25/ShaNQar.git
cd ShaNQar
pip install -r requirements.txt
```

## Running Tests

Certain expected results are only observed on average since the working of the components is inherently probabilistic in the quantum mechanical regime. To verify and validate that the elements of ShaNQar's hardware stack are working correctly, please run our rigorous test suite by copy-pasting the following code in your terminal:
```
pytest -W ignore
```

## Simulation Examples

To run the simulations for Quantum Key Distribution (QKD), please copy-paste the following code in your terminal:
```
python -m src.qkd.BB84
```

To run the simulations for Quantum Teleportation (QT), please copy-paste the following code in your terminal:
```
python -m src.qt.QT
```

## Citation

Please cite us:

```

```

