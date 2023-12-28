// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Registration {
    mapping(address => string[]) public nodes;
    address[] public trainers;
    address[] public scorers;

    event NodeRegistered(address indexed node, string nodeType);

    function registerNode(string memory nodeType) external {
        require(
            keccak256(bytes(nodeType)) == keccak256("trainer") ||
                keccak256(bytes(nodeType)) == keccak256("scorer"),
            "Invalid device type"
        );

        if (keccak256(bytes(nodeType)) == keccak256("trainer")) {
            trainers.push(msg.sender);
        } else if (keccak256(bytes(nodeType)) == keccak256("scorer")) {
            scorers.push(msg.sender);
        }

        nodes[msg.sender].push(nodeType);
        emit NodeRegistered(msg.sender, nodeType);
    }

    function getTrainers() external view returns (address[] memory) {
        return trainers;
    }

    function getScorers() external view returns (address[] memory) {
        return scorers;
    }
}
