// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./RandomNumbers.sol";
import "./Registration.sol";

contract AsyncRound {
    RandomNumbers randomNumbers;
    Registration registration;
    mapping(address => string[]) public trainerToModels;
    mapping(address => mapping(uint256 => uint256[]))
        public trainerToModelIndexToScores;
    mapping(address => mapping(uint256 => address[]))
        public trainerToModelIndexToScorers;

    event ModelSubmitted(string model, address indexed submitter);
    event ModelScorers(
        string model,
        address indexed submitter,
        address[] scorers
    );

    modifier validScorer() {
        address[] memory scorers = registration.getScorers();
        bool found = false;
        for (uint i = 0; i < scorers.length; i++) {
            if (scorers[i] == msg.sender) {
                found = true;
                break;
            }
        }
        require(found, "Not a registered scorer");
        _;
    }

    function selectedScorer(
        address trainer,
        uint256 modelIndex,
        address scorer
    ) internal view returns (bool) {
        address[] memory scorers = trainerToModelIndexToScorers[trainer][
            modelIndex
        ];
        bool found = false;
        for (uint i = 0; i < scorers.length; i++) {
            if (scorers[i] == scorer) {
                found = true;
                break;
            }
        }
        return found;
    }

    constructor(address _randomNumbers, address _registration) {
        randomNumbers = RandomNumbers(_randomNumbers);
        registration = Registration(_registration);
    }

    function submitModel(string memory _model) public {
        trainerToModels[msg.sender].push(_model);
        emit ModelSubmitted(_model, msg.sender);

        address[] memory scorers = randomNumbers.randomArray(
            registration.getScorers()
        );

        trainerToModelIndexToScorers[msg.sender][
            trainerToModels[msg.sender].length - 1 > 0
                ? trainerToModels[msg.sender].length - 1
                : 0
        ] = scorers;

        emit ModelScorers(_model, msg.sender, scorers);
    }

    function scoreModel(
        address trainer,
        string memory _model,
        uint256 score
    ) public validScorer {
        uint256 modelIndex = type(uint).max;
        for (uint256 i = 0; i < trainerToModels[trainer].length; i++) {
            if (
                keccak256(abi.encodePacked(trainerToModels[trainer][i])) ==
                keccak256(abi.encodePacked(_model))
            ) {
                modelIndex = i;
                break;
            }
        }
        require(modelIndex != type(uint).max, "Model not found");
        require(
            selectedScorer(trainer, modelIndex, msg.sender),
            "Scorer not selected"
        );
        trainerToModelIndexToScores[trainer][modelIndex].push(score);
    }

    function getLatestModels() public view returns (string[] memory) {
        string[] memory models = new string[](
            registration.getTrainers().length
        );

        address[] memory trainers = registration.getTrainers();

        for (uint256 i = 0; i < trainers.length; i++) {
            if (trainerToModels[trainers[i]].length == 0) {}
            models[i] = trainerToModels[trainers[i]][
                trainerToModels[trainers[i]].length - 1
            ];
        }

        return models;
    }

    function getModelScores(
        address trainer,
        uint256 index
    ) external view returns (uint256[] memory) {
        return trainerToModelIndexToScores[trainer][index];
    }

    function getLatestModelsWithScores()
        public
        view
        returns (string[] memory, uint256[][] memory)
    {
        address[] memory trainers = registration.getTrainers();
        uint256 trainersLength = trainers.length;
        string[] memory models = new string[](trainersLength);
        uint256[][] memory scores = new uint256[][](trainersLength);

        for (uint256 i = 0; i < trainers.length; i++) {
            if (trainerToModels[trainers[i]].length == 0) {
                continue;
            }
            uint modelIndex = trainerToModels[trainers[i]].length - 1;
            models[i] = trainerToModels[trainers[i]][modelIndex];
            scores[i] = trainerToModelIndexToScores[trainers[i]][modelIndex];
        }

        return (models, scores);
    }
}
