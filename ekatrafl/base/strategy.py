# Copyright 2020 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Adaptive Federated Optimization using Yogi (FedYogi) [Reddi et al., 2020] strategy.

Paper: arxiv.org/abs/2003.00295
"""


from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from flwr.common import (
    FitRes,
    MetricsAggregationFn,
    NDArrays,
    Parameters,
    Scalar,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)
from flwr.server.client_proxy import ClientProxy


# pylint: disable=line-too-long
class FedYogiAggregate:
    """FedYogi [Reddi et al., 2020] strategy.

    Implementation based on https://arxiv.org/abs/2003.00295v5

    Parameters
    ----------
    initial_parameters : Parameters
        Initial global model parameters.
    eta : float, optional
        Server-side learning rate. Defaults to 1e-2.
    eta_l : float, optional
        Client-side learning rate. Defaults to 0.0316.
    beta_1 : float, optional
        Momentum parameter. Defaults to 0.9.
    beta_2 : float, optional
        Second moment parameter. Defaults to 0.99.
    tau : float, optional
        Controls the algorithm's degree of adaptability.
        Defaults to 1e-3.
    """

    # pylint: disable=too-many-arguments,too-many-instance-attributes,too-many-locals, line-too-long
    def __init__(
        self,
        *,
        initial_parameters: Parameters,
        eta: float = 1e-2,
        eta_l: float = 0.0316,
        beta_1: float = 0.9,
        beta_2: float = 0.99,
        tau: float = 1e-3,
    ) -> None:
        self.current_weights = parameters_to_ndarrays(initial_parameters)
        self.eta = eta
        self.eta_l = eta_l
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.tau = tau
        self.m_t: Optional[NDArrays] = None

    def aggregate(self, fedavg_weights_aggregate: NDArrays) -> NDArrays:
        """Aggregate fit results using weighted average."""

        # Yogi
        delta_t: NDArrays = [
            x - y for x, y in zip(fedavg_weights_aggregate, self.current_weights)
        ]

        # m_t
        if not self.m_t:
            self.m_t = [np.zeros_like(x) for x in delta_t]
        self.m_t = [
            np.multiply(self.beta_1, x) + (1 - self.beta_1) * y
            for x, y in zip(self.m_t, delta_t)
        ]

        # v_t
        if not self.v_t:
            self.v_t = [np.zeros_like(x) for x in delta_t]
        self.v_t = [
            x - (1.0 - self.beta_2) * np.multiply(y, y) * np.sign(x - np.multiply(y, y))
            for x, y in zip(self.v_t, delta_t)
        ]

        new_weights = [
            x + self.eta * y / (np.sqrt(z) + self.tau)
            for x, y, z in zip(self.current_weights, self.m_t, self.v_t)
        ]

        self.current_weights = new_weights

        return self.current_weights
