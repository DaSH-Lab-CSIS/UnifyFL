// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Registration
 * @dev This contract manages the registration of nodes as trainers or scorers within the EkatraFL project.
 */
contract Registration {
    mapping(address => string[]) public nodes; // Mapping of node addresses to their types
    address[] public trainers; // Array of addresses of registered trainers
    address[] public scorers; // Array of addresses of registered scorers

    /**
     * @dev Event emitted when a node is registered.
     * @param node The address of the registered node.
     * @param nodeType The type of the registered node (trainer or scorer).
     */
    event NodeRegistered(address indexed node, string nodeType);

    /**
     * @dev Registers a node as a trainer or scorer.
     * @param nodeType The type of the node being registered (trainer or scorer).
     */
    function registerNode(string memory nodeType) external {
        require(
            keccak256(bytes(nodeType)) == keccak256("trainer") ||
                keccak256(bytes(nodeType)) == keccak256("scorer"),
            "Invalid node type"
        );

        if (keccak256(bytes(nodeType)) == keccak256("trainer")) {
            trainers.push(msg.sender);
        } else if (keccak256(bytes(nodeType)) == keccak256("scorer")) {
            scorers.push(msg.sender);
        }

        nodes[msg.sender].push(nodeType);
        emit NodeRegistered(msg.sender, nodeType);
    }

    /**
     * @dev Retrieves the addresses of all registered trainers.
     * @return An array containing the addresses of all registered trainers.
     */
    function getTrainers() external view returns (address[] memory) {
        return trainers;
    }

    /**
     * @dev Retrieves the addresses of all registered scorers.
     * @return An array containing the addresses of all registered scorers.
     */
    function getScorers() external view returns (address[] memory) {
        return scorers;
    }
}
