from logging import INFO
import sys
from typing import Optional

import flwr as fl
from flwr.common.address import parse_address
from flwr.common.grpc import GRPC_MAX_MESSAGE_LENGTH
from flwr.common.telemetry import EventType, event
from flwr.common.logger import log
from flwr.common.typing import Parameters
from flwr.server import ServerConfig
from flwr.server.app import init_defaults
from flwr.server.fleet.grpc_bidi.grpc_server import start_grpc_server
from flwr.server.strategy import Strategy

# import wandb


# #Login to wandb
# wandb.login()


class Server(fl.server.Server):
    def __init__(
        self,
        server_address: str = "localhost:8080",
        config: Optional[ServerConfig] = None,
        strategy: Optional[Strategy] = None,
    ):
        event(EventType.START_SERVER_ENTER)

        # Parse IP address
        parsed_address = parse_address(server_address)
        if not parsed_address:
            sys.exit(f"Server IP address ({server_address}) cannot be parsed.")
        host, port, is_v6 = parsed_address
        address = f"[{host}]:{port}" if is_v6 else f"{host}:{port}"

        # Initialize server and server config
        initialized_server, initialized_config = init_defaults(
            server=None,
            config=config,
            strategy=strategy,
            client_manager=None,
        )
        self.server = initialized_server
        self.num_rounds = 0
        self.config = initialized_config
        log(
            INFO,
            "Starting Custom Flower server, config: %s",
            initialized_config,
        )

        # Start gRPC server

        self.grpc_server = start_grpc_server(
            client_manager=initialized_server.client_manager(),
            server_address=address,
            max_message_length=GRPC_MAX_MESSAGE_LENGTH,
            certificates=None,
        )
        log(
            INFO,
            "Flower ECE: gRPC server running (%s rounds), SSL is %s",
            initialized_config.num_rounds,
            "disabled",
        )

        # Initialize parameters
        log(INFO, "Initializing global parameters")
        self.server.parameters = self.server._get_initial_parameters(
            timeout=initialized_config.round_timeout
        )
        log(INFO, "Evaluating initial parameters")
        res = self.server.strategy.evaluate(0, parameters=self.server.parameters)
        if res is not None:
            log(
                INFO,
                "initial parameters (loss, other metrics): %s, %s",
                res[0],
                res[1],
            )
        # print("server param", type(self.server.parameters))

    def stop(self):
        # Stop the gRPC server
        self.server.disconnect_all_clients(timeout=self.config.round_timeout)
        self.grpc_server.stop(grace=1)

        event(EventType.START_SERVER_LEAVE)

    def start_round(self) -> Optional[Parameters]:
        res_fit = self.server.fit_round(self.num_rounds, self.config.round_timeout)
        if res_fit is not None:
            parameters_prime, _, _ = res_fit  # fit_metrics_aggregated
            print(type(parameters_prime))
            self.server.parameters = parameters_prime
            return parameters_prime
