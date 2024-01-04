// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./RandomNumbers.sol";
import "./Registration.sol";

contract AsyncRound {
    RandomNumbers randomNumbers;
    Registration registration;

    constructor(address _randomNumbers, address _registration) {
        randomNumbers = RandomNumbers(_randomNumbers);
        registration = Registration(_registration);
    }

    event ModelSubmitted(string model, address indexed trainer);
    event StartScoring(
        string model,
        address indexed trainer,
        address[] scorers
    );
    event ScoreSubmitted(string model, address indexed scorer, uint256 score);

    modifier validScorer(string memory _model) {
        address[] memory scorers = modelToScorers[_model];
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

    modifier validTrainer() {
        address[] memory trainers = registration.getTrainers();
        bool found = false;
        for (uint i = 0; i < trainers.length; i++) {
            if (trainers[i] == msg.sender) {
                found = true;
                break;
            }
        }
        require(found, "Not a registered scorer");
        _;
    }

    mapping(address => string[]) public trainerToModels;
    mapping(string => address[]) internal modelToScorers;
    mapping(string => uint256[]) internal modelToScores;

    function submitModel(string memory _model) public validTrainer {
        trainerToModels[msg.sender].push(_model);
        emit ModelSubmitted(_model, msg.sender);
        address[] memory scorers = randomNumbers.randomArray(
            registration.getScorers()
        );
        modelToScorers[_model] = scorers;
        emit StartScoring(_model, msg.sender, scorers);
    }

    function submitScore(
        string memory _model,
        uint256 score
    ) public validScorer(_model) {
        modelToScores[_model].push(score);
        emit ScoreSubmitted(_model, msg.sender, score);
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
            models[i] = trainerToModels[trainers[i]][
                trainerToModels[trainers[i]].length - 1
            ];
            scores[i] = modelToScores[models[i]];
        }

        return (models, scores);
    }
}
