// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./RandomNumbers.sol";
import "./Registration.sol";

contract SyncRound {
    enum RoundPhase {
        Idle,
        Training,
        Scoring
    }

    uint256 public round = 0;
    RoundPhase public currentPhase;

    RandomNumbers randomNumbers;
    Registration registration;

    event StartTraining(uint256 round);
    event StartScoring(uint256 round, address[] scorers, string[] models);

    event ScoreSubmitted(
        uint256 round,
        address scorer,
        string model,
        uint256 score
    );

    event ModelSubmitted(uint256 indexed round, address indexed trainer);

    mapping(uint256 => mapping(address => mapping(string => uint256)))
        public roundScores; // round -> scorer -> model -> score
    mapping(uint256 => address[]) public roundToScorers; // round -> scorer nodes
    mapping(uint256 => mapping(address => string)) public models; // round => trainer => model
    mapping(uint256 => string[]) public roundToModels;
    mapping(string => uint256[]) public modelToScores;

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

    constructor(address _randomNumbers, address _registration) {
        randomNumbers = RandomNumbers(_randomNumbers);
        registration = Registration(_registration);
    }

    function startTraining() public {
        require(currentPhase != RoundPhase.Training, "Already training");
        currentPhase = RoundPhase.Training;
        round++;
        emit StartTraining(round);
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
    ) external validScorer {
        require(currentPhase == RoundPhase.Scoring, "Only during scoring");
        require(
            roundScores[_round][msg.sender][_model] != _score,
            "Score already submitted"
        );
        roundScores[_round][msg.sender][_model] = _score;
        modelToScores[_model].push(_score);
        emit ScoreSubmitted(round, msg.sender, _model, _score);
    }

    function submitModel(string memory _model) external {
        require(currentPhase == RoundPhase.Training, "Only during training");
        models[round][msg.sender] = _model;
        roundToModels[round].push(_model);
        emit ModelSubmitted(round, msg.sender);
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
