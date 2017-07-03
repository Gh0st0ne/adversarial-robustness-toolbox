import numpy as np
import os
import random
import sys

from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.utils import np_utils

from sklearn.datasets import make_moons, make_circles

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from src.attackers.fast_gradient import FastGradientMethod
from src.attackers.virtual_adversarial import VirtualAdversarialMethod

# -------------------------------------------------------------------------------------------------------- TOY DATASETS

def get_toyset(name, nb_instances=20, noise=None, factor=0.6, rnd_state=None):

    if name == "moons":
        X, Y = make_moons(n_samples=nb_instances*10, noise=noise, random_state=rnd_state)

    elif name == "circles":
        X, Y = make_circles(n_samples=nb_instances*10, noise=noise, factor=factor, random_state=rnd_state)

    else:
        raise NotImplementedError("unknown dataset")

    indices = random.sample(range(nb_instances*10), nb_instances)
    X, Y = X[indices], Y[indices]

    y_cat = np_utils.to_categorical(Y, 2)

    return X, Y, y_cat

# ------------------------------------------------------------------------------------------------------ LEARNING UTILS

def simple_nn(nb_units=64):
    # as first layer in a sequential model:
    model = Sequential()
    model.add(Dense(nb_units, input_shape=(2,)))
    # model.add(Dropout(0.1))
    model.add(Dense(nb_units, activation="relu"))
    # model.add(Dropout(0.1))
    model.add(Dense(2, activation='softmax'))

    return model

def data_augmentation(x, y, type="gaussian", nb_instances=1, eps=0.3, **kwargs):

    if type == "uniform":
        x_aug = np.random.uniform(low=[-eps, -eps], high=[eps, eps], size=(nb_instances,) + x.shape)
        x_aug = np.tile(x, (nb_instances, 1)) + x_aug.reshape(-1, *x[0].shape)
        y_aug = np.tile(y, (nb_instances, 1))

    elif type == "gaussian":
        x_aug = np.random.normal(x, scale=eps, size=(nb_instances,) + x.shape)
        x_aug = x_aug.reshape(-1, *x[0].shape)
        y_aug = np.tile(y, (nb_instances, 1))

    elif type == "fgm":
        adv_crafter = FastGradientMethod(model=kwargs["model"], sess=kwargs["session"], ord=2)
        x_aug = adv_crafter.generate(x_val=x, eps=eps)
        y_aug = y.copy()

    elif type == "vat":
        adv_crafter = VirtualAdversarialMethod(model=kwargs["model"], sess=kwargs["session"])
        x_aug = adv_crafter.generate(x_val=x, eps=eps)
        y_aug = y.copy()

    return x_aug, y_aug