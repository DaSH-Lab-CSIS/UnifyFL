// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./RandomNumbers.sol";
import "./Registration.sol";

contract SyncRound {
    RandomNumbers randomNumbers;
    Registration registration;

    constructor(address _randomNumbers, address _registration) {
        randomNumbers = RandomNumbers(_randomNumbers);
        registration = Registration(_registration);
    }

    enum RoundPhase {
        Idle,
        Training,
        Scoring
    }

    uint256 public round = 0;
    RoundPhase public currentPhase;

    event StartTraining(uint256 round);
    event StartScoring(uint256 round, address[] scorers, string[] models);

    event ModelSubmitted(uint256 indexed round, address indexed trainer);
    event ScoreSubmitted(
        uint256 indexed round,
        address indexed scorer,
        string indexed model,
        uint256 score
    );

    modifier validScorer(uint256 _round) {
        address[] memory scorers = roundToScorers[_round];
        bool found = false;
        for (uint i = 0; i < scorers.length; i++) {
            if (scorers[i] == msg.sender) {
                found = true;
                break;
            }
        }
        require(found, "Not an assigned scorer.");
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
        require(found, "Not a registered trainer.");
        _;
    }

    mapping(uint256 => mapping(address => mapping(string => uint256)))
        public roundToScorerToModelToScore;
    mapping(uint256 => address[]) public roundToScorers;
    mapping(uint256 => mapping(address => string)) public roundToTrainerToModel;
    mapping(uint256 => string[]) public roundToModels;
    mapping(string => uint256[]) internal modelToScores;

    function startTraining() public {
        require(currentPhase != RoundPhase.Training, "Already training");
        currentPhase = RoundPhase.Training;
        round++;
        emit StartTraining(round);
    }

    function submitModel(string memory _model) external validTrainer {
        require(currentPhase == RoundPhase.Training, "Only during training");
        roundToTrainerToModel[round][msg.sender] = _model;
        roundToModels[round].push(_model);
        emit ModelSubmitted(round, msg.sender);
    }

    function startScoring() public {
        require(currentPhase != RoundPhase.Scoring, "Already scoring");
        currentPhase = RoundPhase.Scoring;
        address[] memory scorers = randomNumbers.randomArray(
            registration.getScorers()
        );
        roundToScorers[round] = scorers;
        emit StartScoring(round, scorers, roundToModels[round]);
    }

    function submitScore(
        uint256 _round,
        string memory _model,
        uint256 _score
    ) external validScorer(_round) {
        require(currentPhase == RoundPhase.Scoring, "Only during scoring");
        roundToScorerToModelToScore[_round][msg.sender][_model] = _score;
        modelToScores[_model].push(_score);
        emit ScoreSubmitted(round, msg.sender, _model, _score);
    }

    function getModelsWithScores(
        uint256 _round
    ) public view returns (string[] memory, uint256[][] memory) {
        string[] memory _models = roundToModels[_round];
        uint256[][] memory _scores = new uint256[][](_models.length);
        for (uint256 i = 0; i < _models.length; i++) {
            _scores[i] = modelToScores[_models[i]];
        }
        return (_models, _scores);
    }

    function getLatestModelsWithScores()
        external
        view
        returns (string[] memory, uint256[][] memory)
    {
        return getModelsWithScores(round - 1);
    }
}
