import numpy as np
from ensemble import greedy_vote, choose_ensemble_action

def test_greedy_picks_max_lane(sample_obs):
    # Lane index 1 has highest count (0.8)
    result = greedy_vote(sample_obs, n_actions=4)
    assert result == 1

def test_ensemble_no_models(sample_obs):
    action, meta = choose_ensemble_action(sample_obs, step=0, n_actions=4)
    assert 0 <= action < 4
    assert "votes" in meta

def test_ensemble_greedy_fallback(sample_obs):
    # With no RF/LSTM, should still return greedy vote
    action, meta = choose_ensemble_action(
        sample_obs, step=0, n_actions=4,
        rf_clf=None, rf_le=None, lstm_model=None, lstm_hist=[]
    )
    assert action == greedy_vote(sample_obs, n_actions=4)

def test_ensemble_majority_vote(sample_obs):
    # If all 3 voters agree, that action wins
    action, meta = choose_ensemble_action(sample_obs, step=0, n_actions=4)
    valid = [v for v in meta["votes"] if v is not None]
    assert action in valid
