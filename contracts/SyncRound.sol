// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Importing necessary contracts
import "./RandomNumbers.sol";
import "./Registration.sol";

/**
 * @title SyncRound
 * @dev This contract manages synchronous rounds of federated learning within the EkatraFL project.
 */
contract SyncRound {
    RandomNumbers randomNumbers; // Instance of RandomNumbers contract
    Registration registration; // Instance of Registration contract

    // Enumeration for different phases of the round
    enum RoundPhase {
        Idle,
        Training,
        Scoring
    }

    uint256 public round = 0; // Current round number
    RoundPhase public currentPhase; // Current phase of the round

    /**
     * @dev Constructor to initialize contract instances and set the initial phase to Idle.
     * @param _randomNumbers Address of the RandomNumbers contract.
     * @param _registration Address of the Registration contract.
     */
    constructor(address _randomNumbers, address _registration) {
        randomNumbers = RandomNumbers(_randomNumbers);
        registration = Registration(_registration);
        currentPhase = RoundPhase.Idle;
    }

    // Events declaration
    event StartTraining(uint256 round);
    event StartScoring(uint256 round, address[] scorers, string[] models);
    event ModelSubmitted(uint256 indexed round, address indexed trainer);
    event ScoreSubmitted(uint256 indexed round, address indexed scorer, string indexed model, uint256 score);

    /**
     * @dev Modifier to check if the sender is a valid scorer for the current round.
     * @param _round The round number.
     */
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

    /**
     * @dev Modifier to check if the sender is a valid trainer.
     */
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

    // Mapping declarations
    mapping(uint256 => mapping(address => mapping(string => uint256))) public roundToScorerToModelToScore;
    mapping(uint256 => address[]) public roundToScorers;
    mapping(uint256 => mapping(address => string)) public roundToTrainerToModel;
    mapping(uint256 => string[]) public roundToModels;
    mapping(string => uint256[]) internal modelToScores;

    /**
     * @dev Starts the training phase of the round.
     */
    function startTraining() public {
        require(currentPhase != RoundPhase.Training, "Already training");
        currentPhase = RoundPhase.Training;
        round++;
        emit StartTraining(round);
    }

    /**
     * @dev Submits a model by a trainer during the training phase.
     * @param _model The model name being submitted.
     */
    function submitModel(string memory _model) external validTrainer {
        require(currentPhase == RoundPhase.Training, "Only during training");
        roundToTrainerToModel[round][msg.sender] = _model;
        roundToModels[round].push(_model);
        emit ModelSubmitted(round, msg.sender);
    }

    /**
     * @dev Starts the scoring phase of the round.
     */
    function startScoring() public {
        require(currentPhase != RoundPhase.Scoring, "Already scoring");
        currentPhase = RoundPhase.Scoring;
        address[] memory scorers = randomNumbers.randomArray(registration.getScorers());
        roundToScorers[round] = scorers;
        emit StartScoring(round, scorers, roundToModels[round]);
    }

    /**
     * @dev Submits a score by a scorer during the scoring phase.
     * @param _round The round number.
     * @param _model The model name for which the score is being submitted.
     * @param _score The score being submitted.
     */
    function submitScore(uint256 _round, string memory _model, uint256 _score) external validScorer(_round) {
        require(currentPhase == RoundPhase.Scoring, "Only during scoring");
        roundToScorerToModelToScore[_round][msg.sender][_model] = _score;
        modelToScores[_model].push(_score);
        emit ScoreSubmitted(round, msg.sender, _model, _score);
    }

    /**
     * @dev Gets the models submitted during a specific round along with their scores.
     * @param _round The round number.
     * @return An array of model names and an array of corresponding scores for each model.
     */
    function getModelsWithScores(uint256 _round) public view returns (string[] memory, uint256[][] memory) {
        string[] memory _models = roundToModels[_round];
        uint256[][] memory _scores = new uint256[][](_models.length);
        for (uint256 i = 0; i < _models.length; i++) {
            _scores[i] = modelToScores[_models[i]];
        }
        return (_models, _scores);
    }

    /**
     * @dev Gets the latest models submitted along with their scores.
     * @return An array of model names and an array of corresponding scores for each model.
     */
    function getLatestModelsWithScores() external view returns (string[] memory, uint256[][] memory) {
        return getModelsWithScores(round - 1);
    }
}
