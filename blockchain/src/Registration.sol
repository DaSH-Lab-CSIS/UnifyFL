// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Registration {
    mapping(address => string[]) public deviceType; // trainer, aggregator, scorer
    address[] public trainers;
    address[] public aggregators;
    address[] public scorers;

    event DeviceRegistered(address indexed device, string deviceType);

    function registerDevice(string memory _deviceType) external {
        require(
            keccak256(bytes(_deviceType)) == keccak256("trainer") ||
                keccak256(bytes(_deviceType)) == keccak256("aggregator") ||
                keccak256(bytes(_deviceType)) == keccak256("scorer"),
            "Invalid device type"
        );

        if (keccak256(bytes(_deviceType)) == keccak256("trainer")) {
            trainers.push(msg.sender);
        } else if (keccak256(bytes(_deviceType)) == keccak256("aggregator")) {
            aggregators.push(msg.sender);
        } else if (keccak256(bytes(_deviceType)) == keccak256("scorer")) {
            scorers.push(msg.sender);
        }

        deviceType[msg.sender].push(_deviceType);
        emit DeviceRegistered(msg.sender, _deviceType);
    }

    function getTrainers() external view returns (address[] memory) {
        return trainers;
    }

    function getAggregators() external view returns (address[] memory) {
        return aggregators;
    }

    function getScorers() external view returns (address[] memory) {
        return scorers;
    }
}
