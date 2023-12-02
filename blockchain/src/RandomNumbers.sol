// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RandomNumbers {
    function randomArray(
        address[] memory arr
    ) public view returns (address[] memory) {
        uint a = arr.length;
        uint len = (arr.length / 2) + 1;
        address[] memory result = new address[](len);
        bool[] memory used = new bool[](a);

        for (uint i = 0; i < len; i++) {
            uint randNumber = (uint(
                keccak256(abi.encodePacked(block.timestamp, arr[i]))
            ) % a);
            address interim = arr[randNumber];
            if (used[randNumber]) {
                uint j = 0;
                while (!used[randNumber]) {
                    randNumber = (uint(
                        keccak256(abi.encodePacked(block.timestamp, arr[i], j))
                    ) % a);
                    j += 1;
                }
                interim = arr[randNumber];
            }
            result[i] = interim;
            used[randNumber] = true;
        }

        return result;
    }
}
