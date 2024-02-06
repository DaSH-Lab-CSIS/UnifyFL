// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Importing necessary contracts
import "./RandomNumbers.sol";
import "./Registration.sol";

/**
 * @title AsyncRound
 * @dev This contract manages asynchronous rounds of federated learning.
 */
contract AsyncRound {
    RandomNumbers randomNumbers; // Instance of RandomNumbers contract
    Registration registration; // Instance of Registration contract

    /**
     * @dev Constructor to initialize contract instances.
     * @param _randomNumbers Address of the RandomNumbers contract.
     * @param _registration Address of the Registration contract.
     */
    constructor(address _randomNumbers, address _registration) {
        randomNumbers = RandomNumbers(_randomNumbers);
        registration = Registration(_registration);
    }

    // Events declaration
    event ModelSubmitted(string model, address indexed trainer);
    event StartScoring(string model, address indexed trainer, address[] scorers);
    event ScoreSubmitted(string model, address indexed scorer, uint256 score);

    /**
     * @dev Modifier to check if the sender is a valid scorer for a given model.
     * @param _model The model name.
     */
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
        require(found, "Not a registered scorer");
        _;
    }

    // Mapping declarations
    mapping(address => string[]) public trainerToModels;
    mapping(string => address[]) internal modelToScorers;
    mapping(string => uint256[]) internal modelToScores;

    /**
     * @dev Submits a model by a trainer.
     * @param _model The model name.
     */
    function submitModel(string memory _model) public validTrainer {
        trainerToModels[msg.sender].push(_model);
        emit ModelSubmitted(_model, msg.sender);
        address[] memory scorers = randomNumbers.randomArray(registration.getScorers());
        modelToScorers[_model] = scorers;
        emit StartScoring(_model, msg.sender, scorers);
    }

    /**
     * @dev Submits a score by a scorer for a specific model.
     * @param _model The model name.
     * @param score The score submitted by the scorer.
     */
    function submitScore(string memory _model, uint256 score) public validScorer(_model) {
        modelToScores[_model].push(score);
        emit ScoreSubmitted(_model, msg.sender, score);
    }

    /**
     * @dev Gets the latest models submitted by trainers along with their scores.
     * @return An array of model names and an array of corresponding scores for each model.
     */
    function getLatestModelsWithScores() public view returns (string[] memory, uint256[][] memory) {
        address[] memory trainers = registration.getTrainers();
        uint256 trainersLength = trainers.length;
        string[] memory models = new string[](trainersLength);
        uint256[][] memory scores = new uint256[][](trainersLength);

        for (uint256 i = 0; i < trainers.length; i++) {
            if (trainerToModels[trainers[i]].length == 0) {
                continue;
            }
            models[i] = trainerToModels[trainers[i]][trainerToModels[trainers[i]].length - 1];
            scores[i] = modelToScores[models[i]];
        }

        return (models, scores);
    }
}
